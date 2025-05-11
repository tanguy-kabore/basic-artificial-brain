import os
import json
import random
import urllib.request
import zipfile
import csv
import time
from tqdm import tqdm  # Pour les barres de progression

class DatasetImporter:
    """
    Module pour importer des jeux de données de conversations et pré-alimenter 
    le système de mémoire avec des interactions
    """
    
    def __init__(self, memory_system, learning_system):
        """Initialise l'importateur avec le système de mémoire et d'apprentissage"""
        self.memory_system = memory_system
        self.learning_system = learning_system
        self.data_dir = "data/datasets"
        
        # Crée le répertoire des datasets s'il n'existe pas
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Liste des sources de données locales disponibles
        self.available_datasets = {
            "phrases_francaises": {
                "file": "data/datasets/phrases_francaises.txt",
                "parser": self._parse_text_dialogue,
                "description": "Phrases et expressions françaises courantes",
                "size_mb": 0.1,
                "is_local": True
            },
            "conversations_fr": {
                "file": "data/datasets/conversations_fr.json",
                "parser": self._parse_text_dialogue,
                "description": "Conversations en français",
                "size_mb": 0.1,
                "is_local": True
            },
            "articles_fr": {
                "file": "data/datasets/articles_fr.txt",
                "parser": self._parse_text_dialogue,
                "description": "Articles courts sur divers sujets en français",
                "size_mb": 0.2,
                "is_local": True
            },
            "questions_reponses": {
                "file": "data/datasets/questions_reponses.csv",
                "parser": self._parse_text_dialogue,
                "description": "Paires de questions et réponses sur l'IA",
                "size_mb": 0.1,
                "is_local": True
            }
        }
        
    def list_available_datasets(self):
        """Affiche les jeux de données disponibles"""
        print("\nJeux de données disponibles:")
        print("----------------------------")
        for key, dataset in self.available_datasets.items():
            print(f"- {key}: {dataset['description']} ({dataset['size_mb']} MB)")
        print("----------------------------")
        
    def get_dataset_file(self, dataset_name):
        """Récupère le chemin vers le fichier de données local"""
        if dataset_name not in self.available_datasets:
            print(f"Erreur: Le jeu de données '{dataset_name}' n'est pas disponible")
            return None
            
        dataset = self.available_datasets[dataset_name]
        
        # Vérifie si c'est un dataset local
        if dataset.get("is_local", False):
            file_path = dataset["file"]
            # Vérifie si le fichier existe
            if os.path.exists(file_path):
                return file_path
            else:
                print(f"Erreur: Le fichier local {file_path} n'existe pas")
                return None
        else:
            # Ancienne logique de téléchargement (non utilisée pour l'instant)
            print(f"Les datasets distants ne sont plus supportés")
            return None
    
    def import_dataset(self, dataset_name, max_entries=500):
        """
        Importe un jeu de données spécifique et pré-alimente le système de mémoire
        - max_entries: nombre maximum d'entrées à importer pour éviter de surcharger
        """
        if dataset_name not in self.available_datasets:
            print(f"Erreur: Le jeu de données '{dataset_name}' n'est pas disponible")
            return 0
            
        dataset = self.available_datasets[dataset_name]
        
        # Récupérer le chemin du fichier
        filename = self.get_dataset_file(dataset_name)
        if not filename:
            print(f"Impossible d'accéder au fichier pour {dataset_name}")
            return 0
        
        # Parser et importer les données
        print(f"Importation des données de {dataset_name}...")
        
        try:
            entries_imported = dataset["parser"](filename, max_entries)
            print(f"Importation terminée: {entries_imported} éléments ajoutés à la mémoire")
            return entries_imported
        except Exception as e:
            print(f"Erreur lors de l'importation: {str(e)}")
            return 0
    
    def import_multiple_datasets(self, max_entries_per_dataset=200):
        """Importe plusieurs jeux de données avec un nombre limité d'entrées par dataset"""
        total_imported = 0
        for dataset_name in self.available_datasets.keys():
            try:
                print(f"\nImportation de {dataset_name}...")
                imported = self.import_dataset(dataset_name, max_entries_per_dataset)
                total_imported += imported
                
                # Petite pause entre les datasets pour éviter de surcharger le système
                time.sleep(1)
            except Exception as e:
                print(f"Erreur lors de l'importation de {dataset_name}: {str(e)}")
        
        return total_imported
    
    def _parse_daily_dialog(self, filename, max_entries):
        """Parse le jeu de données Daily Dialog"""
        # Localisation des fichiers après décompression
        train_file = os.path.join(self.data_dir, "dailydialog", "train.json")
        
        if not os.path.exists(train_file):
            print(f"Fichier introuvable après décompression: {train_file}")
            return 0
        
        imported_count = 0
        
        with open(train_file, 'r', encoding='utf-8') as f:
            dialogs = json.load(f)
            
            # Traduction simple en français (normalement on utiliserait un service de traduction)
            translations = {
                "hello": "bonjour",
                "hi": "salut",
                "how are you": "comment ça va",
                "fine": "bien",
                "good": "bien",
                "thank you": "merci",
                "thanks": "merci",
                "yes": "oui",
                "no": "non",
                "please": "s'il vous plaît",
                "sorry": "désolé",
                "goodbye": "au revoir",
                "bye": "à bientôt"
            }
            
            # Limite au nombre d'entrées spécifié
            for dialog in dialogs[:max_entries]:
                try:
                    context = ""
                    
                    # Extraire les tours de parole
                    utterances = dialog.get('utterances', [])
                    
                    # Traduire de manière basique
                    for utterance in utterances:
                        utterance_lower = utterance.lower()
                        # Remplacer les mots anglais par leurs équivalents français
                        for eng, fr in translations.items():
                            utterance_lower = utterance_lower.replace(eng, fr)
                        
                        # Ajouter au contexte
                        context += utterance_lower + " "
                        
                        # Ajouter à la mémoire avec une importance moyenne
                        if len(utterance_lower) > 10:  # Ignorer les phrases trop courtes
                            self.memory_system.add_memory(
                                content=utterance_lower,
                                metadata={
                                    'source': 'daily_dialog',
                                    'type': 'conversation',
                                    'context': context[:100]  # Limiter le contexte
                                },
                                importance=0.6  # Importance moyenne
                            )
                            imported_count += 1
                            
                except Exception as e:
                    print(f"Erreur sur un dialogue: {str(e)}")
                    continue
        
        return imported_count
    
    def _parse_text_dialogue(self, filename, max_entries):
        """Parse les dialogues à partir d'un fichier texte"""
        # Cette fonction est adaptative et fonctionne avec divers formats textes
        imported_count = 0
        
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Détecter le format selon l'extension
                if filename.endswith('.json'):
                    # Essayer de parser comme JSON
                    try:
                        data = json.loads(content)
                        # Extraire le texte selon la structure
                        if isinstance(data, list):
                            # Si c'est une liste, parcourir les éléments
                            text_items = []
                            for item in data[:max_entries*2]:  # Double pour avoir plus de choix
                                if isinstance(item, dict):
                                    # Extraire des valeurs de dictionnaire
                                    for k, v in item.items():
                                        if isinstance(v, str) and len(v) > 30:
                                            text_items.append(v)
                                elif isinstance(item, str) and len(item) > 30:
                                    text_items.append(item)
                            # Limiter au nombre demandé
                            paragraphs = text_items[:max_entries]
                        elif isinstance(data, dict):
                            # Si c'est un dict, extraire les valeurs string
                            paragraphs = []
                            for k, v in data.items():
                                if isinstance(v, str) and len(v) > 40:
                                    paragraphs.append(v)
                                elif isinstance(v, dict):
                                    # Récursion simple sur un niveau
                                    for k2, v2 in v.items():
                                        if isinstance(v2, str) and len(v2) > 40:
                                            paragraphs.append(v2)
                            # Limiter au nombre demandé
                            paragraphs = paragraphs[:max_entries]
                        else:
                            paragraphs = [str(data)][:max_entries]
                    except json.JSONDecodeError:
                        # Si échec de JSON, traiter comme texte normal
                        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()][:max_entries]
                
                elif filename.endswith('.csv'):
                    # Traiter comme CSV
                    try:
                        # Utiliser un StringIO pour éviter de réécrire sur disque
                        import io
                        import csv
                        reader = csv.reader(io.StringIO(content))
                        paragraphs = []
                        for row in reader:
                            if row and any(len(cell) > 30 for cell in row):
                                # Concaténer les cellules de la ligne
                                paragraphs.append(" ".join(cell for cell in row if len(cell) > 2))
                            if len(paragraphs) >= max_entries:
                                break
                    except Exception as csv_err:
                        print(f"Erreur lors du parsing CSV: {str(csv_err)}")
                        # Fallback en texte
                        paragraphs = [p.strip() for p in content.split('\n') if len(p.strip()) > 50][:max_entries]
                
                elif filename.endswith('.md'):
                    # Traiter comme Markdown
                    lines = content.split('\n')
                    paragraphs = []
                    current_paragraph = []
                    
                    for line in lines:
                        line = line.strip()
                        # Ignore les lignes de titre et les séparateurs
                        if line.startswith('#') or line.startswith('---') or line.startswith('```'):
                            if current_paragraph:
                                paragraphs.append(' '.join(current_paragraph))
                                current_paragraph = []
                        elif line:  # Ligne non vide
                            current_paragraph.append(line)
                        elif current_paragraph:  # Ligne vide après un paragraphe
                            paragraphs.append(' '.join(current_paragraph))
                            current_paragraph = []
                    
                    # Ajouter le dernier paragraphe si nécessaire
                    if current_paragraph:
                        paragraphs.append(' '.join(current_paragraph))
                    
                    # Filtrer les paragraphes trop courts
                    paragraphs = [p for p in paragraphs if len(p) > 50][:max_entries]
                else:
                    # Format texte générique
                    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 50][:max_entries]
                
                # Traitement et mémorisation des paragraphes
                for paragraph in paragraphs:
                    # Nettoyer le texte
                    paragraph = paragraph.replace('\n', ' ').replace('  ', ' ').strip()
                    
                    if len(paragraph) > 50:  # Ignorer les paragraphes trop courts
                        # Ajouter à la mémoire
                        self.memory_system.add_memory(
                            content=paragraph,
                            metadata={
                                'source': 'dataset_import',
                                'type': 'paragraph',
                                'filename': os.path.basename(filename)
                            },
                            importance=0.6  # Importance moyenne-haute
                        )
                        imported_count += 1
                        
                        # Apprentissage direct
                        self.learning_system.learn_from_exploration(paragraph)
                        
                        # Séparer également en phrases pour un apprentissage plus granulaire
                        sentences = [s.strip() for s in paragraph.split('.') if len(s.strip()) > 20]
                        for sentence in sentences[:3]:  # Limiter à 3 phrases par paragraphe
                            self.memory_system.add_memory(
                                content=sentence,
                                metadata={
                                    'source': 'dataset_import',
                                    'type': 'sentence',
                                    'context': paragraph[:100]  # Limiter le contexte
                                },
                                importance=0.5  # Importance moyenne
                            )
                            imported_count += 1
                            
                            # Apprentissage direct
                            self.learning_system.learn_from_exploration(sentence)
        except Exception as e:
            print(f"Erreur lors du parsing du fichier texte: {str(e)}")
            
        return imported_count
    
    def _parse_open_subtitles(self, filename, max_entries):
        """Parse le jeu de données OpenSubtitles"""
        # Ce dataset est volumineux, nous allons donc échantillonner
        imported_count = 0
        
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                lines = []
                
                # Lire les 5000 premières lignes pour échantillonner
                for _ in range(5000):
                    try:
                        line = f.readline()
                        if not line:
                            break
                        if len(line.strip()) > 10:
                            lines.append(line.strip())
                    except:
                        continue
                
                # Échantillonner aléatoirement
                if lines:
                    sample_size = min(max_entries, len(lines))
                    samples = random.sample(lines, sample_size)
                    
                    for line in samples:
                        self.memory_system.add_memory(
                            content=line,
                            metadata={
                                'source': 'open_subtitles',
                                'type': 'subtitle'
                            },
                            importance=0.5  # Importance moyenne
                        )
                        imported_count += 1
                        
                        # Apprentissage direct
                        self.learning_system.learn_from_exploration(line)
        except Exception as e:
            print(f"Erreur lors du parsing d'OpenSubtitles: {str(e)}")
            
        return imported_count
