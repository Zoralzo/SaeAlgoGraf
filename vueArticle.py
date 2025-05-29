import os
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem
from PyQt6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QPushButton, QSlider
from PyQt6.QtCore import Qt, QPointF, QEvent
from PyQt6.QtGui import QPainter, QColor, QPen

# -----------------------------------------------------------------------------
# --- class vue
# -----------------------------------------------------------------------------


class vueArticle(QWidget):
    def __init__(self, controleur):
        super().__init__()
        self.setWindowTitle("Plan du supermarché")
        self.controleur = controleur

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        # Chargement sécurisé de l'image plan.jpg dans le sous-dossier annexes
        chemin_image = os.path.join(os.path.dirname(__file__), "annexes", "plan.jpg")
        pixmap = QPixmap(chemin_image)

        if pixmap.isNull():
            print("⚠️ Erreur : plan.jpg introuvable à", chemin_image)
            # Optionnel : gérer le cas sans image, par exemple une image vide ou placeholder
            pixmap = QPixmap(800, 600)  # taille arbitraire
            pixmap.fill(Qt.GlobalColor.lightGray)
        
        self.plan_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.plan_item)

        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setMouseTracking(True)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # Zoom
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setMinimum(1)
        self.slider_zoom.setMaximum(300)
        self.slider_zoom.setValue(100)
        self.slider_zoom.valueChanged.connect(self.zoom_changed)

        # Bouton valider
        self.bouton_valider = QPushButton("Valider")
        self.bouton_valider.clicked.connect(self.controleur.exporter_positions)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.slider_zoom)
        layout.addWidget(self.bouton_valider)
        self.setLayout(layout)

        # Dessiner une grille de base
        self.taille_cellule = 50
        self.dessiner_grille()

        self.view.viewport().installEventFilter(self)

    def dessiner_grille(self):
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
        scale_factor = value / 100
        self.view.resetTransform()
        self.view.scale(scale_factor, scale_factor)

    def eventFilter(self, source, event):
        if event.type() == event.Type.MouseButtonPress and event.buttons() == Qt.MouseButton.LeftButton:
            position = self.view.mapToScene(event.position().toPoint())
            x = int(position.x()) // self.taille_cellule
            y = int(position.y()) // self.taille_cellule
            print(f"Zone sélectionnée : x={x}, y={y}")
            self.controleur.ajouter_produit_coordonne(x, y)
        return super().eventFilter(source, event)
