document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('sudoku-grid');
    const newGameButton = document.getElementById('new-game');
    const difficultySelector = document.getElementById('difficulty');
    const timeDisplay = document.getElementById('time');
    const bestTimeDisplay = document.getElementById('best-time');
    const errorCountDisplay = document.getElementById('error-count');
    const numberPad = document.querySelector('.number-pad');
    const numberButtons = document.querySelectorAll('.number-button');

    let timer;
    let startTime;
    let selectedCell = null;
    let solution = [];
    let numberCount = Array(10).fill(0); 
    let errorCount = 0; 
    let maxErrors = 3;

    function startTimer() {
        startTime = new Date();
        timer = setInterval(updateTime, 1000);
    }

    function updateTime() {
        const now = new Date();
        const elapsed = new Date(now - startTime);
        const minutes = String(elapsed.getUTCMinutes()).padStart(2, '0');
        const seconds = String(elapsed.getUTCSeconds()).padStart(2, '0');
        timeDisplay.textContent = `${minutes}:${seconds}`;
    }

    function stopTimer() {
        clearInterval(timer);
    }

    function loadBestTime(difficulty) {
        const bestTime = localStorage.getItem(`best-time-${difficulty}`);
        bestTimeDisplay.textContent = bestTime ? bestTime : 'Н/Д';
    }

    function saveBestTime(difficulty, time) {
        const bestTime = localStorage.getItem(`best-time-${difficulty}`);
        if (!bestTime || time < bestTime) {
            localStorage.setItem(`best-time-${difficulty}`, time);
            loadBestTime(difficulty);
        }
    }

    function newGame() {
        stopTimer();
        grid.innerHTML = '';
        numberPad.classList.add('hidden'); 
        const difficulty = difficultySelector.value;
        const { puzzle, solved } = generateSudoku(difficulty);
        solution = solved;
        numberCount = Array(10).fill(0);
        errorCount = 0; 
        maxErrors = getMaxErrors(difficulty); 
        errorCountDisplay.textContent = `0 / ${maxErrors}`; 
        renderGrid(puzzle);
        numberPad.classList.remove('hidden'); 
        startTimer();
        loadBestTime(difficulty);
    }

    function getMaxErrors(difficulty) {
        switch (difficulty) {
            case 'easy':
                return 7;
            case 'medium':
                return 5;
            case 'hard':
                return 3;
            default:
                return 3;
        }
    }

    function renderGrid(puzzle) {
        puzzle.forEach((row, i) => {
            row.forEach((cell, j) => {
                const cellDiv = document.createElement('div');
                cellDiv.dataset.row = i;
                cellDiv.dataset.col = j;
                if (cell !== 0) {
                    cellDiv.textContent = cell;
                    cellDiv.classList.add('fixed');
                    numberCount[cell]++;
                } else {
                    cellDiv.contentEditable = true;
                    cellDiv.addEventListener('click', selectCell);
                }
                grid.appendChild(cellDiv);
            });
        });
        updateNumberButtons();
    }

    function updateNumberButtons() {
        numberButtons.forEach(button => {
            const number = button.dataset.number;
            button.classList.toggle('disabled', numberCount[number] >= 9);
        });
    }

    function selectCell(event) {
        if (selectedCell) {
            selectedCell.classList.remove('selected');
        }
        selectedCell = event.target;
        selectedCell.classList.add('selected');
        highlightCells(selectedCell.dataset.row, selectedCell.dataset.col);
    }

    function highlightCells(row, col) {
        Array.from(grid.children).forEach(cell => {
            cell.classList.remove('highlight');
            if (cell.dataset.row === row || cell.dataset.col === col) {
                cell.classList.add('highlight');
            }
        });
        if (selectedCell) {
            selectedCell.classList.add('highlight');
        }
    }

    function fillCell(number) {
        if (selectedCell && selectedCell.contentEditable === "true" && !selectedCell.classList.contains('fixed')) {
            const row = selectedCell.dataset.row;
            const col = selectedCell.dataset.col;
            const isCorrect = solution[row][col] === parseInt(number, 10);

            if (isCorrect) {
                selectedCell.textContent = number;
                numberCount[number]++;
                checkError(selectedCell, isCorrect);
                updateNumberButtons();
                checkCompletion();
            } else {
                selectedCell.textContent = number;
                checkError(selectedCell, isCorrect);
            }
        }
    }

    function checkError(cell, isCorrect) {
        const row = cell.dataset.row;
        const col = cell.dataset.col;
        const value = parseInt(cell.textContent, 10);

        let isError = false;
        Array.from(grid.children).forEach(otherCell => {
            if (
                (otherCell.dataset.row === row || otherCell.dataset.col === col ||
                    (Math.floor(otherCell.dataset.row / 3) === Math.floor(row / 3) &&
                        Math.floor(otherCell.dataset.col / 3) === Math.floor(col / 3))) &&
                parseInt(otherCell.textContent, 10) === value &&
                otherCell !== cell
            ) {
                isError = true;
            }
        });

        if (solution[row][col] !== value) {
            isError = true;
        }

        if (isError) {
            cell.classList.add('error');
            errorCount++;
            errorCountDisplay.textContent = `${errorCount} / ${maxErrors}`;
            if (errorCount >= maxErrors) {
                stopTimer();
                alert('Ви програли! Досягнуто максимальну кількість помилок, починаємо нову гру:(');
                setTimeout(newGame, 1000);
            }
        } else if (isCorrect) {
            cell.classList.remove('error');
        }
    }

    function checkCompletion() {
        let isComplete = true;
        Array.from(grid.children).forEach(cell => {
            if (cell.contentEditable === "true" && cell.textContent === "") {
                isComplete = false;
            }
        });

        if (isComplete) {
            stopTimer();
            alert('Вітаємо! Ви завершили головоломку.');
            saveBestTime(difficultySelector.value, timeDisplay.textContent);
        }
    }

    newGameButton.addEventListener('click', () => {
        newGame();
    });

    difficultySelector.addEventListener('change', () => {
        newGame();
    });

    numberButtons.forEach(button => {
        button.addEventListener('click', () => {
            const number = button.dataset.number;
            if (!button.classList.contains('disabled')) {
                fillCell(number);
            }
        });
    });
    
    newGame();
});
