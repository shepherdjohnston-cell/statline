let guessCounter = 1;
let hintsUsed = 0;
let gameComplete = 0;
let revealedHints = [];
let gameResult = 0;
const guessSubmit = document.querySelector('#guess');
const hintBoxes = document.querySelectorAll('.info-box');
const guessAlert = document.querySelector('#guess_alert');
const alertClose = document.querySelector('#alert_close');
const revealTexts = document.querySelectorAll('.reveal-text');

async function gamestate(){

    /*Hints Interactivity*/
    hintBoxes.forEach((box) => {
        const revealCount = Number(box.dataset.revealcount) /*Corresponds to hint boxes html data attribute, the boxes have incrementing values*/
        box.addEventListener('click', () => {
            if (gameComplete) return; /*No interactivity if game is over*/

            else if (revealCount < guessCounter) { /*confirms if user is able to reveal hint based upon their number of guess*/
                box.classList.add('reveal');
                hintsUsed += 1; /*for displayed stats at end of game */
                revealedHints.push(revealCount);
                saveState();
            }
            else {
                shakeAnimation(box); /*if user isn't allowed to reveal said hint yet*/
            }
        });
    });





    guessSubmit.addEventListener('click', async () => {

        /*disallows Submission if game is already over*/
        if (gameComplete) return;


        const guess = input.value; /*stores player guess*/

        /*TODO, try for errors*/
        const result = await fetch('/validate_guess', { /*backend guess validation*/
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                guess: guess,
                day: gameDay })
        });


        const data = await result.json()
        console.log('Server Response:', data);

        if (data.valid === -1){ /*invalid guess */
            guessAlert.classList.remove('hidden'); /*Invalid guess popup*/
           
            
            toggleGuess();
            shakeAnimation(input);

            /*if user clicks input box, or if user clicks alert close button, ability to guess returns*/
            function onInputClick() {
                guessAlert.classList.add('hidden');
                toggleGuess();
                input.removeEventListener('click', onInputClick);
            }

            alertClose.addEventListener('click', () => {
                guessAlert.classList.add('hidden');
                toggleGuess();
                input.value = '';
                input.removeEventListener('click', onInputClick)
            }, { once: true });
            
            input.addEventListener('click', onInputClick);
        }
               
        else if (data.valid === 0){ /*correct guess*/
            correct();
        }

        else { /*valid but incorrect guess*/
            incorrect();
        }
    });
}

document.addEventListener("DOMContentLoaded", () =>{
    loadState(gameDay);
    restoreUI();
    gamestate();
});


