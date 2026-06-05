const input = document.querySelector('#guessPlayer');
const list = document.querySelector('#autocomplete-list');

async function autocompleteList() {
    await loadPlayers(); /*list of all players*/


    input.addEventListener('input', () => {
        if (gameComplete) return;

        guessAlert.classList.add('hidden');
        
        if (!input.value){
            list.innerHTML = '';
            return;
        }


        /*filters playerlist into the first 5 players that start with the user input */
        const playerSuggestions = allPlayers.filter(player =>
            player.toLowerCase().startsWith(input.value.toLowerCase())
        ).slice(0, 5);

        suggestionsHTML(playerSuggestions)
    });

    /*Autocomplete dissapears if anything but input box or autocomplet list is clicked*/
    document.addEventListener('click', e => {
    if (!input.contains(e.target) && !list.contains(e.target)) {
        list.innerHTML = '';
    }
    });

};

function suggestionsHTML(playerList) {
    list.innerHTML = '';
    playerList.forEach(player => {
        const item = document.createElement('div');
        item.className = "autocomplete-item";
        item.textContent = player;

        /*if player suggestion is clicked, autocomplte list goes away, and input is filled with suggested player*/
        item.addEventListener('click', () => {
            input.value = player;
            list.innerHTML = '';
        });

        list.appendChild(item);
    });
}

autocompleteList();
