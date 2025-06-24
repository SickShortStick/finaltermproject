import sys, shutil, os, socket, threading
import database
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QPushButton,
    QGridLayout, QVBoxLayout, QApplication,
    QHBoxLayout, QStackedWidget, QMainWindow,
    QLabel, QMessageBox, QListWidget, QListWidgetItem 
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
        self.sign_in_button.clicked.connect(self.handle_sign_in)

        self.go_to_signup_button = QPushButton("Go to Sign Up", self)
        self.go_to_signup_button.clicked.connect(lambda: main_window.setCentralWidget(SignUpPage()))

        self.buttons_layout.addWidget(self.sign_in_button)
        self.buttons_layout.addWidget(self.go_to_signup_button)

        self.vbox_layout.addWidget(self.username_field)
        self.vbox_layout.addWidget(self.password_field)

        self.vbox_layout.addLayout(self.buttons_layout)
    
    def handle_sign_in(self):
        username = self.username_field.text().strip()
        password = self.password_field.text()

        if database.check_user(username, password):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('127.0.0.1', 12345))
                sock.send(username.encode())  # optional: identify to server
                main_window.setCentralWidget(MainChatWindow(sock, username))
            except Exception as e:
                QMessageBox.critical(self, "Connection Error", f"Could not connect to server: {e}")
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")


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
        self.sign_up_button.clicked.connect(self.handle_sign_up)

        self.go_to_signin_button = QPushButton("Go to Sign In", self)
        self.go_to_signin_button.clicked.connect(lambda: main_window.setCentralWidget(SignInPage()))

        self.buttons_layout.addWidget(self.sign_up_button)
        self.buttons_layout.addWidget(self.go_to_signin_button)

        self.vbox_layout.addWidget(self.phone_field)
        self.vbox_layout.addWidget(self.username_field)
        self.vbox_layout.addWidget(self.password_field)
        self.vbox_layout.addWidget(self.confirm_password_field)

        self.vbox_layout.addLayout(self.buttons_layout)

    def handle_sign_up(self):
        username = self.username_field.text().strip()
        phone = self.phone_field.text().strip()
        password = self.password_field.text()
        confirm = self.confirm_password_field.text()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Username and password cannot be empty.")
            return
        if password != confirm:
            QMessageBox.warning(self, "Input Error", "Passwords do not match.")
            return

        if database.add_user(username, phone, password):
            QMessageBox.information(self, "Success", "Account created successfully! Please sign in.")
            main_window.setCentralWidget(SignInPage())
        else:
            QMessageBox.warning(self, "Error", "Username already exists.")


class ChatPage(QWidget):
    def __init__(self, sock: socket.socket, username: str):
        super().__init__()
        self.sock = sock
        self.username = username

        self.layout = QVBoxLayout(self)
        self.messages_display = QListWidget()
        self.message_input = QLineEdit()
        self.send_button = QPushButton("Send")

        self.layout.addWidget(self.messages_display)
        input_row = QHBoxLayout()
        input_row.addWidget(self.message_input)
        input_row.addWidget(self.send_button)
        self.layout.addLayout(input_row)

        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

        threading.Thread(target=self.receive_loop, daemon=True).start()

    def send_message(self):
        text = self.message_input.text().strip()
        if text:
            try:
                self.sock.send(f"{self.username}: {text}".encode())
                self.message_input.clear()
            except:
                self.messages_display.addItem("⚠️ Could not send message.")

    def receive_loop(self):
        while True:
            try:
                msg = self.sock.recv(1024)
                if not msg:
                    break
                self.messages_display.addItem(msg.decode())
            except:
                break


class MainChatWindow(QWidget):
    def __init__(self, sock, username):
        super().__init__()
        self.setWindowTitle("Chat")
        self.layout = QVBoxLayout(self)
        
        # Sidebar
        self.sidebar = QVBoxLayout()
        self.profile_button = QPushButton(f"👤 {username}")
        self.settings_button = QPushButton("⚙️ Settings")
        self.sidebar.addWidget(self.profile_button)
        self.sidebar.addWidget(self.settings_button)
        
        self.chat_list_label = QLabel("Chats")
        self.chat_list = QListWidget()
        for name in ["Alice", "Bob", "Charlie"]:
            self.chat_list.addItem(name)
        
        self.sidebar.addWidget(self.chat_list_label)
        self.sidebar.addWidget(self.chat_list)
        self.sidebar.addStretch()
        
        # Chat area
        self.chat_stack = QStackedWidget()
        for name in ["Alice", "Bob", "Charlie"]:
            chat_page = ChatPage(sock, name)
            self.chat_stack.addWidget(chat_page)

        self.layout.addLayout(self.sidebar, 1)
        self.layout.addWidget(self.chat_stack, 3)
        
        self.chat_list.itemClicked.connect(self.switch_chat)

    def switch_chat(self, item):
        index = self.chat_list.row(item)
        self.chat_stack.setCurrentIndex(index)

main_window = MainWindow()
main_window.setCentralWidget(SignInPage())
app.exec()