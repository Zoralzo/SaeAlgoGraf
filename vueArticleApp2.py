from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QGraphicsView, QGraphicsScene, QLabel, QSlider
)
from PyQt6.QtGui import QPixmap, QFont, QPen, QColor
from PyQt6.QtCore import Qt, QRectF
from collections import deque

class vueArticle(QWidget):
    def __init__(self, controleur):
        super().__init__()
        self.controleur = controleur
        self.setWindowTitle("Recherche dans le magasin")
        self.resize(900, 700)

        self.taille_cellule = 50
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.plan_item = None

        # Barre de zoom
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setMinimum(10)
        self.slider_zoom.setMaximum(400)
        self.slider_zoom.setValue(100)
        self.slider_zoom.setTickInterval(10)
        self.slider_zoom.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_zoom.valueChanged.connect(self.ajuster_zoom)

        # Barre de recherche
        self.liste_recherche_bar = QLineEdit()
        self.liste_recherche_bar.setPlaceholderText("Entrez des produits séparés par des virgules")
        self.liste_recherche_bar.setMinimumHeight(40)
        self.liste_recherche_bar.setFont(QFont("Arial", 12))

        # Boutons
        bouton_rechercher = QPushButton("Rechercher")
        bouton_recherche_positions = QPushButton("Positions libres")
        bouton_importer_liste = QPushButton("Importer Liste .txt")
        bouton_quitter = QPushButton("Quitter")

        for bouton in [bouton_rechercher, bouton_recherche_positions, bouton_importer_liste, bouton_quitter]:
            bouton.setMinimumHeight(40)
            bouton.setFont(QFont("Arial", 12))

        bouton_rechercher.clicked.connect(self.rechercher)
        bouton_recherche_positions.clicked.connect(self.controleur.rechercher_positions_libres)
        bouton_importer_liste.clicked.connect(self.controleur.importer_liste_txt)
        bouton_quitter.clicked.connect(self.close)

        # Layouts
        layout_principal = QVBoxLayout()

        barre_layout = QHBoxLayout()
        barre_layout.addWidget(QLabel("Produits à rechercher :"))
        barre_layout.addWidget(self.liste_recherche_bar)

        boutons_layout = QHBoxLayout()
        boutons_layout.addWidget(bouton_importer_liste)
        boutons_layout.addWidget(bouton_rechercher)
        boutons_layout.addWidget(bouton_recherche_positions)
        boutons_layout.addWidget(bouton_quitter)

        layout_principal.addLayout(barre_layout)
        layout_principal.addLayout(boutons_layout)
        layout_principal.addWidget(self.view)
        layout_principal.addWidget(QLabel("Zoom :"))
        layout_principal.addWidget(self.slider_zoom)

        self.setLayout(layout_principal)
        self.dessiner_grille()

    def dessiner_grille(self):
        self.scene.clear()

        pixmap = QPixmap("annexes/plan.jpg")
        if pixmap.isNull():
            print("Image non trouvée.")
            return

        self.plan_item = self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(QRectF(pixmap.rect()))

        colonnes = pixmap.width() // self.taille_cellule
        lignes = pixmap.height() // self.taille_cellule

        for x in range(colonnes):
            for y in range(lignes):
                produits = self.controleur.get_produits_coordonne(x, y)

                pen = QPen(QColor("black")) if produits else QPen(QColor(0, 0, 0))
                pen.setWidth(10 if produits else 1)

                self.scene.addRect(
                    x * self.taille_cellule, y * self.taille_cellule,
                    self.taille_cellule, self.taille_cellule,
                    pen
                )

        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def ajuster_zoom(self, value):
        facteur = value / 100
        self.view.resetTransform()
        self.view.scale(facteur, facteur)

    def rechercher(self):
        texte = self.liste_recherche_bar.text()
        produits = [p.strip().lower() for p in texte.split(",") if p.strip()]
        self.controleur.rechercher_produits(produits)

    def actualiser_affichage(self):
        self.dessiner_grille()
        if self.plan_item:
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        else:
            print("Aucun plan à afficher.")


    def afficher_chemin(self, chemin):
        self.dessiner_grille()

        if not chemin:
            return

        # Départ (bleu)
        depart = chemin[0]
        rect = self.scene.addRect(
            depart[0] * self.taille_cellule,
            depart[1] * self.taille_cellule,
            self.taille_cellule,
            self.taille_cellule,
            QPen(QColor("blue"), 2)
        )
        rect.setBrush(QColor(0, 0, 255, 150))

        # Chemin intermédiaire (dégradé jaune -> vert)
        nb_etapes = len(chemin)
        for i, (x, y) in enumerate(chemin[1:-1], start=1):
            ratio = i / nb_etapes
            rouge = int(255 * (1 - ratio))
            vert = int(255 * ratio)
            couleur = QColor(rouge, vert, 0, 180)

            rect = self.scene.addRect(
                x * self.taille_cellule,
                y * self.taille_cellule,
                self.taille_cellule,
                self.taille_cellule,
                QPen(Qt.GlobalColor.transparent)
            )
            rect.setBrush(couleur)

            # Numéro d’étape (facultatif mais sympa)
            texte = self.scene.addText(str(i))
            texte.setDefaultTextColor(Qt.GlobalColor.black)
            texte.setFont(QFont("Arial", 8))
            texte.setPos(x * self.taille_cellule + 5, y * self.taille_cellule + 5)

        # Arrivée (rouge)
        arrivee = chemin[-1]
        rect = self.scene.addRect(
            arrivee[0] * self.taille_cellule,
            arrivee[1] * self.taille_cellule,
            self.taille_cellule,
            self.taille_cellule,
            QPen(QColor("red"), 2)
        )
        rect.setBrush(QColor(255, 0, 0, 150))


    def rechercher_chemin_produits(self, produits):
        depart = self.get_coord_depart()  # (x, y)
        arrivees = self.get_coord_arrivees()  # Liste de 14 coordonnées possibles
        accessibles = set(self.get_chemin_dispo())  # Toutes les cases autorisées

        # Fonction de voisinage (haut, bas, gauche, droite)
        def voisins(coord):
            x, y = coord
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            return [(x + dx, y + dy) for dx, dy in directions if (x + dx, y + dy) in accessibles]

        visited = set()
        queue = deque([(depart, [depart])])
        visited.add(depart)

        while queue:
            courant, chemin = queue.popleft()

            if courant in arrivees:
                self.vue.afficher_chemin(chemin)
                return

            for voisin in voisins(courant):
                if voisin not in visited:
                    visited.add(voisin)
                    queue.append((voisin, chemin + [voisin]))

        print("Aucun chemin trouvé.")

