import sys, json, os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Importation des applications
from controleur import Controleur as ControleurApp1
from vueArticle import vueArticle as VueApp1
from ModeleDonnees import ModeleDonnees as ModeleApp1

from controleurApp2 import Controleur as ControleurApp2
from vueArticleApp2 import vueArticle as VueApp2
from ModeleDonneesApp2 import ModeleDonnees as ModeleApp2

# === Chemin du fichier d'utilisateurs ===
USER_FILE = "users.json"


# === Chiffrement César ===
def caesar_encrypt(text, shift=3):
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        elif char.isdigit():
            result += chr((ord(char) - ord('0') + shift) % 10 + ord('0'))
        else:
            result += char
    return result

def caesar_decrypt(text, shift=3):
    return caesar_encrypt(text, -shift)



# === Page d'accueil (choix entre se connecter ou s'enregistrer) ===
class HomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienvenue")
        self.setMinimumSize(500, 350)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Bienvenue !")
        label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        btn_register = QPushButton("📝 S'enregistrer")
        btn_register.setFont(QFont("Arial", 16))
        btn_register.setFixedHeight(60)
        btn_register.clicked.connect(self.go_register)
        layout.addWidget(btn_register)

        btn_login = QPushButton("🔐 Se connecter")
        btn_login.setFont(QFont("Arial", 16))
        btn_login.setFixedHeight(60)
        btn_login.clicked.connect(self.go_login)
        layout.addWidget(btn_login)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: black;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #005ea3;
            }
        """)

    def go_register(self):
        self.hide()
        self.register = RegisterWindow()
        self.register.show()

    def go_login(self):
        self.hide()
        self.login = LoginWindow()
        self.login.show()

# === Fenêtre d'enregistrement ===
class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enregistrement")
        self.setMinimumSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Créer un compte")
        label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Identifiant")
        self.username.setFont(QFont("Arial", 14))
        self.username.setFixedHeight(40)
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFont(QFont("Arial", 14))
        self.password.setFixedHeight(40)
        layout.addWidget(self.password)

        btn_register = QPushButton("S'enregistrer")
        btn_register.setFont(QFont("Arial", 16))
        btn_register.setFixedHeight(50)
        btn_register.clicked.connect(self.register_user)
        layout.addWidget(btn_register)

        btn_back = QPushButton("← Retour")
        btn_back.setFont(QFont("Arial", 12))
        btn_back.setFixedHeight(40)
        btn_back.clicked.connect(self.go_back)
        layout.addWidget(btn_back)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: black;
            }
            QLineEdit {
                border: 2px solid #0078d7;
                border-radius: 8px;
                padding-left: 10px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #005ea3;
            }
        """)

    def register_user(self):
        user = self.username.text().strip()
        pwd = self.password.text().strip()

        if not user or not pwd:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return

        users = {}
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r") as f:
                users = json.load(f)

        if user in users:
            QMessageBox.warning(self, "Erreur", "Cet identifiant existe déjà.")
        else:
            encrypted_pwd = caesar_encrypt(pwd, 3)  # <-- chiffrement ici
            users[user] = encrypted_pwd
            with open(USER_FILE, "w") as f:
                json.dump(users, f)
            QMessageBox.information(self, "Succès", "Compte créé avec succès !")
            self.hide()
            self.login = LoginWindow()
            self.login.show()


    def go_back(self):
        self.hide()
        self.home = HomeWindow()
        self.home.show()

# === Fenêtre de connexion ===
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion")
        self.setMinimumSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Connexion")
        label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Identifiant")
        self.username.setFont(QFont("Arial", 14))
        self.username.setFixedHeight(40)
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFont(QFont("Arial", 14))
        self.password.setFixedHeight(40)
        layout.addWidget(self.password)

        btn_login = QPushButton("Se connecter")
        btn_login.setFont(QFont("Arial", 16))
        btn_login.setFixedHeight(50)
        btn_login.clicked.connect(self.check_login)
        layout.addWidget(btn_login)

        btn_back = QPushButton("← Retour")
        btn_back.setFont(QFont("Arial", 12))
        btn_back.setFixedHeight(40)
        btn_back.clicked.connect(self.go_back)
        layout.addWidget(btn_back)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: black;
            }
            QLineEdit {
                border: 2px solid #0078d7;
                border-radius: 8px;
                padding-left: 10px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #005ea3;
            }
        """)

    def check_login(self):
        user = self.username.text().strip()
        pwd = self.password.text().strip()

        if not os.path.exists(USER_FILE):
            QMessageBox.warning(self, "Erreur", "Aucun utilisateur enregistré.")
            return

        with open(USER_FILE, "r") as f:
            users = json.load(f)

        encrypted_pwd = users.get(user)
        if encrypted_pwd and pwd == caesar_decrypt(encrypted_pwd, 3):  # <-- déchiffrement ici
            self.hide()
            self.choix_window = ChoiceWindow()
            self.choix_window.show()
        else:
            QMessageBox.warning(self, "Erreur", "Identifiants incorrects.")


    def go_back(self):
        self.hide()
        self.home = HomeWindow()
        self.home.show()

# === Fenêtre de choix d'application ===
class ChoiceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choix de l'application")
        self.setMinimumSize(600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Bienvenue ! Choisissez une application à lancer")
        label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        btn_app1 = QPushButton("🚀 Application 1")
        btn_app1.setFont(QFont("Arial", 14))
        btn_app1.setFixedHeight(60)
        btn_app1.clicked.connect(self.lancer_app1)
        layout.addWidget(btn_app1)

        btn_app2 = QPushButton("🎯 Application 2")
        btn_app2.setFont(QFont("Arial", 14))
        btn_app2.setFixedHeight(60)
        btn_app2.clicked.connect(self.lancer_app2)
        layout.addWidget(btn_app2)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: black;
            }
            QPushButton {
                background-color: #008000;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #005500;
            }
        """)

    def retour_menu(self):
        self.show()

    def lancer_app1(self):
        self.hide()
        modele = ModeleApp1("annexes/liste_produits.json")
        controleur = ControleurApp1(modele)
        self.vue = VueApp1(controleur)

        def on_close(event):
            event.ignore()
            self.vue.hide()
            self.retour_menu()

        self.vue.closeEvent = on_close

        self.vue.show()

    def lancer_app2(self):
        self.hide()
        modele = ModeleApp2("annexes/liste_produits.json")
        controleur = ControleurApp2(modele)
        self.vue = VueApp2(controleur)
        controleur.set_vue(self.vue)

        def on_close(event):
            event.ignore()
            self.vue.hide()
            self.retour_menu()

        self.vue.closeEvent = on_close

        self.vue.showFullScreen()

# === Lancement de l'application ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec())