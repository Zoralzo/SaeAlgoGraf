from PyQt6.QtWidgets import QInputDialog, QMessageBox
import sys
from PyQt6.QtWidgets import QApplication
from ModeleDonneesApp2 import ModeleDonnees
from vueArticleApp2 import vueArticle
from PyQt6.QtWidgets import QFileDialog
import json

# -------------------------------------------------------------------------------
# --- class Controleur
# -------------------------------------------------------------------------------

class Controleur:
    def __init__(self, modele):
        self.modele = modele

    def ajouter_produit_coordonne(self, x, y):
        categories = self.modele.get_categories()
        if not categories:
            QMessageBox.warning(None, "Attention", "Aucune catégorie disponible.")
            return

        categorie, ok = QInputDialog.getItem(None, "Choisir une catégorie", "Catégorie :", categories, 0, False)
        if not ok or not categorie:
            return

        produits = self.modele.get_produits_par_categorie(categorie)
        if not produits:
            QMessageBox.warning(None, "Attention", "Aucun produit dans cette catégorie.")
            return

        produit, ok = QInputDialog.getItem(None, "Choisir un produit", "Produit :", produits, 0, False)
        if not ok or not produit:
            return

        self.modele.ajouter_position(produit, x, y)
        print(f"Produit ajouté : {produit} en ({x}, {y})")

    def exporter_positions(self):
        try:
            self.modele.exporter_positions()
            QMessageBox.information(None, "Export", "Les positions ont été exportées dans produits_positions.json")
        except Exception as e:
            QMessageBox.critical(None, "Erreur", f"Erreur lors de l'export :\n{e}")

    def get_produits_coordonne(self, x, y):
        return self.modele.get_produits_coordonne(x, y)

    def supprimer_produit_coordonne(self, produit, x, y):
        self.modele.supprimer_produit_coordonne(produit, x, y)

    def vider_case(self, x, y):
        self.modele.vider_case(x, y)

    def est_position_valide(self, x, y):
        return self.modele.est_position_valide(x, y)
    
    def importer_magasin_json(self):
        # Ouvrir une fenêtre de dialogue pour choisir un fichier JSON
        chemin_fichier, _ = QFileDialog.getOpenFileName(self.vue, "Importer fichier JSON", "", "Fichiers JSON (*.json)")
        if not chemin_fichier:
            return  # L'utilisateur a annulé

        try:
            with open(chemin_fichier, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Supposons que data soit un dictionnaire avec les infos du magasin
            self.modele.charger_magasin(data)  # méthode à définir dans le modèle pour traiter les données

            QMessageBox.information(self.vue, "Import réussi", "Le magasin a bien été importé depuis le fichier JSON.")
            
            # Actualiser la vue si nécessaire
            self.vue.actualiser_affichage()

        except Exception as e:
            QMessageBox.critical(self.vue, "Erreur import", f"Erreur lors de l'import du fichier JSON :\n{e}")
        
        
    def importer_liste_txt(self):
        chemin_fichier, _ = QFileDialog.getOpenFileName(self.vue, "Importer fichier texte", "", "Fichiers texte (*.txt)")
        if not chemin_fichier:
            return

        try:
            with open(chemin_fichier, "r", encoding="utf-8") as f:
                lignes = f.read().splitlines()

            # Supposons que tu veux stocker cette liste dans ton modèle
            self.modele.charger_liste(lignes)  # méthode à définir dans ton modèle

            QMessageBox.information(self.vue, "Import réussi", "La liste a bien été importée depuis le fichier texte.")
            self.vue.actualiser_affichage()

        except Exception as e:
            QMessageBox.critical(self.vue, "Erreur import", f"Erreur lors de l'import du fichier texte :\n{e}")

# -------------------------------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)

    modele = ModeleDonnees("annexes/liste_produits.json")
    controleur = Controleur(modele)
    fenetre = vueArticle(controleur)
    fenetre.showFullScreen()

    sys.exit(app.exec())
