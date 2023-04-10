import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from googletrans import Translator
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///words.db'
app.secret_key = 'some_secret_key'
db = SQLAlchemy(app)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    english = db.Column(db.String(100), unique=True, nullable=False)
    japanese = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Word('{self.english}', '{self.japanese}')"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/words')
def words():
    return app.send_static_file('words.html')

@app.route('/get_words', methods=['GET'])
def get_words():
    words = Word.query.all()
    output = []
    for word in words:
        word_data = {'english': word.english, 'japanese': word.japanese}
        output.append(word_data)
    return jsonify({'words': output})

@app.route('/add_word', methods=['POST'])
def add_word():
    data = request.get_json()
    english_word = data.get('english')

    translator = Translator()
    translated = translator.translate(english_word, src='en', dest='ja')
    japanese_word = translated.text

    existing_word = Word.query.filter_by(english=english_word).first()
    if existing_word:
        return jsonify({'message': 'この英単語は既に登録されています。'}), 400

    new_word = Word(english=english_word, japanese=japanese_word)
    db.session.add(new_word)
    db.session.commit()
    return jsonify({'message': '新しい単語が追加されました。'}), 201

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('register.html')

@app.route('/profile')
@login_required
def profile():
    user = current_user
    return render_template('profile.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('profile'))
        else:
            return jsonify({'message': 'ユーザー名またはパスワードが間違っています。'}), 400
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# アプリケーションを起動
if __name__ == '__main__':
    if not os.path.exists('words.db'):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
