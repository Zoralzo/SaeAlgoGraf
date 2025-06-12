import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)

# Importation des applications
from controleur import Controleur as ControleurApp1
from vueArticle import vueArticle as VueApp1
from ModeleDonnees import ModeleDonnees as ModeleApp1

from ControleurApp2 import Controleur as ControleurApp2
from vueArticleApp2 import vueArticle as VueApp2
from ModeleDonneesApp2 import ModeleDonnees as ModeleApp2

# === Fenêtre de connexion ===
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label_user = QLabel("Identifiant :")
        self.input_user = QLineEdit()
        layout.addWidget(self.label_user)
        layout.addWidget(self.input_user)

        self.label_pass = QLabel("Mot de passe :")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.label_pass)
        layout.addWidget(self.input_pass)

        self.btn_login = QPushButton("Se connecter")
        self.btn_login.clicked.connect(self.check_login)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

    def check_login(self):
        user = self.input_user.text()
        password = self.input_pass.text()

        if user == "admin" and password == "1234":
            self.accept_login()
        else:
            QMessageBox.warning(self, "Erreur", "Identifiants incorrects.")

    def accept_login(self):
        self.hide()
        self.choix_window = ChoiceWindow()
        self.choix_window.show()

# === Fenêtre de choix entre Application 1 et Application 2 ===
class ChoiceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choix de l'application")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Choisissez une application à lancer :")
        layout.addWidget(self.label)

        btn_app1 = QPushButton("Application 1")
        btn_app1.clicked.connect(self.lancer_app1)
        layout.addWidget(btn_app1)

        btn_app2 = QPushButton("Application 2")
        btn_app2.clicked.connect(self.lancer_app2)
        layout.addWidget(btn_app2)

        self.setLayout(layout)

    def lancer_app1(self):
        self.hide()
        modele = ModeleApp1("annexes/liste_produits.json")
        controleur = ControleurApp1(modele)
        self.vue = VueApp1(controleur)
        self.vue.show()

    def lancer_app2(self):
        self.hide()
        modele = ModeleApp2("annexes/liste_produits.json")
        controleur = ControleurApp2(modele)
        self.vue = VueApp2(controleur)
        controleur.set_vue(self.vue)
        self.vue.showFullScreen()

# === Lancement de l'application ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
