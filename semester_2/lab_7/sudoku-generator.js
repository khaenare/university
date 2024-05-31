function generateSudoku(difficulty) {
    const base = createFullBoard();
    const puzzle = removeNumbers(base, difficulty);
    return { puzzle, solved: base };
}

function createFullBoard() {
    let board = Array.from({ length: 9 }, () => Array(9).fill(0));
    solveSudoku(board);
    return board;
}

function removeNumbers(board, difficulty) {
    const level = { easy: 36, medium: 46, hard: 56 }[difficulty];
    let puzzle = board.map(row => [...row]);

    let attempts = level;
    while (attempts > 0) {
        const row = Math.floor(Math.random() * 9);
        const col = Math.floor(Math.random() * 9);

        if (puzzle[row][col] !== 0) {
            puzzle[row][col] = 0;
            attempts--;
        }
    }
    return puzzle;
}

function solveSudoku(board) {
    const emptyPos = findEmptyPosition(board);
    if (!emptyPos) return true;

    const [row, col] = emptyPos;

    for (let num = 1; num <= 9; num++) {
        if (isValid(board, num, row, col)) {
            board[row][col] = num;

            if (solveSudoku(board)) return true;

            board[row][col] = 0;
        }
    }
    return false;
}

function findEmptyPosition(board) {
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            if (board[i][j] === 0) return [i, j];
        }
    }
    return null;
}

function isValid(board, num, row, col) {
    for (let i = 0; i < 9; i++) {
        if (board[i][col] === num || board[row][i] === num) return false;
    }

    const startRow = Math.floor(row / 3) * 3;
    const startCol = Math.floor(col / 3) * 3;

    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
            if (board[startRow + i][startCol + j] === num) return false;
        }
    }
    return true;
}
