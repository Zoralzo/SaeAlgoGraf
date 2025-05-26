import os
import sys
import json

# -----------------------------------------------------------------------------
# --- class Article
# -----------------------------------------------------------------------------

class Article :
    def __init__(self) -> None :
        
        self.__listeArticles : list[str] = [] 
        self.__fichier = "annexes/articles.json"
