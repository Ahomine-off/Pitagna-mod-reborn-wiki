import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTabWidget, QShortcut
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QFont, QKeySequence

class PagePersonnalisee(QWebEnginePage):
    def certificateError(self, error):
        print("⚠️ Certificat non valide ignoré :", error.errorDescription())
        return True

class Onglet(QWidget):
    def __init__(self, navigateur, url="https://localhost:4433/"):
        super().__init__()
        self.navigateur = navigateur

        # Barre d'adresse
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Entre une URL féline…")
        self.url_bar.returnPressed.connect(self.charger_page)

        # Boutons de navigation
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.revenir_en_arriere)

        self.forward_button = QPushButton("→")
        self.forward_button.clicked.connect(self.revenir_en_avant)

        self.refresh_button = QPushButton("🔄")
        self.refresh_button.clicked.connect(self.actualiser_page)

        self.go_button = QPushButton("Miaou !")
        self.go_button.clicked.connect(self.charger_page)

        # Vue Web
        self.web_view = QWebEngineView()
        self.web_view.setPage(PagePersonnalisee(self.web_view))

        # Layouts
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.refresh_button)
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.go_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.web_view)
        self.setLayout(main_layout)

        self.url_bar.setText(url)
        self.charger_page()

    def charger_page(self):
        url = self.url_bar.text().strip()
        if url.startswith("cat://"):
            url = "https://localhost:4433/"
        elif not url.startswith("http"):
            url = "http://" + url
        self.web_view.load(QUrl(url))

    def revenir_en_arriere(self):
        if self.web_view.history().canGoBack():
            self.web_view.back()

    def revenir_en_avant(self):
        if self.web_view.history().canGoForward():
            self.web_view.forward()

    def actualiser_page(self):
        self.web_view.reload()

class NavigateurFelin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐾 Navigateur Félin de Clément")
        self.setGeometry(100, 100, 1024, 768)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fef6e4;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ff6f61;
                border-radius: 10px;
                font-size: 16px;
                background-color: #fff;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #ff6f61;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff8f81;
            }
        """)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.fermer_onglet)
        self.setCentralWidget(self.tabs)

        # Bouton + pour ajouter un onglet
        self.bouton_plus = QPushButton("+")
        self.bouton_plus.clicked.connect(lambda: self.ajouter_onglet("cat://"))
        self.tabs.setCornerWidget(self.bouton_plus, Qt.TopRightCorner)

        # Raccourci clavier Ctrl+T
        shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        shortcut.activated.connect(lambda: self.ajouter_onglet("cat://"))

        self.ajouter_onglet("https://localhost:4433/")

    def ajouter_onglet(self, url):
        onglet = Onglet(self, url)
        index = self.tabs.addTab(onglet, "🐱 Onglet")
        self.tabs.setCurrentIndex(index)

    def fermer_onglet(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Comic Sans MS", 10))
    fenetre = NavigateurFelin()
    fenetre.show()
    sys.exit(app.exec_())
