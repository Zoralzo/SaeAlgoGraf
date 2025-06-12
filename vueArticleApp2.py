from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QGraphicsView, QGraphicsScene, QLabel, QSlider
)
from PyQt6.QtGui import QPixmap, QFont, QPen, QColor
from PyQt6.QtCore import Qt, QRectF

class vueArticle(QWidget):
    def __init__(self, controleur):
        super().__init__()
        self.controleur = controleur
        self.setWindowTitle("Recherche dans le magasin")
        self.resize(900, 700)

        self.taille_cellule = 40
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.plan_item = None

        # Barre de zoom
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setMinimum(10)   # 10% zoom min
        self.slider_zoom.setMaximum(400)  # 400% zoom max
        self.slider_zoom.setValue(100)    # zoom initial 100%
        self.slider_zoom.setTickInterval(10)
        self.slider_zoom.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_zoom.valueChanged.connect(self.ajuster_zoom)

        # Composants 
        self.liste_recherche_bar = QLineEdit()
        self.liste_recherche_bar.setPlaceholderText("Entrez des produits séparés par des virgules")
        self.liste_recherche_bar.setMinimumHeight(40)
        self.liste_recherche_bar.setFont(QFont("Arial", 12))

        bouton_rechercher = QPushButton("Rechercher")
        bouton_recherche_positions = QPushButton("Positions libres")
        bouton_importer_magasin = QPushButton("Importer Magasin JSON")
        bouton_importer_liste = QPushButton("Importer Liste .txt")
        bouton_quitter = QPushButton("Quitter")

        for bouton in [bouton_rechercher, bouton_recherche_positions, bouton_importer_magasin, bouton_importer_liste, bouton_quitter]:
            bouton.setMinimumHeight(40)
            bouton.setFont(QFont("Arial", 12))

        bouton_rechercher.clicked.connect(self.rechercher)
        bouton_recherche_positions.clicked.connect(self.controleur.rechercher_positions_libres)
        bouton_importer_magasin.clicked.connect(self.controleur.importer_magasin_json)
        bouton_importer_liste.clicked.connect(self.controleur.importer_liste_txt)
        bouton_quitter.clicked.connect(self.close)

        # Layout 
        layout_principal = QVBoxLayout()

        barre_layout = QHBoxLayout()
        barre_layout.addWidget(QLabel("Produits à rechercher :"))
        barre_layout.addWidget(self.liste_recherche_bar)

        boutons_layout = QHBoxLayout()
        boutons_layout.addWidget(bouton_importer_magasin)
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
                # Vérifie s'il y a un produit à ces coordonnées
                produits = self.controleur.get_produits_coordonne(x, y)

                if produits:
                    # Bordure rouge et épaisse
                    pen = QPen(QColor("black"))
                    pen.setWidth(10)
                else:
                    # Bordure noire classique
                    pen = QPen(QColor(0, 0, 0))
                    pen.setWidth(1)

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
        if produits:
            self.controleur.rechercher_produits(produits)

    def actualiser_affichage(self):
        """Actualise l'affichage après un import"""
        self.dessiner_grille()
        if self.plan_item:
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        else:
            print("Aucun plan à afficher.")
