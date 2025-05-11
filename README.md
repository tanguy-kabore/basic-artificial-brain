# Baby AI Brain

Un cerveau artificiel autonome qui apprend progressivement à partir de zéro, comme un bébé, en interagissant avec les humains et en explorant le web.

## Concept

Ce système commence sans connaissance préalable et construit son intelligence à travers:
- Les interactions humaines (feedback positif/négatif)
- L'exploration autonome d'informations sur internet
- L'assimilation progressive de connaissances structurées

## Composants principaux

1. **Réseau neuronal** : Architecture neuronale évolutive qui s'adapte et se complexifie avec l'expérience
2. **Système de mémoire** : Stockage et organisation des souvenirs à court et long terme avec visualisation
3. **Système d'apprentissage** : Apprentissage par renforcement et par exploration autonome
4. **Explorateur web** : Module qui parcourt internet pour découvrir de nouvelles informations
5. **Interface utilisateur** : Application web pour interagir avec le cerveau et visualiser sa mémoire

## Fonctionnalités clés

- **Apprentissage autonome** : Le cerveau apprend constamment et évolue sans supervision
- **Recherche web automatique** : Lorsque le cerveau ne connaît pas la réponse à une question, il cherche automatiquement sur internet
- **Visualisation de la mémoire** : Interface graphique pour visualiser le réseau de connaissances
- **Pré-alimentation de données** : Possibilité d'importer des datasets pour accélérer l'apprentissage initial
- **Sauvegarde de l'état** : Le cerveau sauvegarde automatiquement son état pour reprendre l'apprentissage

## Installation

### Prérequis

- Python 3.8+ (recommandé 3.10+)
- Pip (gestionnaire de packages Python)

### Étapes d'installation

1. Clonez le répertoire ou téléchargez les sources
2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

## Configuration initiale

### Création des datasets locaux

Après l'installation, vous pouvez créer des datasets locaux pour pré-alimenter le cerveau :

```bash
# Créer les datasets de base (phrases, conversations, articles, Q&A)
python data/datasets/create_local_datasets.py
```

Ce script génère :
- `phrases_francaises.txt` : Expressions et phrases courantes
- `conversations_fr.json` : Dialogues et conversations
- `articles_fr.txt` : Articles courts sur différents sujets
- `questions_reponses.csv` : Paires de questions-réponses sur l'IA

### Importation des données

Une fois les datasets créés, vous pouvez les importer dans le cerveau :

```bash
# Importer les datasets avec un maximum de 200 entrées par dataset
python main.py --import --max-entries 200
```

Cette étape est cruciale pour donner au cerveau une base de connaissances initiale.

## Utilisation du cerveau

### Démarrage standard

```bash
python main.py
```

### Options avancées

```bash
# Définir l'hôte et le port
python main.py --host 0.0.0.0 --port 8080

# Mode débogage
python main.py --debug
```

### Paramètres disponibles

| Paramètre | Description |
|------------|-------------|
| `--import` | Déclenche l'importation des datasets |
| `--max-entries` | Nombre maximum d'entrées à importer par dataset |
| `--host` | Adresse IP du serveur web (défaut: 127.0.0.1) |
| `--port` | Port du serveur web (défaut: 5000) |
| `--debug` | Active le mode débogage |

### Accès à l'interface

Après le démarrage, ouvrez votre navigateur à l'adresse http://localhost:5000 (ou l'adresse configurée) pour interagir avec le cerveau artificiel.

## Interaction avec le cerveau

### Conversation

- Entrez votre message dans le champ de texte
- Le cerveau répondra en fonction de ses connaissances actuelles
- S'il ne connaît pas la réponse, il cherchera automatiquement sur internet

### Apprentissage par renforcement

- Utilisez les boutons 👍 (positif) et 👎 (négatif) pour indiquer si la réponse est pertinente
- Ce feedback aide le cerveau à améliorer ses réponses futures

### Visualisation de la mémoire

- Cliquez sur "Visualiser la mémoire" pour voir le réseau de connaissances du cerveau
- Les nœuds sont colorés par type de contenu (phrases, articles, questions-réponses, etc.)
- La taille des nœuds représente leur importance dans le réseau

### Récupération de souvenirs

- Vous pouvez demander au cerveau de vous montrer ses souvenirs sur un sujet spécifique
- Cela vous permet de voir comment il organise et stocke les informations

## Structure du projet

### Fichiers principaux

- `main.py` : Composant principal du cerveau artificiel
- `neural_network.py` : Implémentation du réseau neuronal évolutif
- `memory_system.py` : Système de gestion de la mémoire
- `learning_system.py` : Mécanismes d'apprentissage
- `web_explorer.py` : Module d'exploration autonome du web
- `web_interface.py` : Interface utilisateur web
- `dataset_importer.py` : Outil d'importation de datasets

### Outils et scripts

- `data/datasets/create_local_datasets.py` : Script pour générer des datasets locaux
- `static/visualizations/` : Stockage des visualisations du réseau de mémoire
- `templates/` : Templates HTML pour l'interface web

### Organisation des données

- `data/` : Répertoire principal des données
  - `brain_state.pt` : État sauvegardé du réseau neuronal
  - `memory_system.pkl` : État sauvegardé du système de mémoire
  - `learning_state.json` : État sauvegardé du système d'apprentissage
  - `explorer_state.json` : État sauvegardé de l'explorateur web
  - `datasets/` : Contient les datasets utilisés pour l'apprentissage

## Personnalisation

### Ajout de nouveaux datasets

Vous pouvez modifier le fichier `data/datasets/create_local_datasets.py` pour ajouter de nouvelles données selon vos besoins.

Pour importer vos propres données structurées:

1. Ajoutez vos données au script de création ou créez directement des fichiers dans le format approprié (texte, JSON, CSV)
2. Placez les fichiers dans le répertoire `data/datasets/`
3. Modifiez `dataset_importer.py` pour prendre en compte vos nouveaux fichiers si nécessaire

### Modification des paramètres d'apprentissage

Vous pouvez ajuster les paramètres d'apprentissage en modifiant les valeurs dans `learning_system.py` et `neural_network.py`.
