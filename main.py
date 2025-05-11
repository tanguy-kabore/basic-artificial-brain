import os
import json
import numpy as np
import torch
from datetime import datetime
import argparse

from neural_network import NeuralCore
from memory_system import MemorySystem
from learning_system import LearningSystem
from web_explorer import WebExplorer
from dataset_importer import DatasetImporter
import web_interface

class BabyBrain:
    """
    Classe principale qui rassemble tous les composants du cerveau artificiel
    et coordonne leur fonctionnement.
    """
    
    def __init__(self):
        """Initialise le cerveau artificiel avec tous ses composants"""
        print("Initialisation du cerveau artificiel...")
        
        # Création du dossier de données
        os.makedirs('data', exist_ok=True)
        
        # Dimension des entrées/sorties
        self.input_size = 100
        self.output_size = 100
        
        # Réseau neuronal de base
        print("Création du réseau neuronal...")
        self.neural_core = NeuralCore(
            input_size=self.input_size, 
            hidden_size=128, 
            output_size=self.output_size
        )
        
        # Système de mémoire
        print("Création du système de mémoire...")
        self.memory_system = MemorySystem(
            stm_capacity=50,
            encoding_size=self.input_size
        )
        
        # Système d'apprentissage
        print("Création du système d'apprentissage...")
        self.learning_system = LearningSystem(
            neural_core=self.neural_core,
            memory_system=self.memory_system
        )
        
        # Explorateur web
        print("Création de l'explorateur web...")
        self.web_explorer = WebExplorer(
            learning_system=self.learning_system
        )
        
        # Historique des interactions
        self.interaction_history = []
        
        # Vocabulaire pour l'encodage/décodage du texte
        self.vocabulary = {}
        self.reverse_vocabulary = {}
        self.next_word_id = 1  # 0 est réservé pour les mots inconnus
        
        print("Cerveau artificiel initialisé et prêt à apprendre !")
    
    def _update_vocabulary(self, text):
        """Met à jour le vocabulaire avec de nouveaux mots"""
        words = text.lower().split()
        for word in words:
            if word not in self.vocabulary:
                self.vocabulary[word] = self.next_word_id
                self.reverse_vocabulary[self.next_word_id] = word
                self.next_word_id += 1
    
    def _encode_text(self, text):
        """Encode un texte en vecteur pour le réseau neuronal"""
        # Mise à jour du vocabulaire
        self._update_vocabulary(text)
        
        # Encodage très simple du texte
        words = text.lower().split()
        encoding = np.zeros(self.input_size)
        
        for i, word in enumerate(words[:self.input_size]):
            word_id = self.vocabulary.get(word, 0)  # 0 pour les mots inconnus
            # Utilisation de positions dans le vecteur pour représenter les mots
            position = i % self.input_size
            encoding[position] = word_id / self.next_word_id  # Normalisation
            
        return encoding
    
    def _create_response(self, output_vector, query=None):
        """Crée une réponse textuelle à partir d'un vecteur de sortie"""
        # Au début, les réponses seront aléatoires et simples
        if self.neural_core.experience_counter < 10:
            responses = [
                "Je suis en train d'apprendre.",
                "C'est nouveau pour moi.",
                "Je découvre le monde.",
                "Continuez à interagir avec moi pour m'aider à apprendre.",
                "Chaque interaction me fait grandir."
            ]
            return np.random.choice(responses), False
        
        # Recherche des souvenirs similaires
        memories = self.memory_system.retrieve_memory(output_vector, top_k=5)
        
        # S'il y a des souvenirs pertinents avec des réponses, les utilise
        response_fragments = []
        
        for memory in memories:
            try:
                # Tente de parser le contenu du souvenir
                if isinstance(memory['content'], str) and memory['content'].startswith('{'):
                    memory_data = json.loads(memory['content'])
                    if 'input' in memory_data and isinstance(memory_data['input'], str):
                        response_fragments.append(memory_data['input'])
                elif isinstance(memory['content'], str) and len(memory['content']) > 20:
                    # Ajoute aussi les contenus textuels substantiels
                    response_fragments.append(memory['content'])
            except:
                pass
        
        # Si des fragments ont été extraits, crée une réponse basée sur eux
        if response_fragments:
            # Sélection aléatoire d'un fragment comme base
            base = np.random.choice(response_fragments)
            
            # Tentative de création d'une réponse cohérente
            words = []
            for fragment in response_fragments:
                fragment_words = fragment.split()
                # Ajoute quelques mots aléatoires de chaque fragment
                if fragment_words:
                    start = np.random.randint(0, max(1, len(fragment_words) - 3))
                    end = min(len(fragment_words), start + np.random.randint(1, 4))
                    words.extend(fragment_words[start:end])
            
            # Limite la longueur de la réponse
            if len(words) > 15:
                words = words[:15]
                
            # Si la réponse est vide ou trop courte, utilise la base
            if len(words) < 3:
                return base, False
                
            return ' '.join(words).capitalize() + '.', False
        
        # Si aucune réponse n'a pu être générée et qu'une requête a été fournie,
        # indique qu'une recherche sur internet est nécessaire
        if query:
            return "Je ne connais pas encore la réponse à cette question. Je vais chercher sur internet.", True
            
        # Réponse par défaut si aucune génération n'est possible
        return "Je continue à apprendre et à évoluer avec chaque interaction.", False
    
    def process_message(self, message, is_positive=True):
        """
        Traite un message entrant, apprend de celui-ci et génère une réponse
        - message: texte du message
        - is_positive: indique si le message doit être considéré comme positif
        """
        try:
            # Encode le message
            input_vector = self._encode_text(message)
            
            try:
                # Apprentissage
                output_vector, loss = self.learning_system.learn_from_interaction(
                    input_vector, message, is_positive)
            except Exception as e:
                print(f"Erreur lors de l'apprentissage: {str(e)}")
                # En cas d'erreur, utilise un vecteur aléatoire pour générer une réponse
                output_vector = np.random.randn(self.output_size)
                loss = 0
            
            # Génération de réponse
            try:
                response, needs_web_search = self._create_response(output_vector, query=message)
                
                # Si le cerveau ne connaît pas la réponse, recherche sur internet
                if needs_web_search and hasattr(self, 'web_explorer'):
                    print(f"Recherche sur internet pour: {message}")
                    
                    # Ajoute une URL spécifique à la recherche si le message semble être une question
                    if message.endswith('?') or message.lower().startswith('comment') or \
                       message.lower().startswith('qu') or message.lower().startswith('pourquoi'):
                        search_url = f"https://fr.wikipedia.org/wiki/Special:Search?search={message.replace(' ', '+')}"
                        self.web_explorer.add_url_to_explore(search_url)
                    
                    # Explorer quelques pages en passant la requête
                    pages_explored = self.web_explorer.explore_web(max_pages=2, query=message)
                    
                    if pages_explored > 0:
                        # Tente de générer une nouvelle réponse après exploration
                        post_search_response, _ = self._create_response(output_vector)
                        response = f"J'ai exploré {pages_explored} pages sur internet. Voici ce que j'ai trouvé : {post_search_response}"
                    else:
                        response += " Malheureusement, je n'ai pas pu trouver d'informations pertinentes."
            except Exception as e:
                print(f"Erreur lors de la génération de réponse: {str(e)}")
                response = "Je suis désolé, j'ai du mal à formuler une réponse. Je continue à apprendre."
            
            # Enregistrement de l'interaction
            self.interaction_history.append({
                'input': message,
                'output': response,
                'is_positive': is_positive,
                'timestamp': datetime.now().isoformat()
            })
            
            return response
        except Exception as e:
            print(f"Erreur générale dans process_message: {str(e)}")
            return "Désolé, une erreur s'est produite dans mon traitement. Je suis encore en apprentissage."
    
    def save(self):
        """Sauvegarde l'état complet du cerveau artificiel"""
        # Assure que le dossier existe
        os.makedirs('data', exist_ok=True)
        
        # Sauvegarde de chaque composant
        self.neural_core.save_brain('data/brain_state.pt')
        self.memory_system.save_memory_system('data/memory_system.pkl')
        self.learning_system.save_learning_state('data/learning_state.json')
        
        if hasattr(self, 'web_explorer'):
            self.web_explorer.save_explorer_state('data/explorer_state.json')
        
        # Sauvegarde du vocabulaire
        with open('data/vocabulary.json', 'w') as f:
            json.dump({
                'vocabulary': self.vocabulary,
                'next_word_id': self.next_word_id
            }, f, indent=2)
        
        # Sauvegarde de l'historique des interactions
        with open('data/interaction_history.json', 'w') as f:
            json.dump(self.interaction_history[-100:], f, indent=2)  # Seulement les 100 dernières
            
        print("Cerveau sauvegardé !")
    
    def load(self):
        """Charge l'état du cerveau artificiel depuis les fichiers sauvegardés"""
        success = True
        
        # Charge le réseau neuronal
        if os.path.exists('data/brain_state.pt'):
            success &= self.neural_core.load_brain('data/brain_state.pt')
        else:
            success = False
            
        # Charge le système de mémoire
        if os.path.exists('data/memory_system.pkl'):
            success &= self.memory_system.load_memory_system('data/memory_system.pkl')
        else:
            success = False
            
        # Charge le système d'apprentissage
        if os.path.exists('data/learning_state.json'):
            success &= self.learning_system.load_learning_state('data/learning_state.json')
        else:
            success = False
            
        # Charge l'explorateur web
        if hasattr(self, 'web_explorer') and os.path.exists('data/explorer_state.json'):
            success &= self.web_explorer.load_explorer_state('data/explorer_state.json')
            
        # Charge le vocabulaire
        if os.path.exists('data/vocabulary.json'):
            with open('data/vocabulary.json', 'r') as f:
                vocab_data = json.load(f)
                self.vocabulary = vocab_data['vocabulary']
                self.next_word_id = vocab_data['next_word_id']
                
                # Reconstitue le vocabulaire inverse
                self.reverse_vocabulary = {v: k for k, v in self.vocabulary.items()}
        else:
            success = False
            
        # Charge l'historique des interactions
        if os.path.exists('data/interaction_history.json'):
            with open('data/interaction_history.json', 'r') as f:
                self.interaction_history = json.load(f)
        else:
            self.interaction_history = []
            
        if success:
            print("Cerveau chargé avec succès !")
        else:
            print("Certaines parties du cerveau n'ont pas pu être chargées.")
            
        return success
    
    def import_datasets(self, max_entries=300):
        """Importe des jeux de données de conversations pour pré-alimenter la mémoire"""
        print("\nDémarrage de l'importation des jeux de données...")
        
        # Initialise l'importateur de données
        importer = DatasetImporter(self.memory_system, self.learning_system)
        
        # Affiche les datasets disponibles
        importer.list_available_datasets()
        
        # Importe plusieurs jeux de données
        try:
            total_imported = importer.import_multiple_datasets(max_entries_per_dataset=max_entries)
            print(f"\nImportation terminée avec succès: {total_imported} éléments ajoutés à la mémoire")
            return total_imported
        except Exception as e:
            print(f"Erreur lors de l'importation des datasets: {str(e)}")
            return 0

