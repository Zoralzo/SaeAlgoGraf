# supermarche/controleur.py
from PyQt6.QtWidgets import QInputDialog, QMessageBox

# -----------------------------------------------------------------------------
# --- class controleur
# -----------------------------------------------------------------------------


class Controleur:
    def __init__(self, modele):
        self.modele = modele

    def ajouter_produit_coordonne(self, x, y):
        # Demande à l'utilisateur de choisir une catégorie
        categories = self.modele.get_categories()
        categorie, ok = QInputDialog.getItem(None, "Choisir une catégorie", "Catégorie :", categories, 0, False)
        if not ok or not categorie:
            return

        # Choisir un produit dans la catégorie
        produits = self.modele.get_produits_par_categorie(categorie)
        produit, ok = QInputDialog.getItem(None, "Choisir un produit", "Produit :", produits, 0, False)
        if not ok or not produit:
            return

        self.modele.ajouter_position(produit, x, y)
        print(f"Produit ajouté : {produit} en ({x}, {y})")

    def exporter_positions(self):
        self.modele.exporter_positions()
        QMessageBox.information(None, "Export", "Les positions ont été exportées dans produits_positions.json")
