import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import random
import json
import os
from datetime import datetime

class NeuralCore(nn.Module):
    def __init__(self, input_size=100, hidden_size=128, output_size=100):
        """
        Initialise un réseau neuronal simple qui servira de base au cerveau.
        """
        super(NeuralCore, self).__init__()
        
        # Architecture de base - sera étendue au fur et à mesure de l'apprentissage
        self.input_layer = nn.Linear(input_size, hidden_size)
        self.hidden_layer = nn.Linear(hidden_size, hidden_size)
        self.output_layer = nn.Linear(hidden_size, output_size)
        
        # Paramètres d'apprentissage
        self.learning_rate = 0.01
        self.curiosity_factor = 0.1  # Encourage l'exploration
        self.optimizer = optim.Adam(self.parameters(), lr=self.learning_rate)
        
        # Initialisation des poids de manière aléatoire pour partir d'un "cerveau vierge"
        self._initialize_weights()
        
        # Compteur d'expériences pour suivre l'évolution
        self.experience_counter = 0
        
    def _initialize_weights(self):
        """Initialise les poids de manière aléatoire pour simuler un cerveau vierge"""
        for param in self.parameters():
            nn.init.uniform_(param, -0.1, 0.1)
        
    def forward(self, x):
        """Propagation avant dans le réseau"""
        x = F.relu(self.input_layer(x))
        x = F.relu(self.hidden_layer(x))
        x = self.output_layer(x)
        return x
    
    def learn(self, input_data, target_output=None, reward=0):
        """
        Apprend à partir d'une entrée et d'une sortie attendue ou d'une récompense.
        Si target_output est None, utilise l'apprentissage par renforcement avec la récompense.
        """
        self.experience_counter += 1
        
        # Conversion des données en tenseurs
        x = torch.FloatTensor(input_data)
        
        # Propagation avant
        output = self(x)
        
        # Calcul de la perte selon le type d'apprentissage
        if target_output is not None:
            # Apprentissage supervisé si une sortie cible est fournie
            y = torch.FloatTensor(target_output)
            loss = F.mse_loss(output, y)
        else:
            # Apprentissage par renforcement avec curiosité
            # Plus la sortie est différente de zéro, plus on encourage l'exploration
            novelty = torch.mean(torch.abs(output))
            loss = -reward - self.curiosity_factor * novelty
        
        # Rétropropagation
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return output.detach().numpy(), loss.item()
    
    def evolve_architecture(self):
        """
        Fait évoluer l'architecture du réseau au fil du temps
        Ce mécanisme est simplifié, mais pourrait être plus complexe
        """
        if self.experience_counter % 1000 == 0:
            # Augmente légèrement la taille du réseau
            old_hidden_layer = self.hidden_layer
            new_hidden_size = old_hidden_layer.out_features + 1
            
            # Crée une nouvelle couche plus grande
            new_hidden_layer = nn.Linear(old_hidden_layer.in_features, new_hidden_size)
            
            # Copie les poids existants
            with torch.no_grad():
                new_hidden_layer.weight[:old_hidden_layer.out_features, :] = old_hidden_layer.weight
                new_hidden_layer.bias[:old_hidden_layer.out_features] = old_hidden_layer.bias
            
            # Met à jour la couche de sortie
            old_output_layer = self.output_layer
            new_output_layer = nn.Linear(new_hidden_size, old_output_layer.out_features)
            
            # Copie les poids existants
            with torch.no_grad():
                new_output_layer.weight[:, :old_hidden_layer.out_features] = old_output_layer.weight
                new_output_layer.bias = nn.Parameter(old_output_layer.bias.clone())
            
            # Remplace les couches
            self.hidden_layer = new_hidden_layer
            self.output_layer = new_output_layer
            
            # Met à jour l'optimiseur
            self.optimizer = optim.Adam(self.parameters(), lr=self.learning_rate)
            
            print(f"Architecture évoluée: nouvelle taille de couche cachée = {new_hidden_size}")
    
    def save_brain(self, path="brain_state.pt"):
        """Sauvegarde l'état du cerveau"""
        state = {
            'model_state': self.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'experience_counter': self.experience_counter,
            'learning_rate': self.learning_rate,
            'curiosity_factor': self.curiosity_factor,
            'architecture': {
                'input_size': self.input_layer.in_features,
                'hidden_size': self.hidden_layer.out_features,
                'output_size': self.output_layer.out_features
            }
        }
        torch.save(state, path)
        print(f"Cerveau sauvegardé dans {path}")
    
    def load_brain(self, path="brain_state.pt"):
        """Charge l'état du cerveau"""
        if os.path.exists(path):
            state = torch.load(path)
            
            # Recréation de l'architecture si nécessaire
            if self.input_layer.in_features != state['architecture']['input_size'] or \
               self.hidden_layer.out_features != state['architecture']['hidden_size'] or \
               self.output_layer.out_features != state['architecture']['output_size']:
                
                self.input_layer = nn.Linear(state['architecture']['input_size'], state['architecture']['hidden_size'])
                self.hidden_layer = nn.Linear(state['architecture']['hidden_size'], state['architecture']['hidden_size'])
                self.output_layer = nn.Linear(state['architecture']['hidden_size'], state['architecture']['output_size'])
            
            # Chargement des états
            self.load_state_dict(state['model_state'])
            self.optimizer.load_state_dict(state['optimizer_state'])
            self.experience_counter = state['experience_counter']
            self.learning_rate = state['learning_rate']
            self.curiosity_factor = state['curiosity_factor']
            
            print(f"Cerveau chargé depuis {path}")
            return True
        else:
            print(f"Aucun cerveau trouvé à {path}")
            return False
