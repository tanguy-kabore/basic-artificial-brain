import numpy as np
import torch
import random
import time
import json
import os
from datetime import datetime

class LearningSystem:
    """
    Système d'apprentissage qui coordonne les différentes stratégies
    d'apprentissage du cerveau artificiel.
    """
    
    def __init__(self, neural_core, memory_system):
        self.neural_core = neural_core
        self.memory_system = memory_system
        
        # Paramètres d'apprentissage
        self.exploration_rate = 0.9  # Taux d'exploration élevé au début
        self.learning_rate_decay = 0.9999  # Diminution progressive du taux d'apprentissage
        self.min_exploration_rate = 0.1  # Valeur minimale pour l'exploration
        
        # Métriques d'apprentissage
        self.total_experiences = 0
        self.reward_history = []
        self.loss_history = []
        
        # Concepts appris
        self.concepts = {}
        self.association_strengths = {}
        
    def learn_from_interaction(self, input_data, feedback, is_positive=True):
        """
        Apprend à partir d'une interaction avec un humain
        - input_data: données d'entrée (texte, vecteur, etc.)
        - feedback: retour de l'humain
        - is_positive: indique si le retour est positif ou négatif
        """
        # Préparation des données
        if isinstance(input_data, str):
            # Encodage très simple du texte (à améliorer dans un vrai système)
            input_vector = np.zeros(100)  # Taille arbitraire
            for i, char in enumerate(input_data[:100]):
                input_vector[i % 100] = ord(char) / 255.0
        else:
            input_vector = input_data
            
        # Calcul de la récompense en fonction du feedback
        reward = 1.0 if is_positive else -0.5
        
        # Apprentissage du réseau neural
        output, loss = self.neural_core.learn(input_vector, reward=reward)
        
        # Mise à jour des métriques
        self.total_experiences += 1
        self.reward_history.append(reward)
        self.loss_history.append(loss)
        
        # Stockage de l'expérience en mémoire
        memory_data = {
            'input': input_data,
            'feedback': feedback,
            'output': output.tolist(),
            'reward': reward,
            'timestamp': datetime.now().isoformat()
        }
        
        # L'importance est basée sur la force de la récompense (positive ou négative)
        importance = abs(reward)
        self.memory_system.add_memory(json.dumps(memory_data), 
                                     metadata={'type': 'interaction'},
                                     importance=importance)
        
        # Évolution possible de l'architecture
        if self.total_experiences % 50 == 0:
            self.neural_core.evolve_architecture()
            
        # Consolidation périodique de la mémoire
        if self.total_experiences % 20 == 0:
            self.memory_system.consolidate_memories()
            
        # Décroissance du taux d'exploration
        self.exploration_rate = max(
            self.min_exploration_rate, 
            self.exploration_rate * self.learning_rate_decay
        )
        
        return output, loss
    
    def learn_from_exploration(self, data):
        """
        Apprend de manière autonome à partir de données explorées
        - data: données trouvées (texte, image encodée, etc.)
        """
        # Simplifie les données pour l'apprentissage
        if isinstance(data, str):
            # Encodage très simple du texte
            input_vector = np.zeros(100)  # Taille arbitraire
            for i, char in enumerate(data[:100]):
                input_vector[i % 100] = ord(char) / 255.0
        else:
            input_vector = data
            
        # Décide si on explore au hasard ou si on utilise les connaissances actuelles
        if random.random() < self.exploration_rate:
            # Mode exploration: génère une sortie aléatoire pour encourager l'exploration
            random_output = np.random.randn(100)  # Taille arbitraire de sortie
            
            # Apprentissage avec une petite récompense pour l'exploration
            output, loss = self.neural_core.learn(input_vector, reward=0.1)
            
            # Stocke cette expérience d'exploration en mémoire
            memory_data = {
                'input': data if isinstance(data, str) else "exploration_data",
                'exploration': True,
                'output': output.tolist(),
                'timestamp': datetime.now().isoformat()
            }
            
            self.memory_system.add_memory(json.dumps(memory_data), 
                                         metadata={'type': 'exploration'},
                                         importance=0.3)  # Importance modérée
            
        else:
            # Mode exploitation: utilise les connaissances actuelles
            output, loss = self.neural_core.learn(input_vector, reward=0)
            
        # Mise à jour des métriques
        self.total_experiences += 1
        self.loss_history.append(loss)
        
        return output, loss
    
    def form_concept(self, name, examples):
        """
        Forme un nouveau concept à partir d'exemples
        - name: nom du concept
        - examples: liste d'exemples du concept
        """
        if not examples:
            return False
            
        # Encodage des exemples
        encoded_examples = []
        for example in examples:
            if isinstance(example, str):
                # Encodage simple
                vec = np.zeros(100)
                for i, char in enumerate(example[:100]):
                    vec[i % 100] = ord(char) / 255.0
                encoded_examples.append(vec)
            else:
                encoded_examples.append(example)
                
        # Représentation du concept comme moyenne des exemples
        concept_vector = np.mean(encoded_examples, axis=0)
        
        # Normalisation
        if np.sum(concept_vector) > 0:
            concept_vector = concept_vector / np.linalg.norm(concept_vector)
            
        # Stockage du concept
        self.concepts[name] = {
            'vector': concept_vector,
            'examples': examples,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'usage_count': 0
        }
        
        # Ajoute le concept à la mémoire
        concept_data = {
            'name': name,
            'examples': examples,
            'type': 'concept'
        }
        
        self.memory_system.add_memory(json.dumps(concept_data),
                                     metadata={'type': 'concept', 'name': name},
                                     importance=0.8)  # Concepts sont importants
        
        return True
        
    def associate_concepts(self, concept1, concept2, strength=0.5):
        """
        Crée une association entre deux concepts
        """
        if concept1 not in self.concepts or concept2 not in self.concepts:
            return False
            
        key = f"{concept1}_{concept2}"
        reverse_key = f"{concept2}_{concept1}"
        
        self.association_strengths[key] = strength
        self.association_strengths[reverse_key] = strength
        
        # Mémorisation de l'association
        association_data = {
            'concept1': concept1,
            'concept2': concept2,
            'strength': strength,
            'type': 'association'
        }
        
        self.memory_system.add_memory(json.dumps(association_data),
                                     metadata={'type': 'association'},
                                     importance=0.6)
        
        return True
    
    def get_related_concepts(self, concept_name, threshold=0.3):
        """
        Récupère les concepts liés à un concept donné
        """
        if concept_name not in self.concepts:
            return []
            
        related = []
        for other_concept in self.concepts:
            if other_concept == concept_name:
                continue
                
            key = f"{concept_name}_{other_concept}"
            if key in self.association_strengths and self.association_strengths[key] >= threshold:
                related.append({
                    'name': other_concept,
                    'strength': self.association_strengths[key]
                })
                
        # Trie par force d'association
        related.sort(key=lambda x: x['strength'], reverse=True)
        return related
    
    def save_learning_state(self, path="learning_state.json"):
        """Sauvegarde l'état du système d'apprentissage"""
        # Ne sauvegarde pas les vecteurs numpy directement
        concepts_serializable = {}
        for name, data in self.concepts.items():
            concepts_serializable[name] = {
                'vector': data['vector'].tolist(),
                'examples': data['examples'],
                'created_at': data['created_at'],
                'updated_at': data['updated_at'],
                'usage_count': data['usage_count']
            }
            
        state = {
            'total_experiences': self.total_experiences,
            'exploration_rate': self.exploration_rate,
            'concepts': concepts_serializable,
            'association_strengths': self.association_strengths,
            'reward_history': self.reward_history[-100:],  # Seulement les 100 derniers
            'loss_history': self.loss_history[-100:]  # Seulement les 100 derniers
        }
        
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
            
        print(f"État d'apprentissage sauvegardé dans {path}")
    
    def load_learning_state(self, path="learning_state.json"):
        """Charge l'état du système d'apprentissage"""
        if os.path.exists(path):
            with open(path, 'r') as f:
                state = json.load(f)
                
            self.total_experiences = state['total_experiences']
            self.exploration_rate = state['exploration_rate']
            self.association_strengths = state['association_strengths']
            self.reward_history = state['reward_history']
            self.loss_history = state['loss_history']
            
            # Recrée les concepts avec les vecteurs numpy
            self.concepts = {}
            for name, data in state['concepts'].items():
                self.concepts[name] = {
                    'vector': np.array(data['vector']),
                    'examples': data['examples'],
                    'created_at': data['created_at'],
                    'updated_at': data['updated_at'],
                    'usage_count': data['usage_count']
                }
                
            print(f"État d'apprentissage chargé depuis {path}")
            return True
        else:
            print(f"Aucun état d'apprentissage trouvé à {path}")
            return False
