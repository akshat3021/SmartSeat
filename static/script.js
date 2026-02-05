

function findSeat() {
    const roll = document.getElementById('rollInput').value;
    
    if(!roll) {
        alert("Please enter a roll number!");
        return;
    }

    // Hide Search, Show Result
    document.getElementById('searchBox').style.display = 'none';
    document.getElementById('resultCard').style.display = 'block';

    // DRAW THE GRID
    const grid = document.getElementById('gridTarget');
    grid.innerHTML = ''; // Clear old results

    // Create 25 dummy seats (5x5)
    for(let i=1; i<=25; i++) {
        const seatDiv = document.createElement('div');
        seatDiv.className = 'seat';
        seatDiv.innerHTML = '🪑';
        
        // Simulating: "If roll number is 101, their seat is #13"
        if(i === 13) {
            seatDiv.className = 'seat my-seat'; // The Green Chair class
            seatDiv.innerHTML = '👋';
        }

        grid.appendChild(seatDiv);
    }
}

function closeResult() {
    document.getElementById('searchBox').style.display = 'block';
    document.getElementById('resultCard').style.display = 'none';
    document.getElementById('rollInput').value = '';
}