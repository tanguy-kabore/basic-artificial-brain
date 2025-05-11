import requests
from bs4 import BeautifulSoup
import random
import time
import re
import json
import os
from datetime import datetime
import numpy as np
from urllib.parse import urljoin, urlparse

class WebExplorer:
    """
    Système d'exploration web simplifié qui permet au cerveau artificiel
    d'explorer et d'apprendre à partir d'Internet.
    """
    
    def __init__(self, learning_system, start_urls=None):
        self.learning_system = learning_system
        self.visited_urls = set()
        self.url_queue = list(start_urls or [
            "https://simple.wikipedia.org/wiki/Main_Page",
            "https://en.wikipedia.org/wiki/Artificial_intelligence",
            "https://www.goodreads.com/quotes"
        ])
        
        # Historique d'exploration
        self.exploration_history = []
        
        # Paramètres
        self.max_pages_per_session = 5
        self.min_delay_between_requests = 2  # En secondes
        self.max_url_queue_size = 100
        
        # Mot-clés pour l'évaluation de l'intérêt
        self.interest_keywords = [
            "learn", "knowledge", "science", "art", "history",
            "technology", "nature", "human", "world", "life",
            "language", "communication", "understanding"
        ]
        
        # User-Agent pour ne pas être bloqué
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    
    def _is_valid_url(self, url):
        """Vérifie si une URL est valide pour l'exploration"""
        # Ignore les URLs déjà visitées
        if url in self.visited_urls:
            return False
            
        # Vérifie le format de l'URL
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
        except:
            return False
            
        # Ignore les URLs de certains types de fichiers
        extensions_to_ignore = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.exe', '.mp3', '.mp4', '.avi']
        if any(url.lower().endswith(ext) for ext in extensions_to_ignore):
            return False
            
        # Ignore les URLs provenant de domaines non désirables
        domains_to_ignore = ['facebook.com', 'twitter.com', 'instagram.com', 'youtube.com', 'amazon.com', 'netflix.com']
        if any(domain in url.lower() for domain in domains_to_ignore):
            return False
            
        return True
    
    def _clean_text(self, text):
        """Nettoie le texte extrait des pages web"""
        # Supprime les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        # Supprime les caractères spéciaux
        text = re.sub(r'[^\w\s\.,;?!-]', '', text)
        return text.strip()
    
    def _extract_text_from_page(self, soup):
        """Extrait le texte pertinent d'une page web"""
        # Supprime les scripts et les styles
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.decompose()
            
        # Obtient le texte
        text = soup.get_text()
        
        # Nettoie le texte
        text = self._clean_text(text)
        
        # Divise en paragraphes
        paragraphs = [p for p in text.split('\n') if len(p) > 50]
        
        return paragraphs
    
    def _extract_links_from_page(self, soup, base_url):
        """Extrait les liens d'une page web"""
        links = []
        
        # Trouve tous les liens dans la page
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Convertit les URLs relatives en URLs absolues
            full_url = urljoin(base_url, href)
            
            # Vérifie si l'URL est valide
            if self._is_valid_url(full_url):
                links.append(full_url)
                
        # Limite le nombre de liens pour éviter une explosion
        return links[:20]
    
    def _evaluate_interest(self, text, query=None):
        """Évalue l'intérêt potentiel d'un texte pour l'apprentissage"""
        interest_score = 0.5  # Score de base
        
        # Bonus pour les textes de longueur moyenne (ni trop courts, ni trop longs)
        text_length = len(text)
        if 100 < text_length < 1000:
            interest_score += 0.2
        elif text_length >= 1000:
            interest_score += 0.1
            
        # Bonus pour les mots-clés intéressants
        for keyword in self.interest_keywords:
            if keyword in text.lower():
                interest_score += 0.05
        
        # Si une requête spécifique est fournie, évalue la pertinence par rapport à cette requête
        if query:
            query_words = query.lower().split()
            matched_words = 0
            
            # Compte combien de mots de la requête se trouvent dans le texte
            for word in query_words:
                if len(word) > 3 and word in text.lower():  # Ignore les mots très courts
                    matched_words += 1
            
            # Calcul du ratio de correspondance
            if query_words:
                match_ratio = matched_words / len(query_words)
                # Bonus substantiel pour les textes pertinents à la requête
                interest_score += match_ratio * 0.5
                
        # Plafonne à 1.0
        return min(interest_score, 1.0)
    
    def explore_web(self, max_pages=None, query=None):
        """
        Explore le web de manière autonome
        - max_pages: nombre maximum de pages à explorer
        - query: requête spécifique pour évaluer la pertinence du contenu
        """
        if max_pages is None:
            max_pages = self.max_pages_per_session
            
        pages_explored = 0
        
        while pages_explored < max_pages and self.url_queue:
            # Sélectionne une URL dans la queue (privilégie les URLs spéciales pour les recherches)
            if query and any("search" in url.lower() for url in self.url_queue):
                # Pour une recherche spécifique, priorise les URLs contenant "search"
                url_indices = [i for i, u in enumerate(self.url_queue) if "search" in u.lower()]
                url_idx = url_indices[0] if url_indices else random.randint(0, len(self.url_queue) - 1)
            else:
                # Sélection aléatoire standard
                url_idx = random.randint(0, len(self.url_queue) - 1)
                
            url = self.url_queue.pop(url_idx)
            
            try:
                # Marque l'URL comme visitée
                self.visited_urls.add(url)
                
                # Télécharge la page
                print(f"Exploration de {url}")
                response = requests.get(url, headers=self.headers, timeout=10)
                
                # Vérifie si la requête a réussi
                if response.status_code != 200:
                    print(f"Échec: statut HTTP {response.status_code}")
                    continue
                    
                # Parse la page
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Titre de la page (pour le contexte de mémorisation)
                page_title = soup.title.text if soup.title else url
                
                # Extrait le texte
                paragraphs = self._extract_text_from_page(soup)
                
                # Extrait les liens pour l'exploration future
                new_links = self._extract_links_from_page(soup, url)
                
                # Ajoute les nouveaux liens à la queue
                for link in new_links:
                    if link not in self.visited_urls and link not in self.url_queue:
                        self.url_queue.append(link)
                        
                # Limite la taille de la queue
                if len(self.url_queue) > self.max_url_queue_size:
                    self.url_queue = self.url_queue[:self.max_url_queue_size]
                
                # Apprend à partir des paragraphes intéressants
                learned_count = 0
                highest_interest = 0
                most_interesting_paragraph = ""
                
                for paragraph in paragraphs:
                    # Ignore les paragraphes trop courts
                    if len(paragraph) < 50:
                        continue
                        
                    # Évalue l'intérêt en tenant compte de la requête le cas échéant
                    interest = self._evaluate_interest(paragraph, query)
                    
                    # Garde trace du paragraphe le plus intéressant
                    if interest > highest_interest:
                        highest_interest = interest
                        most_interesting_paragraph = paragraph
                    
                    # Si le texte est intéressant, apprend de celui-ci
                    if interest > 0.6:
                        self.learning_system.learn_from_exploration(paragraph)
                        
                        # Stocke également dans la mémoire avec métadonnées
                        metadata = {
                            'source': url,
                            'page_title': page_title,
                            'type': 'web_content',
                            'query': query if query else 'exploration_générale'
                        }
                        
                        # Une importance plus élevée pour les contenus très pertinents
                        importance = min(0.9, interest + 0.1)
                        
                        # Mémorise le contenu découvert
                        self.learning_system.memory_system.add_memory(
                            content=paragraph,
                            metadata=metadata,
                            importance=importance
                        )
                        
                        learned_count += 1
                        
                        # Limite l'apprentissage à quelques paragraphes par page
                        if learned_count >= 5:  # Augmenté pour capturer plus d'informations
                            break
                
                # Si aucun paragraphe n'était suffisamment intéressant mais qu'on avait une requête,
                # mémorise quand même le plus intéressant pour ne pas perdre d'information
                if learned_count == 0 and query and most_interesting_paragraph:
                    metadata = {
                        'source': url,
                        'page_title': page_title,
                        'type': 'web_content_fallback',
                        'query': query
                    }
                    
                    self.learning_system.memory_system.add_memory(
                        content=most_interesting_paragraph,
                        metadata=metadata,
                        importance=0.5  # Importance moyenne pour les contenus de secours
                    )
                    learned_count = 1
                
                # Enregistre l'exploration
                self.exploration_history.append({
                    'url': url,
                    'timestamp': datetime.now().isoformat(),
                    'paragraphs_count': len(paragraphs),
                    'learned_paragraphs': learned_count,
                    'new_links_found': len(new_links),
                    'query': query if query else None
                })
                
                pages_explored += 1
                
                # Pause pour ne pas surcharger les serveurs web
                time.sleep(self.min_delay_between_requests)
                
            except Exception as e:
                print(f"Erreur lors de l'exploration de {url}: {str(e)}")
                continue
                
        return pages_explored
    
    def add_url_to_explore(self, url):
        """Ajoute une URL à la queue d'exploration"""
        if self._is_valid_url(url) and url not in self.url_queue:
            self.url_queue.append(url)
            return True
        return False
    
    def get_exploration_stats(self):
        """Retourne des statistiques sur l'exploration web"""
        stats = {
            'urls_visited': len(self.visited_urls),
            'urls_in_queue': len(self.url_queue),
            'exploration_history': len(self.exploration_history)
        }
        
        # Ajoute les 5 dernières explorations
        if self.exploration_history:
            stats['recent_explorations'] = self.exploration_history[-5:]
            
        return stats
    
    def save_explorer_state(self, path="explorer_state.json"):
        """Sauvegarde l'état de l'explorateur web"""
        state = {
            'visited_urls': list(self.visited_urls),
            'url_queue': self.url_queue,
            'exploration_history': self.exploration_history[-100:],  # Seulement les 100 derniers
            'max_pages_per_session': self.max_pages_per_session,
            'min_delay_between_requests': self.min_delay_between_requests,
            'max_url_queue_size': self.max_url_queue_size,
            'interest_keywords': self.interest_keywords
        }
        
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
            
        print(f"État de l'explorateur web sauvegardé dans {path}")
    
    def load_explorer_state(self, path="explorer_state.json"):
        """Charge l'état de l'explorateur web"""
        if os.path.exists(path):
            with open(path, 'r') as f:
                state = json.load(f)
                
            self.visited_urls = set(state['visited_urls'])
            self.url_queue = state['url_queue']
            self.exploration_history = state['exploration_history']
            self.max_pages_per_session = state['max_pages_per_session']
            self.min_delay_between_requests = state['min_delay_between_requests']
            self.max_url_queue_size = state['max_url_queue_size']
            self.interest_keywords = state['interest_keywords']
            
            print(f"État de l'explorateur web chargé depuis {path}")
            return True
        else:
            print(f"Aucun état d'explorateur web trouvé à {path}")
            return False
