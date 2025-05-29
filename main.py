import sys
from PyQt6.QtWidgets import QApplication
from ModeleDonnees import ModeleDonnees
from Controleur import Controleur
from vueArticle import vueArticle

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Initialisation du modèle
    modele = ModeleDonnees("annexes/liste_produits.json")

    # Création du contrôleur avec le modèle
    controleur = Controleur(modele)

    # Création de la fenêtre principale avec le contrôleur
    fenetre = vueArticle(controleur)
    fenetre.show()

    sys.exit(app.exec())

