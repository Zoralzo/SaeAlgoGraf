from PyQt6.QtWidgets import QInputDialog, QMessageBox
import sys
from PyQt6.QtWidgets import QApplication
from ModeleDonnees import ModeleDonnees
from vueArticle import vueArticle

# -----------------------------------------------------------------------------
# --- class Controleur
# -----------------------------------------------------------------------------

class Controleur:
    def __init__(self, modele):
        self.modele = modele

    def ajouter_produit_coordonne(self, x, y):
        categories = self.modele.get_categories()
        categorie, ok = QInputDialog.getItem(None, "Choisir une catégorie", "Catégorie :", categories, 0, False)
        if not ok or not categorie:
            return

        produits = self.modele.get_produits_par_categorie(categorie)
        produit, ok = QInputDialog.getItem(None, "Choisir un produit", "Produit :", produits, 0, False)
        if not ok or not produit:
            return

        self.modele.ajouter_position(produit, x, y)
        print(f"Produit ajouté : {produit} en ({x}, {y})")

    def exporter_positions(self):
        self.modele.exporter_positions()
        QMessageBox.information(None, "Export", "Les positions ont été exportées dans produits_positions.json")

    def get_produits_coordonne(self, x, y):
        return self.modele.get_produits_coordonne(x, y)

    def supprimer_produit_coordonne(self, produit, x, y):
        self.modele.supprimer_produit_coordonne(produit, x, y)

    def vider_case(self, x, y):
        self.modele.vider_case(x, y)

    def est_position_valide(self, x, y):
        return self.modele.est_position_valide(x, y)

        
        

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