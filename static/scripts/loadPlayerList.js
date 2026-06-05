let allPlayers = [];

async function loadPlayers() {
    const res = await fetch("/api/players"); /*TODO add try and except*/
    allPlayers = await res.json();
}

