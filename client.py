import sys, shutil, os, socket, threading
import database
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QFileDialog
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
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 800, 600)

        self.show()

class ProfileDialog(QDialog):

    def __init__(self, username, phone):
        super().__init__()
        self.setWindowTitle("Profile")
        self.setGeometry(200, 200, 400, 300)

        self.form_layout = QFormLayout(self)

        self.profile_picture = QLabel(self)
        self.profile_picture.setFixedSize(100, 100)
        load_profile_picture(self.profile_picture)
        self.profile_picture.setStyleSheet("border-radius: 50px; border: 2px solid gray;")


        self.username_field = QLineEdit(self)
        self.username_field.setText(username)
        self.username_field.setReadOnly(True)

        self.phone_field = QLineEdit(self)
        self.phone_field.setText(phone)
        self.phone_field.setReadOnly(True)

        self.form_layout.addRow("Picture", self.profile_picture)
        self.form_layout.addRow("Username:", self.username_field)
        self.form_layout.addRow("Phone:", self.phone_field)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        self.button_box.accepted.connect(self.accept)

        self.form_layout.addWidget(self.button_box)
        self.setLayout(self.form_layout)

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

    def accept(self):
        username = self.username_field.text().strip()
        phone = self.phone_field.text().strip()

        if not username or not phone:
            QMessageBox.warning(self, "Input Error", "Username and phone cannot be empty.")
            return
        
        if not database.check_user_phone(username, phone):
            QMessageBox.warning(self, "Input Error", "Phone number does not match the username.")
            return
        
        if database.add_contact(main_window.centralWidget().username, username, phone):
            QMessageBox.information(self, "Success", f"Contact {username} added successfully!")
            main_window.centralWidget().update_chat_stack()
        else:
            QMessageBox.warning(self, "Error", "Failed to add contact. It may already exist.")

class SettingsDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 400, 300)

        self.form_layout = QFormLayout(self)

        self.username_field = QLineEdit(self)
        self.username_field.setText(main_window.centralWidget().username)
        self.phone_field = QLineEdit(self)
        self.phone_field.setText(main_window.centralWidget().phone)

        self.new_password_field = QLineEdit(self)
        self.new_password_field.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirm_password_field = QLineEdit(self)
        self.confirm_password_field.setEchoMode(QLineEdit.EchoMode.Password)

        self.change_profile_picture_button = QPushButton("Change Profile Picture", self)
        self.change_profile_picture_button.clicked.connect(self.choose_image)

        self.form_layout.addRow("Username:", self.username_field)
        self.form_layout.addRow("Phone:", self.phone_field)
        self.form_layout.addRow("New Password:", self.new_password_field)
        self.form_layout.addRow("Confirm Password:", self.confirm_password_field)
        self.form_layout.addRow(self.change_profile_picture_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.reject)


        self.form_layout.addWidget(self.button_box)
        self.setLayout(self.form_layout)

    def choose_image(self):
        file_path, i = QFileDialog.getOpenFileName(
            self,
            "Select Profile Picture",
            "",
            "Image Files (*.png *.jpg *.jpeg )"
        )
        if file_path:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            dest = os.path.join(BASE_DIR, f"Assets/profile_{main_window.centralWidget().username}.jpg")
            try:
                shutil.copyfile(file_path, dest)
                QMessageBox.information(self, "Success", "Profile picture updated!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not update picture:\n{e}")

        
    def save_settings(self):
        new_username = self.username_field.text().strip()
        new_phone = self.phone_field.text().strip()

        if not new_username or not new_phone:
            QMessageBox.warning(self, "Input Error", "Username and phone cannot be empty.")
            return

        old_username = main_window.centralWidget().username
        if new_username != old_username:
            if not database.update_username(old_username, new_username):
                QMessageBox.warning(self, "Error", "Username is already taken.")
                return

        if not database.update_phone(new_username, new_phone):
            QMessageBox.warning(self, "Error", "Failed to update phone.")
            return

        new_password = self.new_password_field.text().strip()
        confirm_password = self.confirm_password_field.text().strip()

        if new_password and new_password != confirm_password:
            QMessageBox.warning(self, "Input Error", "Passwords do not match.")
            return

        if new_password and not database.update_user_info(new_username, new_password):
            QMessageBox.warning(self, "Error", "Failed to update password.")
            return

        try:
            if new_username != old_username:
                main_window.centralWidget().sock.send(f"USERNAME_CHANGE:{old_username}:{new_username}".encode())
        except Exception as e:
            print(f"Error notifying server of username change: {e}")

        main_window.centralWidget().username = new_username
        main_window.centralWidget().phone = new_phone
        main_window.centralWidget().update_chat_stack()
        QMessageBox.information(self, "Success", "Settings updated successfully!")


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
                sock.send(username.encode())
                main_window.setCentralWidget(MainChatWindow(sock, username, database.get_phone(username)))
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
    def __init__(self, sock: socket.socket, username: str, recipient: str):
        super().__init__()
        self.sock = sock
        self.recipient = recipient
        self.username = username

        self.layout = QVBoxLayout(self)
        self.messages_display = QListWidget()
        self.message_input = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_picture_button = QPushButton("Send Picture")

        self.layout.addWidget(self.messages_display)
        input_row = QHBoxLayout()
        input_row.addWidget(self.message_input)
        input_row.addWidget(self.send_picture_button)
        input_row.addWidget(self.send_button)
        self.layout.addLayout(input_row)

        self.send_picture_button.clicked.connect(self.choose_image)
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

        self.get_chat_history()

        self.send_button.setStyleSheet("background-color: lightblue;")
        self.send_picture_button.setStyleSheet("background-color: lightgreen;")


    def choose_image(self):
        file_path, i = QFileDialog.getOpenFileName(
            self,
            "Select Profile Picture",
            "",
            "Image Files (*.png *.jpg *.jpeg )"
        )
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    data = file.read()
                filename = os.path.basename(file_path)
                header = f"{self.recipient}:<img>:{filename}:{len(data)}"
                self.sock.send(header.encode())
                self.sock.send(data)
                
                assets_dir = "Assets"
                if not os.path.exists(assets_dir):
                    os.makedirs(assets_dir)
                
                sent_image_path = os.path.join(assets_dir, f"sent_{filename}_from_{self.username}_to_{self.recipient}.jpg")
                import shutil
                shutil.copy2(file_path, sent_image_path)
                database.save_image(self.username, self.recipient, sent_image_path, filename)
                
                chat_item = QListWidgetItem(f"You sent an image: {filename}")
                chat_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.messages_display.addItem(chat_item)
               
                image_label = QLabel()
                pixmap = QPixmap(file_path)
                pixmap = pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
                image_label.setPixmap(pixmap)
                image_label.setFixedSize(pixmap.size())
                
                image_widget = QWidget()
                image_layout = QHBoxLayout()
                image_layout.setContentsMargins(5, 5, 5, 5)
                
                image_layout.addStretch()
                image_layout.addWidget(image_label)
                image_widget.setLayout(image_layout)
                
                chat_list_item = QListWidgetItem()
                chat_list_item.setSizeHint(image_widget.sizeHint())
                
                self.messages_display.addItem(chat_list_item)
                self.messages_display.setItemWidget(chat_list_item, image_widget)
                self.messages_display.scrollToBottom()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not upload picture:\n{e}")

    def send_message(self):
        text = self.message_input.text().strip()
        if text:

            item = QListWidgetItem(f"You: {text}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.messages_display.addItem(item)
            self.messages_display.scrollToBottom()
            try:
                self.sock.send(f"{self.recipient}: {text}".encode())
                print(f"{self.username} sent: {text}")
                database.save_message(self.username, self.recipient, text)
                self.message_input.clear()
            except:
                error_item = QListWidgetItem("⚠️ Could not send message.")
                error_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.messages_display.addItem(error_item)


    def add_received_message(self, text):
        item = QListWidgetItem(f"{self.recipient}: {text}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        self.messages_display.addItem(item)
        self.messages_display.scrollToBottom()

    
    def get_chat_history(self):
        print(f'{database.get_chat_history(self.username, self.recipient)}')
        for message in database.get_chat_history(self.username, self.recipient):
            if message.message_type == 'text':
                if message.sender_id == database.get_id(self.username):
                    item = QListWidgetItem(f"You: {message.chat_content}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                else:
                    item = QListWidgetItem(f"{self.recipient}: {message.chat_content}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                self.messages_display.addItem(item)
            elif message.message_type == 'image':
                image_path, filename = message.chat_content.split('|')
                is_sent = message.sender_id == database.get_id(self.username)
                
                if is_sent:
                    text_item = QListWidgetItem(f"You sent an image: {filename}")
                    text_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                else:
                    text_item = QListWidgetItem(f"{self.recipient} sent an image: {filename}")
                    text_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                self.messages_display.addItem(text_item)
                
                if os.path.exists(image_path):
                    image_label = QLabel()
                    pixmap = QPixmap(image_path)
                    pixmap = pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
                    image_label.setPixmap(pixmap)
                    image_label.setFixedSize(pixmap.size())
                    
                    image_widget = QWidget()
                    image_layout = QHBoxLayout()
                    image_layout.setContentsMargins(5, 5, 5, 5)
                    
                    if is_sent:
                        image_layout.addStretch()
                        image_layout.addWidget(image_label)
                    else:
                        image_layout.addWidget(image_label)
                        image_layout.addStretch()
                    
                    image_widget.setLayout(image_layout)
                    
                    chat_list_item = QListWidgetItem()
                    chat_list_item.setSizeHint(image_widget.sizeHint())
                    
                    self.messages_display.addItem(chat_list_item)
                    self.messages_display.setItemWidget(chat_list_item, image_widget)


class MainChatWindow(QWidget):
    message_received = pyqtSignal(str, str)
    image_received = pyqtSignal(str, str, str, bytes)

    def __init__(self, sock, username, phone):
        super().__init__()
        self.setWindowTitle("Chat")
        self.layout = QHBoxLayout(self)
        self.quick_actions_bar = QHBoxLayout()

        self.sock = sock
        self.username = username
        self.phone = phone
        
        
        self.sidebar = QVBoxLayout()
        self.add_contact_button = QPushButton()
        self.add_contact_icon = QIcon("Assets/Contact.png")
        self.add_contact_button.setIcon(self.add_contact_icon)
        self.add_contact_button.setIconSize(QSize(48, 48))
        self.add_contact_button.clicked.connect(lambda: AddContactDialog().exec())

        self.profile_button = QPushButton()
        self.profile_button_picture = QLabel(self.profile_button)
        load_profile_picture(self.profile_button_picture)
        self.profile_button.setIconSize(QSize(48, 48))
        self.profile_button.clicked.connect(lambda: ProfileDialog(username, phone).exec())

        self.settings_button = QPushButton()
        self.settings_button.clicked.connect(lambda: SettingsDialog().exec())
        self.settings_icon = QIcon("Assets/setting.png")
        self.settings_button.setIconSize(QSize(48, 48))
        self.settings_button.setIcon(self.settings_icon)

        self.quick_actions_bar.addWidget(self.settings_button)
        self.quick_actions_bar.addWidget(self.add_contact_button)
        self.quick_actions_bar.addWidget(self.profile_button)

        self.sidebar.addLayout(self.quick_actions_bar)
        
        self.chat_list_label = QLabel("Chats")
        self.chat_list = QListWidget()
        
        self.sidebar.addWidget(self.chat_list_label)
        self.sidebar.addWidget(self.chat_list)
        self.sidebar.addStretch()
        
        
        self.chat_stack = QStackedWidget()
        self.chat_pages = {}
        self.update_chat_stack()

        self.layout.addLayout(self.sidebar, 1)
        self.layout.addWidget(self.chat_stack, 3)
        
        self.chat_list.itemClicked.connect(self.switch_chat)

        self.message_received.connect(self.handle_message_received)
        self.image_received.connect(self.handle_image_received)

        threading.Thread(target=self.receive_loop, daemon=True).start()

    def switch_chat(self, item):
        index = self.chat_list.row(item)
        self.chat_stack.setCurrentIndex(index)


    def handle_message_received(self, sender, text):
        if sender in self.chat_pages:
            item = QListWidgetItem(f"{sender}: {text}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
            self.chat_pages[sender].messages_display.addItem(item)
            self.chat_pages[sender].messages_display.scrollToBottom()
    
    def handle_image_received(self, sender, filename, save_path, image_data):
        if sender in self.chat_pages:
            item = QListWidgetItem(f"{sender} sent an image: {filename}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
            self.chat_pages[sender].messages_display.addItem(item)
            
            image_label = QLabel()
            pixmap = QPixmap(save_path)
            pixmap = pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(pixmap)
            image_label.setFixedSize(pixmap.size())
            
            image_widget = QWidget()
            image_layout = QHBoxLayout()
            image_layout.setContentsMargins(5, 5, 5, 5)
            
            image_layout.addWidget(image_label)
            image_layout.addStretch()
            image_widget.setLayout(image_layout)
            
            chat_list_item = QListWidgetItem()
            chat_list_item.setSizeHint(image_widget.sizeHint())
            
            self.chat_pages[sender].messages_display.addItem(chat_list_item)
            self.chat_pages[sender].messages_display.setItemWidget(chat_list_item, image_widget)
            self.chat_pages[sender].messages_display.scrollToBottom()

    def update_chat_stack(self):
        self.chat_list.clear()
        for name in database.get_contacts(self.username):
            chat_page = ChatPage(self.sock, self.username, name)
            
            contact_widget = QWidget()
            contact_layout = QHBoxLayout()
            contact_layout.setContentsMargins(8, 8, 8, 8)
            contact_layout.setSpacing(10)
            
            profile_label = QLabel()
            profile_pixmap = load_contact_profile_picture(name)
            profile_pixmap = profile_pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            profile_label.setPixmap(profile_pixmap)
            profile_label.setFixedSize(40, 40)
            profile_label.setStyleSheet("border-radius: 20px; border: 1px solid gray;")
            
            name_label = QLabel(name)
            name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
            name_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            
            contact_layout.addWidget(profile_label)
            contact_layout.addWidget(name_label)
            contact_layout.addStretch()
            contact_widget.setLayout(contact_layout)
            contact_widget.setFixedHeight(56)
            
            list_item = QListWidgetItem()
            list_item.setSizeHint(QSize(0, 56))
            
            self.chat_list.addItem(list_item)
            self.chat_list.setItemWidget(list_item, contact_widget)
            
            self.chat_pages[name] = chat_page
            self.chat_stack.addWidget(chat_page)
        
    def receive_loop(self):
        print("Starting receive loop...")
        message_buffer = b''
        
        while True:
            try:
                data = self.sock.recv(8192)
                if not data:
                    break
                
                message_buffer += data
                
                while True:
                    try:
                        decoded = message_buffer.decode()
                        
                        if '<img>' in decoded:
                            parts = decoded.split(':')
                            if len(parts) >= 4:
                                sender = parts[0].strip()
                                filename = parts[2].strip()
                                size = int(parts[3].strip())
                                
                                print(f"[IMAGE] Receiving from {sender}: {filename} ({size} bytes)")
                                
                                message_buffer = b''
                                
                                image_data = b''
                                while len(image_data) < size:
                                    chunk_size = min(8192, size - len(image_data))
                                    chunk = self.sock.recv(chunk_size)
                                    if not chunk:
                                        raise ConnectionError("Connection lost during image transfer")
                                    image_data += chunk
                                
                                assets_dir = "Assets"
                                if not os.path.exists(assets_dir):
                                    os.makedirs(assets_dir)
                                
                                save_path = os.path.join(assets_dir, f"received_{filename}_from_{sender}_to_{self.username}.jpg")
                                with open(save_path, 'wb') as f:
                                    f.write(image_data)
                                
                                database.save_image(sender, self.username, save_path, filename)
                                
                                self.image_received.emit(sender, filename, save_path, image_data)
                                break
                            else:
                                break
                        else:
                            if ':' in decoded:
                                sender, text = decoded.split(':', 1)
                                sender = sender.strip()
                                text = text.strip()
                                
                                print(f"[MESSAGE] Received from {sender}: {text}")
                                
                                if sender in self.chat_pages:
                                    self.message_received.emit(sender, text)
                                else:
                                    print(f"[WARNING] No chat page for sender: {sender}")
                                
                                message_buffer = b''
                                break
                            else:
                                break
                    except UnicodeDecodeError:
                        break
                    except ValueError as e:
                        print(f"[ERROR] Message parsing error: {e}")
                        message_buffer = b''
                        break
                        
            except Exception as e:
                print(f"Error in receive_loop: {e}")
                break
    

def load_profile_picture(profile_picture):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(BASE_DIR, "Assets/profile.jpg")

    if os.path.exists(profile_path):
        pixmap = QPixmap(profile_path)
        pixmap = pixmap.scaled(profile_picture.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        profile_picture.setPixmap(pixmap)
    else:
        profile_picture.setText("No Image")

def load_contact_profile_picture(contact_name):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    contact_profile_path = os.path.join(BASE_DIR, f"Assets/profile_{contact_name}.jpg")
    default_profile_path = os.path.join(BASE_DIR, "Assets/default_profile.jpg")
    
    if os.path.exists(contact_profile_path):
        return QPixmap(contact_profile_path)
    elif os.path.exists(default_profile_path):
        return QPixmap(default_profile_path)
    else:
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.GlobalColor.gray)
        return pixmap


main_window = MainWindow()
main_window.setCentralWidget(SignInPage())
app.exec()
