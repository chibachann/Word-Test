document.getElementById("word-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const englishWords = document.getElementById("english-word").value;
    const wordsArray = englishWords.split(" ");

    for (const englishWord of wordsArray) {
        const response = await fetch("/add_word", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ english: englishWord }),
        });

        const messageElem = document.getElementById("message");
        const data = await response.json();
        messageElem.textContent = data.message;

        if (response.status === 201) {
            messageElem.style.color = "green";
        } else {
            messageElem.style.color = "red";
        }
    }
});

async function nextQuestion() {
    const response = await fetch("/get_question");
    const question = await response.json();

    document.getElementById("english-word").textContent = question.english;
    const optionsContainer = document.getElementById("options");
    optionsContainer.innerHTML = "";

    question.options.forEach((option) => {
        const button = document.createElement("button");
        button.textContent = option;
        button.onclick = () => checkAnswer(option, question.correct_option);
        optionsContainer.appendChild(button);
    });
}

function checkAnswer(selectedOption, correctOption) {
    const resultElem = document.getElementById("result");
    if (selectedOption === correctOption) {
        resultElem.textContent = "正解！";
        resultElem.style.color = "green";
    } else {
        resultElem.textContent = "不正解...";
        resultElem.style.color = "red";
    }
}

nextQuestion(); // 最初の問題を表示

