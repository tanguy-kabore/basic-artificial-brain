import os
import json
import random
import csv

# Assurer que le répertoire existe
os.makedirs('C:/Users/HP/CascadeProjects/baby_ai_brain/data/datasets', exist_ok=True)

# 1. Phrases et expressions françaises courantes
phrases = [
    "Bonjour, comment allez-vous aujourd'hui?",
    "Je suis heureux de vous rencontrer.",
    "Quel temps fait-il aujourd'hui?",
    "Pourriez-vous me dire où se trouve la bibliothèque?",
    "J'aime beaucoup la cuisine française.",
    "Avez-vous vu le dernier film qui est sorti au cinéma?",
    "Je cherche un bon restaurant dans le quartier.",
    "Quelle est votre chanson préférée?",
    "Je travaille comme ingénieur dans une entreprise de technologie.",
    "La France est connue pour ses vins et ses fromages.",
    "Paris est la capitale de la France.",
    "Le Louvre est l'un des musées les plus célèbres du monde.",
    "J'aimerais réserver une table pour deux personnes ce soir.",
    "Pouvez-vous me recommander un bon livre à lire?",
    "Les mathématiques sont essentielles dans de nombreux domaines scientifiques.",
    "L'intelligence artificielle révolutionne notre façon de vivre.",
    "Internet a transformé la manière dont nous communiquons.",
    "La musique a le pouvoir de changer notre humeur.",
    "L'apprentissage d'une nouvelle langue est toujours enrichissant.",
    "La photographie est un art qui capture des moments précieux.",
    "Je voudrais améliorer mes compétences en programmation.",
    "Le changement climatique est l'un des plus grands défis de notre époque.",
    "Les énergies renouvelables sont l'avenir de notre planète.",
    "La lecture est une façon d'explorer de nouveaux mondes.",
    "Le sport est important pour maintenir une bonne santé.",
    "La communication est la clé d'une relation réussie.",
    "La patience est une vertu qui s'acquiert avec le temps.",
    "Les voyages nous permettent de découvrir différentes cultures.",
    "L'éducation est la base d'une société prospère.",
    "La créativité nous aide à résoudre des problèmes complexes.",
    "Le respect mutuel est essentiel dans toute relation.",
    "L'art exprime ce que les mots ne peuvent pas dire.",
    "La technologie évolue à un rythme incroyable.",
    "La nature nous offre des spectacles magnifiques.",
    "Le cinéma est une forme d'art qui raconte des histoires.",
    "La science nous aide à comprendre le monde qui nous entoure.",
    "L'histoire nous permet d'apprendre des erreurs du passé.",
    "La philosophie nous pousse à réfléchir sur le sens de la vie.",
    "La cuisine est un art qui rassemble les gens.",
    "Le rire est le meilleur remède contre le stress.",
]

# 2. Conversations simples
conversations = [
    {
        "dialogue": [
            "Bonjour, comment vas-tu?",
            "Je vais bien, merci! Et toi?",
            "Très bien aussi. Qu'as-tu prévu pour aujourd'hui?",
            "Je vais travailler sur mon projet d'intelligence artificielle.",
            "Oh, c'est intéressant! De quoi s'agit-il?",
            "Je développe un cerveau artificiel qui apprend par lui-même."
        ]
    },
    {
        "dialogue": [
            "Excuse-moi, sais-tu où se trouve la bibliothèque?",
            "Oui, elle est à deux rues d'ici, sur la droite.",
            "Merci beaucoup! Est-elle ouverte le dimanche?",
            "Oui, mais seulement l'après-midi, de 14h à 18h.",
            "Parfait, j'irai demain alors. Merci pour l'information!"
        ]
    },
    {
        "dialogue": [
            "J'ai entendu parler d'un nouveau restaurant dans le quartier.",
            "Ah oui? Quel genre de cuisine propose-t-il?",
            "C'est un restaurant qui sert des plats traditionnels français avec une touche moderne.",
            "Ça a l'air délicieux! On pourrait y aller ce week-end?",
            "Bonne idée! Je vais réserver une table pour samedi soir."
        ]
    },
    {
        "dialogue": [
            "Tu as vu le dernier film de science-fiction?",
            "Non, pas encore. Est-ce qu'il est bon?",
            "Absolument! L'histoire est fascinante et les effets spéciaux sont incroyables.",
            "Tu as piqué ma curiosité! Je vais essayer de le voir ce week-end.",
            "Tu ne seras pas déçu. C'est l'un des meilleurs films que j'ai vus cette année."
        ]
    },
    {
        "dialogue": [
            "J'ai commencé à apprendre la programmation en Python.",
            "C'est un excellent choix! Python est très populaire et relativement facile à apprendre.",
            "Oui, j'apprécie sa syntaxe claire. As-tu des ressources à me recommander?",
            "Il y a plusieurs cours en ligne gratuits qui sont très bien. Je peux te partager quelques liens.",
            "Ce serait super, merci! J'aimerais créer mon propre projet d'IA un jour."
        ]
    },
]