if __name__ == "__main__":
    # Analyse des arguments de ligne de commande
    parser = argparse.ArgumentParser(description='Baby AI Brain - Un cerveau artificiel qui apprend comme un bébé')
    parser.add_argument('--host', default='127.0.0.1', help='Adresse IP du serveur web')
    parser.add_argument('--port', type=int, default=5000, help='Port du serveur web')
    parser.add_argument('--debug', action='store_true', help='Active le mode débogage')
    parser.add_argument('--import', dest='import_datasets', action='store_true',
                      help='Importer des jeux de données pour pré-alimenter la mémoire')
    parser.add_argument('--max-entries', type=int, default=200,
                      help='Nombre maximum d\'entrées à importer par dataset')
    args = parser.parse_args()
    
    # Création du cerveau
    brain = BabyBrain()
    
    # Tente de charger un cerveau existant
    if os.path.exists('data/brain_state.pt'):
        print("Cerveau existant détecté, chargement en cours...")
        brain.load()
    else:
        print("Aucun cerveau existant trouvé, création d'un nouveau cerveau...")
    
    # Import des datasets si demandé
    if args.import_datasets:
        print("Pré-alimentation du cerveau avec des datasets...") 
        imported_count = brain.import_datasets(max_entries=args.max_entries)
        
        # Force la consolidation des mémoires à court terme vers la mémoire à long terme
        if imported_count > 0:
            print("\nConsolidation des mémoires importées...")
            consolidated = brain.memory_system.consolidate_memories()
            print(f"{consolidated} mémoires ont été consolidées dans le réseau à long terme")
            
        # Sauvegarde après importation
        brain.save()
    
    # Affichage de l'adresse d'accès
    print(f"\nDémarrage de l'interface web sur http://{args.host}:{args.port}")
    print("Utilisez Ctrl+C pour arrêter le serveur\n")
    
    # Démarre l'interface web
    web_interface.start_interface(brain, host=args.host, port=args.port, debug=args.debug)
