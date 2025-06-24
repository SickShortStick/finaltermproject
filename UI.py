import sys, shutil, os
from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QPushButton,
    QGridLayout, QVBoxLayout, QApplication,
    QHBoxLayout, QStackedWidget, QMainWindow,
    QLabel
)

app = QApplication(sys.argv)

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-image: url('Assets/Intro.jpg'); background-repeat: no-repeat; background-position: center;")
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 800, 600)

        self.show()

class AddContactDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Contact")
        self.setGeometry(200, 200, 400, 300)

        self.form_layout = QFormLayout(self)

        self.username_field = QLineEdit(self)
        self.phone_field = QLineEdit(self)

        self.form_layout.addRow("Username:", self.username_field)
        self.form_layout.addRow("Phone:", self.phone_field)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.form_layout.addWidget(self.button_box)
        self.setLayout(self.form_layout)

class SettingsDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 400, 300)

        self.form_layout = QFormLayout(self)

        self.username_field = QLineEdit(self)
        self.phone_field = QLineEdit(self)

        self.new_password_field = QLineEdit(self)
        self.new_password_field.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirm_password_field = QLineEdit(self)
        self.confirm_password_field.setEchoMode(QLineEdit.EchoMode.Password)

        self.change_profile_picture_button = QPushButton("Change Profile Picture", self)

        self.form_layout.addRow("Username:", self.username_field)
        self.form_layout.addRow("Phone:", self.phone_field)
        self.form_layout.addRow("New Password:", self.new_password_field)
        self.form_layout.addRow("Confirm Password:", self.confirm_password_field)
        self.form_layout.addRow(self.change_profile_picture_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.form_layout.addWidget(self.button_box)
        self.setLayout(self.form_layout)

class SignInPage(QWidget):

    def __init__(self):
        super().__init__()

        self.show()
        self.setWindowTitle("Sign In Page")
        
        self.vbox_layout = QVBoxLayout(self)
        self.vbox_layout.setContentsMargins(100, 100, 100, 100)

        self.buttons_layout = QHBoxLayout()

        self.username_field = QLineEdit(self)
        self.username_field.setPlaceholderText("Username")

        self.password_field = QLineEdit(self)
        self.password_field.setPlaceholderText("Password")
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)

        self.sign_in_button = QPushButton("Sign In", self)

        self.go_to_signup_button = QPushButton("Go to Sign Up", self)
        self.go_to_signup_button.clicked.connect(lambda: main_window.setCentralWidget(SignUpPage()))

        self.buttons_layout.addWidget(self.sign_in_button)
        self.buttons_layout.addWidget(self.go_to_signup_button)

        self.vbox_layout.addWidget(self.username_field)
        self.vbox_layout.addWidget(self.password_field)

        self.vbox_layout.addLayout(self.buttons_layout)

class SignUpPage(QWidget):

    def __init__(self):
        super().__init__()

        self.show()
        self.setWindowTitle("Sign Up Page")
        
        self.vbox_layout = QVBoxLayout(self)
        self.vbox_layout.setContentsMargins(100, 100, 100, 100)

        self.buttons_layout = QHBoxLayout()

        self.phone_field = QLineEdit(self)
        self.phone_field.setPlaceholderText("Phone Number")

        self.username_field = QLineEdit(self)
        self.username_field.setPlaceholderText("Username")

        self.password_field = QLineEdit(self)
        self.password_field.setPlaceholderText("Password")
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirm_password_field = QLineEdit(self)
        self.confirm_password_field.setPlaceholderText("Confirm Password")
        self.confirm_password_field.setEchoMode(QLineEdit.EchoMode.Password)

        self.sign_up_button = QPushButton("Sign Up", self)

        self.go_to_signin_button = QPushButton("Go to Sign In", self)
        self.go_to_signin_button.clicked.connect(lambda: main_window.setCentralWidget(SignInPage()))

        self.buttons_layout.addWidget(self.sign_up_button)
        self.buttons_layout.addWidget(self.go_to_signin_button)

        self.vbox_layout.addWidget(self.phone_field)
        self.vbox_layout.addWidget(self.username_field)
        self.vbox_layout.addWidget(self.password_field)
        self.vbox_layout.addWidget(self.confirm_password_field)

        self.vbox_layout.addLayout(self.buttons_layout)

main_window = MainWindow()
main_window.setCentralWidget(SignInPage())
app.exec()