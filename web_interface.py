from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
import time
from datetime import datetime

app = Flask(__name__)

# Référence globale au cerveau artificiel
brain = None

@app.route('/')
def index():
    """Page d'accueil de l'interface"""
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Sert les fichiers statiques"""
    return send_from_directory('static', path)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Retourne le statut actuel du cerveau artificiel"""
    if not brain:
        return jsonify({
            'status': 'error',
            'message': 'Le cerveau n\'est pas initialisé'
        }), 500
    
    # Récupération des statistiques
    stats = {
        'neural_network': {
            'experience_counter': brain.neural_core.experience_counter,
            'learning_rate': brain.neural_core.learning_rate,
            'curiosity_factor': brain.neural_core.curiosity_factor
        },
        'memory': {
            'stm_size': len(brain.memory_system.stm_buffer),
            'ltm_size': len(brain.memory_system.ltm_network),
            'total_memories': brain.memory_system.memory_counter
        },
        'learning': {
            'exploration_rate': brain.learning_system.exploration_rate,
            'total_experiences': brain.learning_system.total_experiences,
            'concepts_count': len(brain.learning_system.concepts)
        }
    }
    
    if hasattr(brain, 'web_explorer'):
        stats['web_explorer'] = brain.web_explorer.get_exploration_stats()
    
    return jsonify({
        'status': 'active',
        'timestamp': datetime.now().isoformat(),
        'stats': stats
    })

@app.route('/api/interact', methods=['POST'])
def interact():
    """Point d'entrée pour interagir avec le cerveau artificiel"""
    try:
        if not brain:
            return jsonify({
                'status': 'error',
                'message': 'Le cerveau n\'est pas initialisé'
            }), 500
        
        # Récupération des données de la requête
        try:
            data = request.get_json()
            if not data or 'message' not in data:
                return jsonify({
                    'status': 'error',
                    'message': 'Message obligatoire'
                }), 400
        except Exception as e:
            print(f"Erreur lors de l'analyse des données de la requête: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Format de données invalide'
            }), 400
        
        message = data['message']
        is_positive = data.get('is_positive', True)  # Par défaut, considère un message positif
        
        # Interaction avec le cerveau
        try:
            start_time = time.time()
            response = brain.process_message(message, is_positive)
            processing_time = time.time() - start_time
            
            return jsonify({
                'status': 'success',
                'input': message,
                'response': response,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Erreur lors de l'interaction avec le cerveau: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Erreur: {str(e)}"
            }), 500
    except Exception as e:
        print(f"Erreur générale dans interact: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Une erreur inattendue s\'est produite'
        }), 500

@app.route('/api/feedback', methods=['POST'])
def feedback():
    """Point d'entrée pour envoyer un feedback sur une réponse précédente"""
    try:
        if not brain:
            return jsonify({
                'status': 'error',
                'message': 'Le cerveau n\'est pas initialisé'
            }), 500
        
        # Récupération des données de la requête
        try:
            data = request.get_json()
            if not data or 'input' not in data or 'output' not in data or 'is_positive' not in data:
                return jsonify({
                    'status': 'error',
                    'message': 'Données de feedback incomplètes'
                }), 400
        except Exception as e:
            print(f"Erreur lors de l'analyse des données de feedback: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Format de données invalide'
            }), 400
        
        input_msg = data['input']
        output_msg = data['output']
        is_positive = data['is_positive']
        
        # Mise à jour de l'historique des interactions
        try:
            # Trouver l'interaction correspondante dans l'historique
            for interaction in reversed(brain.interaction_history):
                if interaction['input'] == input_msg and interaction['output'] == output_msg:
                    # Mettre à jour le feedback
                    interaction['is_positive'] = is_positive
                    break
            
            # Sauvegarder l'historique mis à jour
            with open('data/interaction_history.json', 'w') as f:
                json.dump(brain.interaction_history[-100:], f, indent=2)  # Seulement les 100 dernières
            
            return jsonify({
                'status': 'success',
                'message': 'Feedback enregistré avec succès'
            })
        except Exception as e:
            print(f"Erreur lors de l'enregistrement du feedback: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Erreur: {str(e)}"
            }), 500
    except Exception as e:
        print(f"Erreur générale dans feedback: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Une erreur inattendue s\'est produite'
        }), 500