# 3. Articles courts sur divers sujets
articles = [
    {
        "titre": "L'Intelligence Artificielle",
        "contenu": """L'intelligence artificielle (IA) est un domaine de l'informatique qui vise à créer des machines capables de simuler l'intelligence humaine. Elle englobe plusieurs techniques, dont l'apprentissage automatique, qui permet aux ordinateurs d'apprendre à partir de données sans être explicitement programmés. Les applications de l'IA sont nombreuses et touchent de nombreux secteurs: la santé, l'éducation, les transports, la finance et bien d'autres. L'un des défis majeurs de l'IA est de développer des systèmes qui peuvent non seulement traiter de grandes quantités d'informations, mais aussi comprendre le contexte et s'adapter à des situations nouvelles, comme le fait l'intelligence humaine."""
    },
    {
        "titre": "La Cuisine Française",
        "contenu": """La cuisine française est réputée dans le monde entier pour sa finesse et sa diversité. Elle varie considérablement selon les régions, chacune ayant ses spécialités et ses traditions culinaires. Du cassoulet du Sud-Ouest aux crêpes bretonnes, en passant par la bouillabaisse marseillaise et le bœuf bourguignon, la France offre un véritable voyage gastronomique. Les techniques de cuisson, les sauces et les pâtisseries françaises sont particulièrement célèbres et ont influencé de nombreuses cuisines à travers le monde. La tradition du repas français, avec son rituel et son art de vivre, a d'ailleurs été inscrite au patrimoine culturel immatériel de l'UNESCO en 2010."""
    },
    {
        "titre": "L'Histoire de l'Internet",
        "contenu": """L'internet que nous connaissons aujourd'hui est le résultat d'une évolution qui a débuté dans les années 1960 avec le projet ARPANET du département de la Défense américain. Initialement conçu pour connecter quelques ordinateurs de recherche, il s'est progressivement transformé en un réseau mondial reliant des milliards d'appareils. L'invention du World Wide Web par Tim Berners-Lee en 1989 a révolutionné l'accès à l'information en introduisant les pages web et les hyperliens. Depuis, l'internet n'a cessé d'évoluer, passant du Web 1.0 (sites statiques) au Web 2.0 (réseaux sociaux, contenu généré par les utilisateurs) et maintenant vers le Web 3.0 (web sémantique, blockchain, réalité virtuelle). Cette évolution continue de transformer notre façon de communiquer, de travailler et d'accéder à l'information."""
    },
    {
        "titre": "Les Énergies Renouvelables",
        "contenu": """Les énergies renouvelables sont des sources d'énergie dont le renouvellement naturel est assez rapide pour qu'elles puissent être considérées comme inépuisables à l'échelle du temps humain. Les principales formes d'énergies renouvelables sont l'énergie solaire, éolienne, hydraulique, géothermique et la biomasse. Contrairement aux énergies fossiles comme le pétrole, le charbon et le gaz naturel, les énergies renouvelables émettent peu ou pas de gaz à effet de serre et contribuent donc à la lutte contre le changement climatique. De plus en plus de pays investissent massivement dans ces technologies pour réduire leur dépendance aux combustibles fossiles et atteindre leurs objectifs de neutralité carbone. Malgré des défis comme l'intermittence et le stockage, les énergies renouvelables sont en plein essor et leur part dans le mix énergétique mondial ne cesse d'augmenter."""
    },
    {
        "titre": "L'Apprentissage des Langues",
        "contenu": """Apprendre une nouvelle langue est un processus fascinant qui va bien au-delà de la simple mémorisation de vocabulaire et de règles grammaticales. C'est une porte ouverte sur une nouvelle culture, une nouvelle façon de penser et de voir le monde. Les études montrent que le bilinguisme ou le multilinguisme présente de nombreux avantages cognitifs, comme une meilleure concentration, une plus grande flexibilité mentale et même un retard potentiel de l'apparition de maladies neurodégénératives comme Alzheimer. Avec la mondialisation et les technologies numériques, l'apprentissage des langues est plus accessible que jamais, grâce à des applications, des plateformes en ligne et des communautés d'échange linguistique. Que ce soit pour des raisons professionnelles, personnelles ou simplement par passion, l'apprentissage d'une langue étrangère est un enrichissement considérable pour tout individu."""
    },
]

