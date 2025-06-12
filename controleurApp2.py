from PyQt6.QtWidgets import QInputDialog, QMessageBox
import sys
from PyQt6.QtWidgets import QApplication
from ModeleDonneesApp2 import ModeleDonnees
from vueArticleApp2 import vueArticle
from PyQt6.QtWidgets import QFileDialog
import json

class Controleur:
    def __init__(self, modele):
        self.modele = modele
        self.vue = None  # Ajout d'une référence à la vue

    def set_vue(self, vue):
        self.vue = vue

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
            chemin_fichier = "produits_positions.json"
            if self.modele.exporter_positions(chemin_fichier):
                QMessageBox.information(None, "Export", "Les positions ont été exportées dans produits_positions.json")
            else:
                QMessageBox.critical(None, "Erreur", "Erreur lors de l'export")
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
        if not self.vue:
            QMessageBox.critical(None, "Erreur", "Vue non initialisée")
            return

        chemin_fichier, _ = QFileDialog.getOpenFileName(self.vue, "Importer fichier JSON", "", "Fichiers JSON (*.json)")
        if not chemin_fichier:
            return

        try:
            with open(chemin_fichier, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data:
                produit = item.get("produit")
                x = item.get("x")
                y = item.get("y")
                if produit and isinstance(x, int) and isinstance(y, int):
                    self.modele.ajouter_position(produit, x, y)

            QMessageBox.information(self.vue, "Import réussi", "Les produits ont été importés et placés sur la grille.")
            self.vue.actualiser_affichage()

        except Exception as e:
            QMessageBox.critical(self.vue, "Erreur import", f"Erreur lors de l'import du fichier JSON :\n{e}")

        
    def importer_liste_txt(self):
        if not self.vue:
            QMessageBox.critical(None, "Erreur", "Vue non initialisée")
            return

        chemin_fichier, _ = QFileDialog.getOpenFileName(self.vue, "Importer fichier texte", "", "Fichiers texte (*.txt)")
        if not chemin_fichier:
            return

        try:
            with open(chemin_fichier, "r", encoding="utf-8") as f:
                lignes = f.read().splitlines()

            # Nettoyer les lignes et supprimer les vides
            produits = [ligne.strip() for ligne in lignes if ligne.strip()]
            
            if produits:
                self.rechercher_produits(produits)
                QMessageBox.information(self.vue, "Import réussi", f"{len(produits)} produits ont été importés depuis le fichier texte.")
            else:
                QMessageBox.warning(self.vue, "Avertissement", "Le fichier texte est vide ou ne contient pas de données valides.")

        except Exception as e:
            QMessageBox.critical(self.vue, "Erreur import", f"Erreur lors de l'import du fichier texte :\n{e}")

    def rechercher_produits(self, produits):
        """Recherche les produits dans le modèle et affiche leurs positions"""
        if not produits:
            QMessageBox.warning(self.vue, "Avertissement", "Aucun produit à rechercher.")
            return

        resultats = []
        for produit in produits:
            # Recherche dans les positions existantes
            for pos in self.modele.positions:
                if pos["id"].lower() == produit.lower():
                    resultats.append(f"{pos['id']} trouvé en ({pos['x']}, {pos['y']})")
            
            # Si non trouvé, vérifier si le produit existe dans le catalogue
            produit_existe = any(p["id"].lower() == produit.lower() for p in self.modele.produits)
            if not produit_existe:
                resultats.append(f"{produit} non trouvé dans le catalogue")

        if resultats:
            message = "\n".join(resultats)
            QMessageBox.information(self.vue, "Résultats de recherche", message)
        else:
            QMessageBox.information(self.vue, "Résultats", "Aucun produit trouvé.")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    modele = ModeleDonnees("annexes/liste_produits.json")
    controleur = Controleur(modele)
    fenetre = vueArticle(controleur)
    controleur.set_vue(fenetre)  # Lier la vue au contrôleur
    fenetre.showFullScreen()

    sys.exit(app.exec())