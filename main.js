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