@app.route('/api/explore_web', methods=['POST'])
def explore_web():
    """Déclenche une exploration web du cerveau artificiel"""
    if not brain or not hasattr(brain, 'web_explorer'):
        return jsonify({
            'status': 'error',
            'message': 'Explorateur web non disponible'
        }), 500
    
    # Récupération des paramètres
    data = request.get_json() or {}
    max_pages = data.get('max_pages', None)
    
    # Déclenche l'exploration
    pages_explored = brain.web_explorer.explore_web(max_pages)
    
    return jsonify({
        'status': 'success',
        'pages_explored': pages_explored,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/add_url', methods=['POST'])
def add_url():
    """Ajoute une URL à la liste d'exploration du cerveau"""
    if not brain or not hasattr(brain, 'web_explorer'):
        return jsonify({
            'status': 'error',
            'message': 'Explorateur web non disponible'
        }), 500
    
    # Récupération de l'URL
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({
            'status': 'error',
            'message': 'URL obligatoire'
        }), 400
    
    # Ajoute l'URL
    success = brain.web_explorer.add_url_to_explore(data['url'])
    
    return jsonify({
        'status': 'success' if success else 'error',
        'message': 'URL ajoutée' if success else 'URL invalide ou déjà présente',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/save_brain', methods=['POST'])
def save_brain():
    """Sauvegarde l'état du cerveau artificiel"""
    if not brain:
        return jsonify({
            'status': 'error',
            'message': 'Le cerveau n\'est pas initialisé'
        }), 500
    
    # Sauvegarde les différents composants
    brain.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Cerveau sauvegardé',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/retrieve_memory', methods=['POST'])
def retrieve_memory():
    """Récupère des souvenirs en fonction d'une requête"""
    if not brain:
        return jsonify({
            'status': 'error',
            'message': 'Le cerveau n\'est pas initialisé'
        }), 500
    
    # Récupération de la requête
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Requête obligatoire'
        }), 400
    
    query = data['query']
    top_k = data.get('top_k', 3)
    
    # Recherche des souvenirs
    memories = brain.memory_system.retrieve_memory(query, top_k)
    
    # Conversion pour le JSON
    memory_list = []
    for memory in memories:
        memory_copy = dict(memory)
        # Supprime les champs non sérialisables
        if 'encoding' in memory_copy:
            memory_copy['encoding'] = memory_copy['encoding'].tolist()
        memory_list.append(memory_copy)
    
    return jsonify({
        'status': 'success',
        'query': query,
        'memories': memory_list,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/visualize_memory', methods=['GET'])
def visualize_memory():
    """Génère et renvoie une visualisation du réseau de mémoire"""
    if not brain:
        return jsonify({
            'status': 'error',
            'message': 'Le cerveau n\'est pas initialisé'
        }), 500
    
    # Génère la visualisation
    filename = f'memory_network_{int(time.time())}.png'
    filepath = os.path.join('static', 'visualizations', filename)
    
    # Assure que le répertoire existe
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    brain.memory_system.visualize_memory_network(filepath)
    
    return jsonify({
        'status': 'success',
        'visualization_url': f'/static/visualizations/{filename}',
        'timestamp': datetime.now().isoformat()
    })

def start_interface(brain_instance, host='127.0.0.1', port=5000, debug=False):
    """Démarre l'interface web"""
    global brain
    brain = brain_instance
    
    # Crée les répertoires nécessaires
    os.makedirs('static/visualizations', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Démarre le serveur
    app.run(host=host, port=port, debug=debug)
