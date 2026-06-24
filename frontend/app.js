document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const points = document.querySelectorAll('.point');
    const statusDisplay = document.getElementById('status');
    const optionsForm = document.getElementById('game-options-form');
    const gameModeRadios = document.querySelectorAll('input[name="gameMode"]');
    const aiDifficultySelect = document.getElementById('ai-difficulty');

    // L'URL de votre API FastAPI (à adapter si besoin)
    const API_BASE_URL = 'http://localhost:8000/api';

    // Game State (Calqué sur get_game_state() du backend)
    let currentGame = {
        mode: 'hvh',
        difficulty: 'medium',
        isActive: false,
        selectedPosition: null, // Utilisé pour la Phase 2 (Mouvement)
        
        // État provenant du backend Python
        state: {
            p1_positions: [],
            p2_positions: [],
            current_player: 1,
            phase: 1,
            pieces_placed: 0,
            game_over: false,
            winner: null
        }
    };

    /**
     * Met à jour l'affichage en fonction de l'état renvoyé par le backend
     */
    function updateBoard(backendState) {
        currentGame.state = backendState;

        // 1. Nettoyer le plateau
        points.forEach(point => {
            point.innerHTML = ''; 
            point.classList.remove('selected');
        });

        // 2. Placer les pions du Joueur 1
        backendState.p1_positions.forEach(index => {
            const point = document.querySelector(`.point[data-index="${index}"]`);
            if (point) {
                const piece = document.createElement('div');
                piece.classList.add('piece', 'player1');
                point.appendChild(piece);
            }
        });

        // 3. Placer les pions du Joueur 2
        backendState.p2_positions.forEach(index => {
            const point = document.querySelector(`.point[data-index="${index}"]`);
            if (point) {
                const piece = document.createElement('div');
                piece.classList.add('piece', 'player2');
                point.appendChild(piece);
            }
        });

        // 4. Mettre à jour le texte de statut
        if (backendState.game_over) {
            statusDisplay.textContent = `Partie terminée ! Le Joueur ${backendState.winner} a gagné !`;
            currentGame.isActive = false;
        } else {
            const phaseText = backendState.phase === 1 ? "Phase 1 (Placement)" : "Phase 2 (Mouvement)";
            statusDisplay.textContent = `${phaseText} - Au tour du Joueur ${backendState.current_player}`;
        }
    }

    /**
     * Démarre une nouvelle partie
     */
    async function startNewGame(mode, difficulty) {
        currentGame.mode = mode;
        currentGame.difficulty = difficulty;
        currentGame.isActive = true;
        currentGame.selectedPosition = null;

        // Appel hypothétique à une route FastAPI pour réinitialiser le jeu
        try {
            // Remplacez cette simulation par un vrai fetch() vers votre route de reset
             const response = await fetch(`${API_BASE_URL}/reset`, { method: 'POST' });
             const initialState = await response.json();
            
            // Simulation de l'état initial (plateau vide) renvoyé par le backend
            /*const initialState = {
                p1_positions: [],
                p2_positions: [],
                current_player: 1,
                phase: 1,
                pieces_placed: 0,
                game_over: false,
                winner: null
            };*/
            
            updateBoard(initialState);
            console.log(`Nouvelle partie. Mode: ${mode}, Difficulté: ${difficulty}`);

        } catch (error) {
            console.error("Erreur lors de la connexion au backend:", error);
            statusDisplay.textContent = "Erreur de connexion au serveur.";
        }
    }

    /**
     * Envoie l'action (Placement ou Mouvement) au backend Python
     */
    async function sendActionToBackend(actionType, fromPos, toPos) {
        try {
            // Construction de l'URL avec les paramètres attendus par FastAPI
            let url = `${API_BASE_URL}/move?action_type=${actionType}`;
            if (fromPos !== null) url += `&from_pos=${fromPos}`;
            if (toPos !== null) url += `&to_pos=${toPos}`;

            // Décommentez ceci quand votre serveur Uvicorn tourne
            
            const response = await fetch(url, { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                updateBoard(data.state);
            } else {
                statusDisplay.textContent = "Coup invalide !";
            }
            
           
           console.log(`Action envoyée : ${actionType}, de ${fromPos} vers ${toPos}`);
           
        } catch (error) {
            console.error("Erreur de communication API :", error);
        }
    }

    // --- Gestionnaires d'événements ---

    optionsForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(optionsForm);
        startNewGame(formData.get('gameMode'), formData.get('difficulty'));
    });

    gameModeRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            aiDifficultySelect.disabled = radio.value !== 'hva';
        });
    });

    // Cœur de l'interaction utilisateur
    points.forEach(point => {
        point.addEventListener('click', () => {
            if (!currentGame.isActive || currentGame.state.game_over) return;

            const clickedIndex = parseInt(point.dataset.index);
            const { phase, current_player, p1_positions, p2_positions } = currentGame.state;

            // --- PHASE 1 : PLACEMENT ---
            if (phase === 1) {
                // On s'assure que la case est vide avant d'envoyer la requête
                if (!p1_positions.includes(clickedIndex) && !p2_positions.includes(clickedIndex)) {
                    sendActionToBackend('place', null, clickedIndex);
                }
            } 
            // --- PHASE 2 : MOUVEMENT ---
            else if (phase === 2) {
                const currentPlayerPositions = current_player === 1 ? p1_positions : p2_positions;
                const isOwnPiece = currentPlayerPositions.includes(clickedIndex);

                // 1er Clic : Sélectionner un de ses pions
                if (isOwnPiece) {
                    // Retirer la sélection précédente
                    points.forEach(p => p.classList.remove('selected'));
                    
                    // Ajouter la sélection visuelle sur le nouveau pion
                    point.classList.add('selected');
                    currentGame.selectedPosition = clickedIndex;
                } 
                // 2ème Clic : Choisir la destination (si un pion est déjà sélectionné)
                else if (currentGame.selectedPosition !== null) {
                    const isOpponentPiece = (current_player === 1 ? p2_positions : p1_positions).includes(clickedIndex);
                    
                    // Si la case de destination est vide
                    if (!isOpponentPiece && !isOwnPiece) {
                        sendActionToBackend('move', currentGame.selectedPosition, clickedIndex);
                        currentGame.selectedPosition = null; // Réinitialiser la sélection
                        points.forEach(p => p.classList.remove('selected'));
                    }
                }
            }
        });
    });

    statusDisplay.textContent = "Sélectionnez un mode et lancez la partie.";
});
