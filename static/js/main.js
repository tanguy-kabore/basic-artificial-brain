document.addEventListener('DOMContentLoaded', function() {
    // S'assure que la fenêtre modale est cachée au démarrage
    const vModal = document.getElementById('visualization-modal');
    vModal.style.display = 'none';
    // Éléments DOM
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const exploreBtn = document.getElementById('explore-btn');
    const maxPages = document.getElementById('max-pages');
    const urlInput = document.getElementById('url-input');
    const addUrlBtn = document.getElementById('add-url-btn');
    const memoryQuery = document.getElementById('memory-query');
    const searchMemoryBtn = document.getElementById('search-memory-btn');
    const visualizeMemoryBtn = document.getElementById('visualize-memory-btn');
    const saveBrainBtn = document.getElementById('save-brain-btn');
    const memoryResults = document.getElementById('memory-results');
    const memoryItems = document.getElementById('memory-items');
    const closeMemoryBtn = document.getElementById('close-memory-btn');
    const visualizationModal = document.getElementById('visualization-modal');
    const closeModal = document.getElementById('close-modal-btn');
    const closeVisualizationBtn = document.getElementById('close-visualization-btn');
    const memoryVisualization = document.getElementById('memory-visualization');

    // État
    let messageHistory = {}; // Historique des messages

    // Mise à jour des statistiques
    function updateStats() {
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'active') {
                    // Mise à jour des valeurs
                    document.getElementById('experience-counter').textContent = 
                        data.stats.neural_network.experience_counter;
                    document.getElementById('curiosity-factor').textContent = 
                        data.stats.neural_network.curiosity_factor.toFixed(2);
                    document.getElementById('stm-size').textContent = 
                        data.stats.memory.stm_size;
                    document.getElementById('ltm-size').textContent = 
                        data.stats.memory.ltm_size;
                    document.getElementById('exploration-rate').textContent = 
                        data.stats.learning.exploration_rate.toFixed(2);
                    document.getElementById('concepts-count').textContent = 
                        data.stats.learning.concepts_count;
                }
            })
            .catch(error => {
                console.error('Erreur lors de la récupération du statut:', error);
                addSystemMessage('Erreur de connexion au cerveau.');
            });
    }

    // Ajout d'un message au chat
    function addMessage(text, type, messageId = null) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', type);
        
        // Pour les réponses du cerveau, on ajoute des boutons de feedback
        if (type === 'ai') {
            const textElement = document.createElement('div');
            textElement.textContent = text;
            messageElement.appendChild(textElement);
            
            const feedbackElement = document.createElement('div');
            feedbackElement.classList.add('message-feedback');
            
            const positiveBtn = document.createElement('button');
            positiveBtn.innerHTML = '👍';
            positiveBtn.classList.add('btn', 'feedback-btn', 'positive');
            positiveBtn.title = 'Cette réponse est bonne';
            
            const negativeBtn = document.createElement('button');
            negativeBtn.innerHTML = '👎';
            negativeBtn.classList.add('btn', 'feedback-btn', 'negative');
            negativeBtn.title = 'Cette réponse est mauvaise';
            
            // On stocke l'ID du message pour le feedback
            const messageUniqueId = messageId || Date.now().toString();
            positiveBtn.dataset.messageId = messageUniqueId;
            negativeBtn.dataset.messageId = messageUniqueId;
            messageElement.dataset.messageId = messageUniqueId;
            
            // Ajout des gestionnaires d'événements
            positiveBtn.addEventListener('click', function() {
                sendFeedback(messageUniqueId, true);
                positiveBtn.classList.add('active');
                negativeBtn.classList.remove('active');
            });
            
            negativeBtn.addEventListener('click', function() {
                sendFeedback(messageUniqueId, false);
                negativeBtn.classList.add('active');
                positiveBtn.classList.remove('active');
            });
            
            feedbackElement.appendChild(positiveBtn);
            feedbackElement.appendChild(negativeBtn);
            messageElement.appendChild(feedbackElement);
        } else {
            messageElement.textContent = text;
        }
        
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageElement;
    }

    // Message système
    function addSystemMessage(text) {
        addMessage(text, 'system');
    }

    // Envoi d'un feedback pour une réponse du cerveau
    function sendFeedback(messageId, isPositive) {
        console.log(`Envoi de feedback pour le message ${messageId}: ${isPositive ? 'positif' : 'négatif'}`);
        
        // Récupère les données du message
        if (!messageHistory[messageId]) {
            console.error("Impossible de trouver les détails du message pour envoyer le feedback");
            return;
        }
        
        const messageData = messageHistory[messageId];
        
        // Prépare les données
        const data = {
            message_id: messageId,
            input: messageData.input,
            output: messageData.output,
            is_positive: isPositive
        };
        
        // Envoie la requête
        fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Feedback envoyé avec succès');
            } else {
                console.error('Erreur lors de l\'envoi du feedback:', data.message);
                addSystemMessage(`Erreur: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Erreur lors de l\'envoi du feedback:', error);
            addSystemMessage('Erreur de connexion au cerveau.');
        });
    }
    
    // Envoi d'un message au cerveau
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Affiche le message de l'utilisateur
        addMessage(message, 'user');
        
        // Prépare les données
        const data = {
            message: message
        };
        
        // Réinitialise l'entrée
        userInput.value = '';
        
        // Envoie la requête
        fetch('/api/interact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Générer un ID unique pour le message
                const messageId = Date.now().toString();
                
                // Stocker les détails du message pour le feedback futur
                messageHistory[messageId] = {
                    input: data.input,
                    output: data.response,
                    timestamp: data.timestamp
                };
                
                // Ajouter le message avec les boutons de feedback
                addMessage(data.response, 'ai', messageId);
                
                // Met à jour les statistiques
                updateStats();
            } else {
                addSystemMessage(`Erreur: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Erreur lors de l\'interaction:', error);
            addSystemMessage('Erreur de communication avec le cerveau.');
        });
    }

    // Exploration web
    function exploreWeb() {
        const pages = parseInt(maxPages.value) || 3;
        
        addSystemMessage('Exploration web en cours...');
        
        fetch('/api/explore_web', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ max_pages: pages })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                addSystemMessage(`Exploration terminée ! ${data.pages_explored} pages explorées.`);
                updateStats();
            } else {
                addSystemMessage('Erreur: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erreur lors de l\'exploration:', error);
            addSystemMessage('Erreur de communication avec l\'explorateur web.');
        });
    }

    // Ajout d'URL
    function addUrl() {
        const url = urlInput.value.trim();
        if (!url) return;
        
        fetch('/api/add_url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        })
        .then(response => response.json())
        .then(data => {
            addSystemMessage(data.message);
            if (data.status === 'success') {
                urlInput.value = '';
            }
        })
        .catch(error => {
            console.error('Erreur lors de l\'ajout d\'URL:', error);
            addSystemMessage('Erreur de communication avec l\'explorateur web.');
        });
    }

    // Recherche en mémoire
    function searchMemory() {
        const query = memoryQuery.value.trim();
        if (!query) return;
        
        fetch('/api/retrieve_memory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query, top_k: 5 })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Affiche les résultats
                memoryItems.innerHTML = '';
                
                if (data.memories.length === 0) {
                    memoryItems.innerHTML = '<p>Aucun souvenir trouvé.</p>';
                } else {
                    data.memories.forEach(memory => {
                        const item = document.createElement('div');
                        item.classList.add('memory-item');
                        
                        let content = memory.content;
                        try {
                            // Si le contenu est au format JSON, le parse
                            const parsed = JSON.parse(content);
                            content = '<pre>' + JSON.stringify(parsed, null, 2) + '</pre>';
                        } catch (e) {
                            // Sinon, utilise le contenu brut
                        }
                        
                        item.innerHTML = `
                            <div class="memory-content">${content}</div>
                            <div class="memory-metadata">
                                <p>Importance: ${memory.importance.toFixed(2)}</p>
                                <p>Créé le: ${new Date(memory.created_at).toLocaleString()}</p>
                            </div>
                        `;
                        
                        memoryItems.appendChild(item);
                    });
                }
                
                // Affiche le panneau de résultats
                memoryResults.classList.remove('hidden');
            } else {
                addSystemMessage('Erreur: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erreur lors de la recherche en mémoire:', error);
            addSystemMessage('Erreur de communication avec le système de mémoire.');
        });
    }

    // Visualisation de la mémoire
    function visualizeMemory() {
        fetch('/api/visualize_memory')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Affiche l'image
                    memoryVisualization.src = data.visualization_url;
                    // Montre explicitement la modal
                    visualizationModal.style.display = 'flex';
                    console.log('Modal affichée');
                } else {
                    addSystemMessage('Erreur: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Erreur lors de la visualisation de la mémoire:', error);
                addSystemMessage('Erreur de communication avec le système de mémoire.');
            });
    }

    // Sauvegarde du cerveau
    function saveBrain() {
        fetch('/api/save_brain', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                addSystemMessage(data.message);
            })
            .catch(error => {
                console.error('Erreur lors de la sauvegarde:', error);
                addSystemMessage('Erreur de communication avec le cerveau.');
            });
    }

    // Événements
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Les gestionnaires d'événements pour les boutons de feedback ont été supprimés
    // car les boutons sont maintenant générés dynamiquement pour chaque message
    
    exploreBtn.addEventListener('click', exploreWeb);
    addUrlBtn.addEventListener('click', addUrl);
    searchMemoryBtn.addEventListener('click', searchMemory);
    visualizeMemoryBtn.addEventListener('click', visualizeMemory);
    saveBrainBtn.addEventListener('click', saveBrain);
    
    closeMemoryBtn.addEventListener('click', function() {
        memoryResults.classList.add('hidden');
    });
    
    // Fonction pour fermer la fenêtre modale
    function closeModalFunction() {
        console.log('Fermeture de la fenêtre modale');
        visualizationModal.style.display = 'none';
    }

    // Bouton de fermeture de la fenêtre modale (X)
    if (closeModal) {
        closeModal.addEventListener('click', closeModalFunction);
    } else {
        console.error('Le bouton de fermeture X n\'a pas été trouvé');
    }
    
    // Bouton Fermer standard
    if (closeVisualizationBtn) {
        closeVisualizationBtn.addEventListener('click', closeModalFunction);
    } else {
        console.error('Le bouton Fermer n\'a pas été trouvé');
    }
    
    // Fermer la fenêtre modale en cliquant en dehors du contenu
    visualizationModal.addEventListener('click', function(event) {
        if (event.target === visualizationModal) {
            closeModalFunction();
        }
    });
    
    // Fermer la fenêtre modale avec la touche Echap
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && visualizationModal.style.display !== 'none') {
            closeModalFunction();
        }
    });
    
    // Mise à jour initiale des statistiques
    updateStats();
    
    // Mise à jour périodique des statistiques (toutes les 10 secondes)
    setInterval(updateStats, 10000);
});
