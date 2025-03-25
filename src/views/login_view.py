# src/views/login_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.models.database import Database
from src.models.user import User
from src.repositories.user_repository import UserRepository

class LoginWidget(QWidget):
    """Login screen widget"""
    
    # Signal emitted on successful login
    login_successful = pyqtSignal(str)  # User name
    
    def __init__(self, user_repository):
        super().__init__()
        self.user_repository = user_repository
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        main_layout = QVBoxLayout(self)
        
        # Center the login form
        main_layout.addStretch(1)
        
        # Login form container
        form_container = QFrame()
        form_container.setFrameShape(QFrame.Shape.StyledPanel)
        form_container.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 2px solid #D1D5DB;
                border-radius: 10px;
                max-width: 400px;
            }
        """)
        form_container.setMaximumWidth(400)
        
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Drone Search & Recovery")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E3A8A; text-align: center;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Login to your account")
        subtitle_label.setStyleSheet("font-size: 16px; color: #4A90E2; text-align: center;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(subtitle_label)
        form_layout.addSpacing(10)
        
        # Username field
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-size: 14px; color: #1E3A8A;")
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D1D5DB;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        form_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 14px; color: #1E3A8A;")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #D1D5DB;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        form_layout.addWidget(self.password_input)
        
        # Login button
        login_button = QPushButton("Login")
        login_button.setMinimumHeight(50)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3A80D2;
            }
        """)
        login_button.clicked.connect(self.attempt_login)
        form_layout.addWidget(login_button)
        
        # Center the form container
        container_layout = QHBoxLayout()
        container_layout.addStretch(1)
        container_layout.addWidget(form_container)
        container_layout.addStretch(1)
        
        main_layout.addLayout(container_layout)
        main_layout.addStretch(1)
    
    def attempt_login(self):
        """Validate login credentials"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return
        
        # Authenticate using repository
        user = self.user_repository.authenticate(username, password)
        
        if user:
            self.login_successful.emit(username)
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")