# Fonction pour créer un fichier de phrases
def create_phrases_file():
    outpath = 'C:/Users/HP/CascadeProjects/baby_ai_brain/data/datasets/phrases_francaises.txt'
    with open(outpath, 'w', encoding='utf-8') as f:
        for phrase in phrases:
            f.write(phrase + "\n\n")
    return outpath

# Fonction pour créer un fichier de conversations
def create_conversations_file():
    outpath = 'C:/Users/HP/CascadeProjects/baby_ai_brain/data/datasets/conversations_fr.json'
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)
    return outpath

# Fonction pour créer un fichier d'articles
def create_articles_file():
    outpath = 'C:/Users/HP/CascadeProjects/baby_ai_brain/data/datasets/articles_fr.txt'
    with open(outpath, 'w', encoding='utf-8') as f:
        for article in articles:
            f.write(f"# {article['titre']}\n\n")
            f.write(f"{article['contenu']}\n\n")
            f.write("---\n\n")
    return outpath

# Fonction pour créer un fichier CSV avec des paires question-réponse
def create_qa_file():
    outpath = 'C:/Users/HP/CascadeProjects/baby_ai_brain/data/datasets/questions_reponses.csv'
    qa_pairs = [
        ["Qu'est-ce que l'intelligence artificielle?", "L'intelligence artificielle est un domaine de l'informatique qui vise à créer des machines capables de simuler l'intelligence humaine, notamment pour résoudre des problèmes complexes."],
        ["Comment fonctionne l'apprentissage automatique?", "L'apprentissage automatique permet aux ordinateurs d'apprendre à partir de données sans être explicitement programmés, en utilisant des algorithmes qui identifient des motifs et font des prédictions."],
        ["Qu'est-ce que le deep learning?", "Le deep learning est une branche de l'apprentissage automatique qui utilise des réseaux de neurones artificiels avec plusieurs couches pour analyser des données complexes comme les images ou le texte."],
        ["Quels sont les avantages de l'IA?", "L'IA permet d'automatiser des tâches répétitives, d'analyser de grandes quantités de données, d'améliorer la prise de décision et de résoudre des problèmes complexes dans divers domaines."],
        ["Quels sont les risques liés à l'IA?", "Les risques incluent la perte d'emplois due à l'automatisation, les biais algorithmiques, les questions de vie privée, la dépendance technologique et les préoccupations éthiques sur l'autonomie des systèmes d'IA."],
        ["Qu'est-ce qu'un réseau de neurones?", "Un réseau de neurones est un modèle informatique inspiré du cerveau humain, composé de neurones artificiels interconnectés qui traitent et transmettent des informations pour résoudre des problèmes."],
        ["Comment l'IA peut-elle être utilisée en médecine?", "En médecine, l'IA aide au diagnostic précoce de maladies, à l'analyse d'images médicales, au développement de médicaments, à la personnalisation des traitements et à l'optimisation des systèmes de santé."],
        ["Quelle est la différence entre l'IA faible et l'IA forte?", "L'IA faible est conçue pour des tâches spécifiques (comme jouer aux échecs), tandis que l'IA forte aurait une intelligence généralisée comparable à celle des humains, capable de comprendre et d'apprendre n'importe quelle tâche intellectuelle."],
        ["Qu'est-ce que le traitement du langage naturel?", "Le traitement du langage naturel est une branche de l'IA qui permet aux ordinateurs de comprendre, interpréter et générer le langage humain de manière utile et significative."],
        ["Comment fonctionne la reconnaissance d'images?", "La reconnaissance d'images utilise des algorithmes d'apprentissage profond pour identifier et classifier des objets, des personnes ou des motifs dans des images numériques en analysant leurs caractéristiques visuelles."]
    ]
    
    with open(outpath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Question", "Réponse"])
        for qa in qa_pairs:
            writer.writerow(qa)
    return outpath

# Création des fichiers
print("Création des datasets locaux...")
phrases_file = create_phrases_file()
conversations_file = create_conversations_file()
articles_file = create_articles_file()
qa_file = create_qa_file()

print(f"Datasets créés avec succès:\n- {phrases_file}\n- {conversations_file}\n- {articles_file}\n- {qa_file}")
