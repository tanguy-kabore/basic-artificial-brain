import numpy as np
import torch
import networkx as nx
import json
import os
import pickle
from datetime import datetime
# Configurer Matplotlib pour utiliser un backend non-interactif
import matplotlib
matplotlib.use('Agg')  # Agg est un backend non-GUI
import matplotlib.pyplot as plt
from collections import defaultdict, deque

class MemorySystem:
    """
    Système de mémoire pour stocker et récupérer des informations.
    Comprend:
    - Mémoire à court terme (buffer temporaire)
    - Mémoire à long terme (réseau de concepts liés)
    - Mécanisme de consolidation (transfert de court à long terme)
    """
    
    def __init__(self, stm_capacity=50, encoding_size=100):
        # Mémoire à court terme (Short-Term Memory)
        self.stm_capacity = stm_capacity
        self.stm_buffer = deque(maxlen=stm_capacity)
        
        # Mémoire à long terme (Long-Term Memory) - réseau de concepts
        self.ltm_network = nx.DiGraph()
        
        # Taille de l'encodage des souvenirs
        self.encoding_size = encoding_size
        
        # Compteur pour l'attribution d'IDs uniques
        self.memory_counter = 0
        
        # Cache pour les encodages de mots
        self.word_encodings = {}
        
    def _generate_word_encoding(self, word):
        """Génère un encodage vectoriel simple pour un mot"""
        if word in self.word_encodings:
            return self.word_encodings[word]
        
        # Une méthode naïve d'encodage basée sur les caractères
        # Dans un système plus avancé, on utiliserait des embeddings
        encoding = np.zeros(self.encoding_size)
        for i, char in enumerate(word):
            if i < self.encoding_size:
                encoding[i] = ord(char) / 255.0
                
        # Normalisation
        if np.sum(encoding) > 0:
            encoding = encoding / np.linalg.norm(encoding)
            
        self.word_encodings[word] = encoding
        return encoding
    
    def _encode_memory(self, memory_data):
        """Encode un souvenir en vecteur"""
        # Si c'est déjà un vecteur compatible
        if isinstance(memory_data, np.ndarray) and memory_data.shape[0] == self.encoding_size:
            return memory_data
        
        # Si c'est du texte
        if isinstance(memory_data, str):
            # Encodage très simplifié du texte
            words = memory_data.lower().split()
            if not words:
                return np.zeros(self.encoding_size)
                
            encodings = [self._generate_word_encoding(word) for word in words]
            return np.mean(encodings, axis=0)
        
        # Pour d'autres types de données, retourne un vecteur zéro
        return np.zeros(self.encoding_size)
    
    def add_memory(self, content, metadata=None, importance=0.5):
        """
        Ajoute un nouveau souvenir à la mémoire à court terme
        - content: le contenu du souvenir (texte, vecteur, etc.)
        - metadata: informations additionnelles (source, contexte, etc.)
        - importance: valeur entre 0 et 1 indiquant l'importance du souvenir
        """
        memory_id = self.memory_counter
        self.memory_counter += 1
        
        # Encode le contenu
        encoding = self._encode_memory(content)
        
        # Crée l'objet mémoire
        memory = {
            'id': memory_id,
            'content': content,
            'encoding': encoding,
            'metadata': metadata or {},
            'importance': importance,
            'created_at': datetime.now().isoformat(),
            'access_count': 0,
            'last_accessed': None
        }
        
        # Ajoute à la mémoire à court terme
        self.stm_buffer.append(memory)
        
        # Si le souvenir est important, le consolide immédiatement
        if importance > 0.7:
            self._consolidate_memory(memory)
            
        return memory_id
    
    def _consolidate_memory(self, memory):
        """Transfère un souvenir de la mémoire à court terme vers la mémoire à long terme"""
        # Ajoute le nœud au réseau
        self.ltm_network.add_node(memory['id'], **memory)
        
        # Trouve les souvenirs similaires pour créer des liens
        for node_id in self.ltm_network.nodes():
            if node_id == memory['id']:
                continue
                
            node_data = self.ltm_network.nodes[node_id]
            # Calcule la similarité cosinus
            sim = np.dot(memory['encoding'], node_data['encoding'])
            
            # Si la similarité est suffisante, crée un lien
            if sim > 0.3:
                self.ltm_network.add_edge(memory['id'], node_id, weight=sim)
                self.ltm_network.add_edge(node_id, memory['id'], weight=sim)
    
    def consolidate_memories(self):
        """Processus périodique de consolidation des souvenirs"""
        # Trie les souvenirs par importance
        memories_to_consolidate = sorted(list(self.stm_buffer), 
                                         key=lambda x: x['importance'], 
                                         reverse=True)
        
        # Prend les plus importants (30% des souvenirs)
        num_to_consolidate = max(1, int(len(memories_to_consolidate) * 0.3))
        
        for memory in memories_to_consolidate[:num_to_consolidate]:
            if memory['id'] not in self.ltm_network:
                self._consolidate_memory(memory)
                
        # Vide la mémoire à court terme
        self.stm_buffer.clear()
        
        return num_to_consolidate
    
    def retrieve_memory(self, query, top_k=3):
        """
        Récupère les souvenirs les plus pertinents en fonction d'une requête
        - query: texte ou vecteur de requête
        - top_k: nombre de souvenirs à récupérer
        """
        # Encode la requête
        query_encoding = self._encode_memory(query)
        
        # Cherche dans la mémoire à court terme
        stm_memories = list(self.stm_buffer)
        similarities_stm = []
        
        for memory in stm_memories:
            sim = np.dot(query_encoding, memory['encoding'])
            similarities_stm.append((memory, sim))
        
        # Cherche dans la mémoire à long terme
        ltm_memories = []
        similarities_ltm = []
        
        for node_id in self.ltm_network.nodes():
            memory = self.ltm_network.nodes[node_id]
            sim = np.dot(query_encoding, memory['encoding'])
            similarities_ltm.append((memory, sim))
            
            # Met à jour le compteur d'accès
            self.ltm_network.nodes[node_id]['access_count'] += 1
            self.ltm_network.nodes[node_id]['last_accessed'] = datetime.now().isoformat()
        
        # Combine et trie les résultats
        all_similarities = similarities_stm + similarities_ltm
        all_similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Retourne les top_k résultats
        return [item[0] for item in all_similarities[:top_k]]
    
    def visualize_memory_network(self, filename='memory_network.png', max_nodes_to_show=50):
        """Visualise le réseau de mémoire à long terme"""
        plt.figure(figsize=(15, 12), dpi=100)
        
        if len(self.ltm_network) == 0:
            # Si le réseau est vide, crée une image avec un message
            print("Le réseau de mémoire est vide. Création d'une image par défaut.")
            plt.text(0.5, 0.5, "Le réseau de mémoire est vide\nLe cerveau commence à apprendre...",
                     horizontalalignment='center', verticalalignment='center',
                     fontsize=20, color='#3498db')
            
            # Ajout d'un cercle représentant le cerveau vide
            circle = plt.Circle((0.5, 0.25), 0.15, color='#e74c3c', alpha=0.6)
            plt.gca().add_patch(circle)
            
            # Ajout de petits cercles représentant des connexions potentielles
            for i in range(5):
                x = 0.5 + 0.3 * np.cos(i * 2 * np.pi / 5)
                y = 0.25 + 0.3 * np.sin(i * 2 * np.pi / 5)
                small_circle = plt.Circle((x, y), 0.05, color='#3498db', alpha=0.4)
                plt.gca().add_patch(small_circle)
                # Ligne de connexion potentielle
                plt.plot([0.5, x], [0.25, y], '--', color='#bdc3c7', alpha=0.4, linewidth=1)
        else:
            # Information sur la taille du réseau
            total_nodes = len(self.ltm_network)
            total_edges = len(self.ltm_network.edges())
            print(f"Réseau de mémoire: {total_nodes} nœuds, {total_edges} connexions")
            
            # Sélectionne un sous-ensemble de nœuds si nécessaire
            if total_nodes > max_nodes_to_show:
                # Sélectionner les nœuds par importance
                nodes_with_importance = [(node, self.ltm_network.nodes[node]['importance']) 
                                        for node in self.ltm_network.nodes()]
                nodes_with_importance.sort(key=lambda x: x[1], reverse=True)
                selected_nodes = [n[0] for n in nodes_with_importance[:max_nodes_to_show]]
                
                # Créer un sous-graphe
                subgraph = self.ltm_network.subgraph(selected_nodes)
                print(f"Affichage des {len(subgraph)} nœuds les plus importants sur {total_nodes} total")
                graph_to_display = subgraph
            else:
                graph_to_display = self.ltm_network
            
            # Utilisation d'un algorithme de disposition plus adapté aux grands graphes
            try:
                # Kamada-Kawai fonctionne bien pour les graphes de taille moyenne
                pos = nx.kamada_kawai_layout(graph_to_display) 
            except:
                # Spring layout si KK échoue
                pos = nx.spring_layout(graph_to_display, k=0.3, iterations=50)
            
            # Classification des nœuds par type/thème pour les couleurs
            node_colors = []
            node_sizes = []
            node_groups = {}
            
            for node in graph_to_display.nodes():
                # Importances pour la taille des nœuds (normalisées)
                importance = graph_to_display.nodes[node]['importance']
                node_sizes.append(100 + importance * 500)  # Plus petit pour les grands graphes
                
                # Groupes/couleurs basés sur les métadonnées ou le contenu
                metadata = graph_to_display.nodes[node].get('metadata', {})
                content = graph_to_display.nodes[node].get('content', '')
                
                # Déterminer un groupe pour le nœud
                if 'type' in metadata:
                    group = metadata['type']
                elif 'source' in metadata:
                    group = metadata['source']
                elif isinstance(content, str) and len(content) > 10:
                    # Tente de classifier par premier mot significatif
                    words = content.lower().split()
                    group = words[0] if words else 'unknown'
                else:
                    group = 'unknown'
                
                if group not in node_groups:
                    node_groups[group] = len(node_groups)
                
                # Assigner une couleur basée sur le groupe
                color_idx = node_groups[group] % 10  # Cycle parmi 10 couleurs
                colormap = plt.cm.tab10
                node_colors.append(colormap(color_idx))
            
            # Détermination du poids des arêtes
            edge_weights = []
            for u, v in graph_to_display.edges():
                try:
                    weight = graph_to_display[u][v]['weight'] * 2
                    edge_weights.append(max(0.5, min(4.0, weight)))  # Limiter la plage
                except KeyError:
                    edge_weights.append(0.5)  # Valeur par défaut
            
            # Dessin du graphe
            nx.draw_networkx_nodes(graph_to_display, pos, node_size=node_sizes, 
                                   node_color=node_colors, alpha=0.7)
            nx.draw_networkx_edges(graph_to_display, pos, width=edge_weights,
                                   alpha=0.3, edge_color='gray', arrowsize=5)
            
            # Étiquettes des nœuds (plus informatives)
            labels = {}
            for node in graph_to_display.nodes():
                content = graph_to_display.nodes[node]['content']
                if isinstance(content, str):
                    # Récupérer les premiers mots pour une étiquette concise
                    words = content.split()
                    if len(words) >= 2:
                        label = ' '.join(words[:2])
                        if len(label) > 15:
                            label = label[:15] + '...'
                        labels[node] = f"[{label}]"
                    else:
                        labels[node] = f"[{content[:15]}]" if len(content) > 15 else f"[{content}]"
                else:
                    labels[node] = f"ID:{node}"
            
            # Ajuster la taille de police en fonction du nombre de nœuds
            font_size = max(4, min(9, 12 - len(graph_to_display) // 20))
            nx.draw_networkx_labels(graph_to_display, pos, labels, font_size=font_size, font_weight='bold')
            
            # Ajouter une légende pour les groupes
            legend_elements = []
            for group, idx in node_groups.items():
                color_idx = idx % 10
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                                 markerfacecolor=colormap(color_idx), markersize=10,
                                                 label=group))
            
            # Placer la légende hors du graphe
            plt.legend(handles=legend_elements, loc='upper right', fontsize=9)
            
            # Ajouter un texte d'information sur le nombre total de nœuds
            if total_nodes > max_nodes_to_show:
                plt.text(0.02, 0.02, 
                         f"Affichage des {len(graph_to_display)} nœuds les plus importants sur {total_nodes} nœuds au total",
                         fontsize=8, transform=plt.gca().transAxes, 
                         bbox=dict(facecolor='white', alpha=0.7))
        
        plt.title("Réseau de Mémoire - Baby AI Brain")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        
        print(f"Visualisation sauvegardée dans {filename}")
    
    def save_memory_system(self, path="memory_system.pkl"):
        """Sauvegarde le système de mémoire"""
        state = {
            'stm_buffer': list(self.stm_buffer),
            'ltm_network': nx.node_link_data(self.ltm_network),
            'memory_counter': self.memory_counter,
            'word_encodings': self.word_encodings,
            'stm_capacity': self.stm_capacity,
            'encoding_size': self.encoding_size
        }
        
        with open(path, 'wb') as f:
            pickle.dump(state, f)
            
        print(f"Système de mémoire sauvegardé dans {path}")
    
    def load_memory_system(self, path="memory_system.pkl"):
        """Charge le système de mémoire"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                state = pickle.load(f)
            
            self.stm_buffer = deque(state['stm_buffer'], maxlen=state['stm_capacity'])
            self.ltm_network = nx.node_link_graph(state['ltm_network'])
            self.memory_counter = state['memory_counter']
            self.word_encodings = state['word_encodings']
            self.stm_capacity = state['stm_capacity']
            self.encoding_size = state['encoding_size']
            
            print(f"Système de mémoire chargé depuis {path}")
            return True
        else:
            print(f"Aucun système de mémoire trouvé à {path}")
            return False
