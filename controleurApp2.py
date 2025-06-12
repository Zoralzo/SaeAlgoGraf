from PyQt6.QtWidgets import QInputDialog, QMessageBox
import sys
from PyQt6.QtWidgets import QApplication
from ModeleDonneesApp2 import *
from vueArticleApp2 import vueArticle
from PyQt6.QtWidgets import QFileDialog
from collections import deque



class Controleur:
    def __init__(self, modele):
        self.modele = modele
        self.vue = None  # Ajout d'une référence à la vue
        self.charger_positions_par_defaut("produits_positions.json")

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
    
    def charger_positions_par_defaut(self, chemin_fichier):
        import json
        try:
            with open(chemin_fichier, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data:
                produit = item.get("produit")
                x = item.get("x")
                y = item.get("y")
                if produit and isinstance(x, int) and isinstance(y, int):
                    self.modele.ajouter_position(produit, x, y)

            print(f"{len(data)} produits chargés depuis {chemin_fichier}.")
        except FileNotFoundError:
            print(f"Fichier {chemin_fichier} non trouvé. Aucun produit chargé.")
        except Exception as e:
            print(f"Erreur lors du chargement initial des positions : {e}")

        
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
            
        

    def trouver_plus_court_chemin_contraint(self, depart, arrivees, chemin_dispo):
        from collections import deque

        queue = deque()
        queue.append((depart, [depart]))
        visited = set()
        visited.add(depart)

        while queue:
            current, path = queue.popleft()

            if current in arrivees:
                return path

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                voisin = (current[0] + dx, current[1] + dy)
                if voisin in chemin_dispo and voisin not in visited:
                    visited.add(voisin)
                    queue.append((voisin, path + [voisin]))

        return None




    def rechercher_chemin_produits(self, positions_produits):
        depart = (45, 42)
        arrivees = [(15, 42), (17, 42), (19, 42), (20, 42), (22, 42),
                    (25, 42), (27, 42), (29, 42), (31, 42), (32, 42),
                    (34, 42), (36, 42), (37, 42)]

        if not positions_produits:
            return

        chemin_dispo = self.get_chemin_dispo(self.modele.caseUiliser())



        chemin_total = []
        position_actuelle = depart
        cases_utilisées = set()

        for destination in positions_produits:
            chemin = self.trouver_plus_court_chemin_contraint(
                position_actuelle,
                {destination},
                set(chemin_dispo) - set(cases_utilisées)
            )
            if chemin:
                chemin_total.extend(chemin[1:])  # éviter de répéter le dernier point
                position_actuelle = destination
                cases_utilisées.update(chemin)
            else:
                print(f"Pas de chemin possible vers {destination}")

        # Aller à une des 14 arrivées
        chemin_final = self.trouver_plus_court_chemin_contraint(position_actuelle, set(arrivees), set(chemin_dispo) - set(cases_utilisées))


        if chemin_final:
            chemin_total.extend(chemin_final[1:])
            self.vue.afficher_chemin(chemin_total)
        else:
            QMessageBox.warning(self.vue, "Chemin impossible", "Aucune arrivée valide atteignable.")

    
    def rechercher_produits(self, produits):
        """Recherche les produits dans le modèle et affiche leurs positions + le chemin"""
        if not produits:
            QMessageBox.warning(self.vue, "Avertissement", "Aucun produit à rechercher.")
            return

        resultats = []
        positions = []

        for produit in produits:
            for pos in self.modele.positions:
                if pos["id"].lower() == produit.lower():
                    resultats.append(f"{pos['id']} trouvé en ({pos['x']}, {pos['y']})")
                    positions.append((pos["x"], pos["y"]))
                    break

        if resultats:
            message = "\n".join(resultats)
            QMessageBox.information(self.vue, "Résultats de recherche", message)
            self.rechercher_chemin_produits(positions)
        else:
            QMessageBox.information(self.vue, "Résultats", "Aucun produit trouvé.")
   
    
    def rechercher_positions_libres(self):
        positions_libres = self.modele.rechercher_positions_possibles()
        if positions_libres:
            message = "\n".join(f"({x}, {y})" for x, y in positions_libres)
            QMessageBox.information(self.vue, "Positions libres", f"Positions disponibles :\n{message}")
        else:
            QMessageBox.information(self.vue, "Positions libres", "Aucune position libre disponible.")



    def get_chemin_dispo(self, cases_utilisees):
        """Retourne les cases disponibles pour le cheminement"""
        chemin_dispo = self.modele.caseUiliser()
        for x in range(0, 50):
            for y in range(0, 50):
                if (x, y) not in cases_utilisees:
                    chemin_dispo.append((x, y))
        return chemin_dispo


 



if __name__ == '__main__':
    app = QApplication(sys.argv)

    modele = ModeleDonnees("annexes/liste_produits.json")
    controleur = Controleur(modele)
    fenetre = vueArticle(controleur)
    controleur.set_vue(fenetre)  # Lier la vue au contrôleur
    fenetre.showFullScreen()

    sys.exit(app.exec())