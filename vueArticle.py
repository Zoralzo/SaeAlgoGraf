import os
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QGraphicsPixmapItem, QWidget, QGraphicsView, QGraphicsScene,
    QVBoxLayout, QPushButton, QSlider, QHBoxLayout, QListWidget,
    QLabel, QMessageBox, QLineEdit
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QApplication
# -----------------------------------------------------------------------------
# --- class VueArticle
# -----------------------------------------------------------------------------

class vueArticle(QWidget):
    def __init__(self, controleur):
        super().__init__()
        self.setWindowTitle("Plan du supermarché")
        self.controleur = controleur

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        chemin_image = os.path.join(os.path.dirname(__file__), "annexes", "plan.jpg")
        pixmap = QPixmap(chemin_image)

        if pixmap.isNull():
            print(" Erreur : plan.jpg introuvable à", chemin_image)
            pixmap = QPixmap(800, 600)
            pixmap.fill(Qt.GlobalColor.lightGray)

        self.plan_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.plan_item)

        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setMouseTracking(True)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setMinimum(1)
        self.slider_zoom.setMaximum(300)
        self.slider_zoom.setValue(100)
        self.slider_zoom.valueChanged.connect(self.zoom_changed)

        self.bouton_valider = QPushButton("Valider")
        self.bouton_quitter = QPushButton("Quitter l'application")
        self.bouton_quitter.clicked.connect(self.quitter_application)
        self.bouton_valider.clicked.connect(self.controleur.exporter_positions)

        # Zone latérale
        self.liste_produits_case = QListWidget()

        # --- Barre de recherche ---
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Rechercher un produit...")
        self.search_bar.textChanged.connect(self.filtrer_produits)
        self.texte_filtre = ""

        self.bouton_ajouter = QPushButton("Ajouter un produit")
        self.bouton_supprimer = QPushButton("Supprimer le produit sélectionné")
        self.bouton_vider = QPushButton("Vider la case")

        self.bouton_ajouter.clicked.connect(self.ajouter_produit_case)
        self.bouton_supprimer.clicked.connect(self.supprimer_produit_case)
        self.bouton_vider.clicked.connect(self.vider_case)

        layout_droit = QVBoxLayout()
        layout_droit.addWidget(QLabel("Contenu de la case"))
        layout_droit.addWidget(self.search_bar)
        layout_droit.addWidget(self.liste_produits_case)
        layout_droit.addWidget(self.bouton_ajouter)
        layout_droit.addWidget(self.bouton_supprimer)
        layout_droit.addWidget(self.bouton_vider)
        layout_droit.addWidget(self.bouton_quitter)
        layout_droit.addStretch()
        layout_droit.addWidget(self.bouton_valider)

        layout_gauche = QVBoxLayout()
        layout_gauche.addWidget(self.view)
        layout_gauche.addWidget(self.slider_zoom)

        layout_principal = QHBoxLayout()
        layout_principal.addLayout(layout_gauche)
        layout_principal.addLayout(layout_droit)

        self.setLayout(layout_principal)
        self.showFullScreen()

        self.taille_cellule = 50
        self.rectangles_colores = {}  # Pour fond jaune sur cases avec produit
        self.rect_selection = None  # Pour bordure noire sur case sélectionnée
        self.dessiner_grille()

        self.view.viewport().installEventFilter(self)

        self.x_selection = None
        self.y_selection = None

        # On colore directement les cases avec produits
        self.mettre_a_jour_couleurs_cases()

    def dessiner_grille(self):
        """
        Dessine la grille sur la carte
        """
        grille_color = QColor(0, 0, 0)
        pen = QPen(grille_color)
        pen.setWidth(1)
        largeur = self.plan_item.pixmap().width()
        hauteur = self.plan_item.pixmap().height()

        for x in range(0, largeur, self.taille_cellule):
            self.scene.addLine(x, 0, x, hauteur, pen)
        for y in range(0, hauteur, self.taille_cellule):
            self.scene.addLine(0, y, largeur, y, pen)

    def zoom_changed(self, value):
        """
        Créer un zoom sur la carte
        """
        scale_factor = value / 100
        self.view.resetTransform()
        self.view.scale(scale_factor, scale_factor)

    def eventFilter(self, source, event):
        """
        Verifie la position du clique si il est valide ou non
        """
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            position = self.view.mapToScene(event.position().toPoint())
            x = int(position.x()) // self.taille_cellule
            y = int(position.y()) // self.taille_cellule

            if not self.controleur.est_position_valide(x, y):
                QMessageBox.warning(self, "Hors rayon", "Vous ne cliquez pas dans un rayon.")
                return True

            self.x_selection = x
            self.y_selection = y
            print(f"Case sélectionnée : x={self.x_selection}, y={self.y_selection}")
            self.mettre_a_jour_liste_produits()
            self.mettre_a_jour_bordure_selection()

        elif event.type() == QEvent.Type.MouseMove:
            position = self.view.mapToScene(event.position().toPoint())
            x = int(position.x()) // self.taille_cellule
            y = int(position.y()) // self.taille_cellule

            if self.controleur.est_position_valide(x, y):
                self.view.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                self.view.viewport().setCursor(Qt.CursorShape.ForbiddenCursor)

        return super().eventFilter(source, event)

    def mettre_a_jour_couleurs_cases(self):
        """
        Colore en jaune toutes les cases qui contiennent au moins un produit.
        """
        # D'abord, on enlève les anciens rectangles jaunes
        for rect_item in self.rectangles_colores.values():
            self.scene.removeItem(rect_item)
        self.rectangles_colores.clear()

        largeur = self.plan_item.pixmap().width() // self.taille_cellule
        hauteur = self.plan_item.pixmap().height() // self.taille_cellule

        for x in range(largeur):
            for y in range(hauteur):
                produits = self.controleur.get_produits_coordonne(x, y)
                if produits:
                    x_pix = x * self.taille_cellule
                    y_pix = y * self.taille_cellule
                    rect = self.scene.addRect(
                        x_pix, y_pix,
                        self.taille_cellule, self.taille_cellule,
                        pen=QPen(Qt.GlobalColor.transparent),  # Pas de bordure ici
                        brush=QColor(255, 215, 0, 100)  # Jaune transparent
                    )
                    self.rectangles_colores[(x, y)] = rect

    def mettre_a_jour_bordure_selection(self):
        """
        Met une bordure noire épaisse autour de la case sélectionnée uniquement.
        """
        # Supprime ancienne bordure si existante
        if self.rect_selection is not None:
            self.scene.removeItem(self.rect_selection)
            self.rect_selection = None

        if self.x_selection is None or self.y_selection is None:
            return

        x_pix = self.x_selection * self.taille_cellule
        y_pix = self.y_selection * self.taille_cellule

        self.rect_selection = self.scene.addRect(
            x_pix, y_pix,
            self.taille_cellule, self.taille_cellule,
            pen=QPen(QColor(0, 0, 0), 5),
            brush=Qt.GlobalColor.transparent
        )

    def mettre_a_jour_liste_produits(self):
        """
        Met à jour la liste des produits de la case sélectionnée,
        avec filtrage selon la recherche.
        """
        self.liste_produits_case.clear()
        if self.x_selection is None or self.y_selection is None:
            return

        produits = self.controleur.get_produits_coordonne(self.x_selection, self.y_selection)

        # Appliquer le filtre si texte_filtre non vide (insensible à la casse)
        if self.texte_filtre:
            produits = [p for p in produits if self.texte_filtre.lower() in p.lower()]

        self.liste_produits_case.addItems(produits)

    def filtrer_produits(self, texte):
        """
        Met à jour la liste selon le texte saisi dans la barre de recherche.
        """
        self.texte_filtre = texte
        self.mettre_a_jour_liste_produits()

    def ajouter_produit_case(self):
        """
        ajoute un article a une case
        """
        if self.x_selection is None or self.y_selection is None:
            QMessageBox.warning(self, "Erreur", "Aucune case sélectionnée")
            return
        self.controleur.ajouter_produit_coordonne(self.x_selection, self.y_selection)
        self.mettre_a_jour_couleurs_cases()
        self.mettre_a_jour_liste_produits()

    def supprimer_produit_case(self):
        """
        supprime un article a une case
        """
        if self.x_selection is None or self.y_selection is None:
            QMessageBox.warning(self, "Erreur", "Aucune case sélectionnée")
            return
        self.controleur.supprimer_produit_coordonne(self.x_selection, self.y_selection)
        self.mettre_a_jour_couleurs_cases()
        self.mettre_a_jour_liste_produits()

    def vider_case(self):
        """
        vide tous les articles d'une case
        """
        if self.x_selection is None or self.y_selection is None:
            QMessageBox.warning(self, "Erreur", "Aucune case sélectionnée")
            return
        self.controleur.vider_case(self.x_selection, self.y_selection)
        self.mettre_a_jour_couleurs_cases()
        self.mettre_a_jour_liste_produits()

    def quitter_application(self):
        """
        Quitte l'application
        """
        self.close()
