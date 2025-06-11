import os
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QGraphicsPixmapItem, QWidget, QGraphicsView, QGraphicsScene,
    QVBoxLayout, QPushButton, QSlider, QHBoxLayout, QListWidget,
    QLabel, QMessageBox
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
        self.bouton_ajouter = QPushButton("Ajouter un produit")
        self.bouton_supprimer = QPushButton("Supprimer le produit sélectionné")
        self.bouton_vider = QPushButton("Vider la case")

        self.bouton_ajouter.clicked.connect(self.ajouter_produit_case)
        self.bouton_supprimer.clicked.connect(self.supprimer_produit_case)
        self.bouton_vider.clicked.connect(self.vider_case)

        layout_droit = QVBoxLayout()
        layout_droit.addWidget(QLabel("Contenu de la case"))
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
        self.dessiner_grille()

        self.view.viewport().installEventFilter(self)

        self.x_selection = None
        self.y_selection = None

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

        elif event.type() == QEvent.Type.MouseMove:
            position = self.view.mapToScene(event.position().toPoint())
            x = int(position.x()) // self.taille_cellule
            y = int(position.y()) // self.taille_cellule

            if self.controleur.est_position_valide(x, y):
                self.view.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                self.view.viewport().setCursor(Qt.CursorShape.ForbiddenCursor)

        return super().eventFilter(source, event)



    def mettre_a_jour_liste_produits(self):
        """
        donne les articles d'une case
        """
        self.liste_produits_case.clear()
        if self.x_selection is None or self.y_selection is None:
            return
        produits = self.controleur.get_produits_coordonne(self.x_selection, self.y_selection)
        self.liste_produits_case.addItems(produits)

    def ajouter_produit_case(self):
        """
        ajoute un article a une case
        """
        if self.x_selection is None or self.y_selection is None:
            QMessageBox.warning(self, "Erreur", "Aucune case sélectionnée")
            return
        self.controleur.ajouter_produit_coordonne(self.x_selection, self.y_selection)
        self.mettre_a_jour_liste_produits()

    def supprimer_produit_case(self):
        """
        supprime article d'une case
        """
        selected = self.liste_produits_case.currentItem()
        if selected:
            produit = selected.text()
            self.controleur.supprimer_produit_coordonne(produit, self.x_selection, self.y_selection)
            self.mettre_a_jour_liste_produits()

    def vider_case(self):
        """
        Vide articles d'une case
        """
        self.controleur.vider_case(self.x_selection, self.y_selection)
        self.mettre_a_jour_liste_produits()

    def quitter_application(self):
        reponse = QMessageBox.question(
            self,
            "Quitter",
            "Voulez-vous vraiment quitter l'application ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reponse == QMessageBox.StandardButton.Yes:
            QApplication.quit()
