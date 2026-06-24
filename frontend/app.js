document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const points = document.querySelectorAll('.point');
    const statusDisplay = document.getElementById('status');
    const optionsForm = document.getElementById('game-options-form');
    const gameModeRadios = document.querySelectorAll('input[name="gameMode"]');
    const aiDifficultySelect = document.getElementById('ai-difficulty');

    // Game State
    let currentGame = {
        mode: 'hvh',
        difficulty: 'medium',
        boardState: [
            0, 0, 0,
            0, 0, 0,
            0, 0, 0
        ],
        currentPlayer: 1,
        isActive: false
    };

    /**
     * Updates the visual representation of the board.
     * @param {number[]} boardState - An array of 9 numbers (0, 1, or 2).
     */
    function updateBoard(boardState) {
        if (boardState.length !== 9) {
            console.error("Invalid board state:", boardState);
            return;
        }
        currentGame.boardState = boardState;
        points.forEach((point, index) => {
            point.innerHTML = ''; // Clear existing piece
            const pieceType = boardState[index];
            if (pieceType === 1 || pieceType === 2) {
                const piece = document.createElement('div');
                piece.classList.add('piece', pieceType === 1 ? 'player1' : 'player2');
                point.appendChild(piece);
            }
        });
    }

    /**
     * Starts a new game with the specified options.
     * @param {string} mode 
     * @param {string} difficulty 
     */
    function startNewGame(mode, difficulty) {
        currentGame.mode = mode;
        currentGame.difficulty = difficulty;
        currentGame.isActive = true;
        currentGame.currentPlayer = 1;

        // This is the initial board setup for Fanorona Telo
        const initialBoard = [
            1, 1, 1,
            1, 0, 2,
            2, 2, 2
        ];
        updateBoard(initialBoard);

        statusDisplay.textContent = `Game started: ${getModeText(mode, difficulty)}. Player 1's Turn.`;
        console.log(`Starting new game. Mode: ${mode}, Difficulty: ${difficulty}`);

        // TODO: Add logic to handle AI's first move if applicable (e.g., AI vs AI)
    }

    function getModeText(mode, difficulty) {
        switch (mode) {
            case 'hvh': return 'Human vs Human';
            case 'hva': return `Human vs AI (${difficulty})`;
            case 'ava': return `AI vs AI (${difficulty})`;
            default: return 'Unknown Mode';
        }
    }

    // --- Event Listeners ---

    // Handle form submission to start a new game
    optionsForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(optionsForm);
        const mode = formData.get('gameMode');
        const difficulty = formData.get('difficulty');
        startNewGame(mode, difficulty);
    });

    // Enable/disable AI difficulty dropdown based on game mode
    gameModeRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            aiDifficultySelect.disabled = radio.value !== 'hva';
        });
    });

    // Handle player clicks on the board
    points.forEach(point => {
        point.addEventListener('click', () => {
            if (!currentGame.isActive) {
                statusDisplay.textContent = "Start a new game first!";
                return;
            }
            const index = point.dataset.index;
            console.log(`Player clicked on point index: ${index}`);
            
            // TODO: Implement move logic and send to backend/AI.
            statusDisplay.textContent = `You clicked on point ${index}`;
        });
    });

    // --- Backend Communication (Placeholder) ---
    function connectToBackend() {
        // WebSocket connection logic would go here.
        // For now, the game is fully client-side.
        console.log("Backend connection is not live. Running in client-side mode.");
    }

    // Initial setup
    statusDisplay.textContent = "Select a game mode and start a new game.";
    connectToBackend();
});