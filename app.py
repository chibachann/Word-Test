import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from googletrans import Translator

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///words.db'
db = SQLAlchemy(app)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    english = db.Column(db.String(100), unique=True, nullable=False)
    japanese = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Word('{self.english}', '{self.japanese}')"
    
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

@app.before_first_request
def create_tables():
    db.create_all()
# 英単語を追加するエンドポイントを定義します。
@app.route('/add_word', methods=['POST'])
def add_word():
    data = request.get_json()
    english_word = data.get('english')

    # Google翻訳を使用して英語単語を日本語に翻訳します。
    translator = Translator()
    translated = translator.translate(english_word, src='en', dest='ja')
    japanese_word = translated.text

    # 既に存在する単語をチェックします。
    existing_word = Word.query.filter_by(english=english_word).first()
    if existing_word:
        return jsonify({'message': 'この英単語は既に登録されています。'}), 400

    # 新しい単語をデータベースに追加し、コミットします。
    new_word = Word(english=english_word, japanese=japanese_word)
    db.session.add(new_word)
    db.session.commit()
    return jsonify({'message': '新しい単語が追加されました。'}), 201

# 英単語を削除するエンドポイントを定義します。
@app.route('/delete_word', methods=['POST'])
def delete_word():
    data = request.get_json()
    english_word = data.get('english')

    # データベースから単語を検索します。
    word = Word.query.filter_by(english=english_word).first()
    if not word:
        return jsonify({'message': '単語が見つかりません。'}), 404

    # 単語をデータベースから削除し、コミットします。
    db.session.delete(word)
    db.session.commit()
    return jsonify({'message': '単語が削除されました。'}), 200

# アプリケーションを起動
if __name__ == '__main__':
    if not os.path.exists('words.db'):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
