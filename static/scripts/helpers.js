function freezeGame(result) {
    gameComplete = 1; /*Global Game Status variable */
    saveState();

    /*disable interactivity*/
    input.disabled = true;
    input.style.backgroundColor = "#e0e0e0";

    toggleGuess();
    gameOverPopUp(result);
}



function toggleGuess() {
    guessSubmit.disabled = !guessSubmit.disabled;
    guessSubmit.disabled ? (guessSubmit.style.opacity = .6, guessSubmit.style.cursor = "not-allowed") : (guessSubmit.style.opacity = 1, guessSubmit.style.cursor = "allowed");
}



async function correct(){
    gameResult = 1;
    freezeGame(true)
    
    await saveStats();
    saveState();

    input.style.color = "green";
    hintBoxes.forEach(box => {
       box.classList.add('reveal');
    });

}




async function incorrect(){
    shakeAnimation(input)

    input.value = '';

    if (guessCounter == 6) { /*if maximum number of guess has been used*/
        gameResult = 0;
        freezeGame(false);
        await saveStats();
        return;
    }

    /*updates visual guess counter*/
    guessCounter += 1;
    saveState();
    document.querySelector("#guess-counter").textContent = `${guessCounter}/6`;


    updateHintMessages();
}



function gameOverPopUp(win) {
    const gameOverModal = new bootstrap.Modal('#gameOverModal');

    /*# of guesses used*/
    if (win) {
        document.querySelector('#gameOverMessage').textContent = "Congratulations!";
        document.querySelector('#guesses').textContent = `${guessCounter} / 6`;
        document.querySelector('#hintsUsed').textContent = hintsUsed;
    }

    /*# of hints used*/
    else {
        document.querySelector('#gameOverMessage').textContent = "Next Time!";
        document.querySelector('#stats-container').style.visibility = "hidden";
    }

    gameOverModal.show();
}


function shakeAnimation(target) /*for invalid inputs/interactions*/
{
    target.classList.add('shake');

    target.addEventListener("animationend", () => {
       target.classList.remove('shake');
    });
}

function saveState(){
    const state = {
        guessCounter,
        hintsUsed,
        revealedHints,
        gameComplete,
        gameResult,
    }

    localStorage.setItem(`statlineGame_${gameDay}`, JSON.stringify(state));
}

function loadState(day){
    const saved = localStorage.getItem(`statlineGame_${day}`);

    if (!saved) return;

    const state = JSON.parse(saved);

    guessCounter = state.guessCounter;
    hintsUsed = state.hintsUsed;
    gameComplete = state.gameComplete;
    revealedHints = state.revealedHints;
    gameResult = state.gameResult;
}

function restoreUI(){

    document.querySelector("#guess-counter").textContent = /*error on console for this line */
        `${guessCounter}/6`;

    if (gameComplete){
        freezeGame(gameResult);
    }

    hintBoxes.forEach(box => {
        const revealCount = Number(box.dataset.revealcount); /*Corresponds to hint boxes html data attribute, the boxes have incrementing values*/

        if (revealedHints.includes(revealCount))
        {
            box.classList.add('reveal');
        }
    });

    updateHintMessages();
    

}

function updateHintMessages(){
    revealTexts.forEach((text) => {
        const revealCount = Number(text.parentElement.parentElement.dataset.revealcount); /*grandparent of text div stores the reveal count data in each hint box */
        let revealMessage = '';
        let guessesLeft = (revealCount - guessCounter) + 1; /*guesses needed to reveal hint*/

        /*plural vs singular*/
        if (guessesLeft == 1){
            revealMessage = 'after 1 more guess';
        }
        else if (guessCounter <= revealCount){
            revealMessage = `after ${String((revealCount - guessCounter) + 1)} more guesses`;
        }

        text.textContent = `Click to reveal ${revealMessage}`;
    });
}

async function saveStats(){
    const stats = {
        guesses: guessCounter,
        hints: hintsUsed,
        game_won: gameResult,
        day: gameDay
    };

    const response = await fetch('/api/stats', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(stats)
    })

    const data= await response.json();
    console.log(data);
}
