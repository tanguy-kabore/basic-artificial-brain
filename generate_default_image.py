import matplotlib.pyplot as plt
import networkx as nx
import os

# Création du dossier si nécessaire
os.makedirs('static/visualizations', exist_ok=True)

# Création du graphe
G = nx.DiGraph()

# Ajout des nœuds avec taille et couleur
G.add_node('Concept central', size=1500, color='#e74c3c')
G.add_node('Apprentissage', size=700, color='#3498db')
G.add_node('Mémoire', size=700, color='#2ecc71')
G.add_node('Exploration', size=700, color='#9b59b6')
G.add_node('Langage', size=700, color='#f39c12')

# Ajout des liens
G.add_edge('Concept central', 'Apprentissage', weight=0.8)
G.add_edge('Concept central', 'Mémoire', weight=0.7)
G.add_edge('Concept central', 'Exploration', weight=0.6)
G.add_edge('Concept central', 'Langage', weight=0.5)
G.add_edge('Apprentissage', 'Mémoire', weight=0.4)
G.add_edge('Mémoire', 'Langage', weight=0.3)

# Disposition du graphe
pos = nx.spring_layout(G, seed=42)

# Préparation des attributs visuels
node_sizes = [G.nodes[node]['size'] for node in G.nodes()]
node_colors = [G.nodes[node]['color'] for node in G.nodes()]
edge_weights = [G.edges[edge]['weight']*3 for edge in G.edges()]

# Création de la figure
plt.figure(figsize=(10, 8))
nx.draw_networkx(
    G, pos,
    with_labels=True,
    node_size=node_sizes,
    node_color=node_colors,
    width=edge_weights,
    edge_color='gray',
    font_size=12,
    font_color='black',
    font_weight='bold',
    alpha=0.8
)

plt.title('Réseau de Mémoire - Baby AI Brain', fontsize=16)
plt.axis('off')

# Sauvegarde de l'image
plt.savefig('static/visualizations/default_memory_network.png', dpi=100, bbox_inches='tight')
plt.close()

print("Image par défaut générée avec succès!")
