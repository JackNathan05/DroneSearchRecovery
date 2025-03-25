# src/views/mission_planner.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QTextEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

class MissionPlannerWidget(QWidget):
    """New mission planner screen widget"""
    
    # Signal to notify when a mission is created
    mission_created = pyqtSignal(str, str)  # mission_name, mission_description
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with title and back button
        header_layout = QHBoxLayout()
        
        # Back button
        back_button = QPushButton("← Home")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1E3A8A;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        back_button.clicked.connect(self.go_home)
        header_layout.addWidget(back_button)
        
        # Title
        title_label = QLabel("New Mission Planner")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E3A8A;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)
        
        # Mission name section
        name_label = QLabel("What should this mission be called?")
        name_label.setStyleSheet("font-size: 16px; color: #1E3A8A;")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter mission name...")
        self.name_input.setMinimumHeight(40)
        self.name_input.setStyleSheet("""
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
        
        main_layout.addWidget(name_label)
        main_layout.addWidget(self.name_input)
        main_layout.addSpacing(30)
        
        # Natural language interface section
        nl_label = QLabel("Describe your search mission in natural language:")
        nl_label.setStyleSheet("font-size: 16px; color: #1E3A8A;")
        main_layout.addWidget(nl_label)
        
        # Chat interface
        chat_frame = QFrame()
        chat_frame.setFrameShape(QFrame.Shape.StyledPanel)
        chat_frame.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 2px solid #D1D5DB;
                border-radius: 10px;
            }
        """)
        chat_layout = QVBoxLayout(chat_frame)
        
        # Chat history display
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setMinimumHeight(200)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                font-size: 14px;
            }
        """)
        
        # Chat input area
        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your mission description...")
        self.chat_input.setMinimumHeight(40)
        self.chat_input.setStyleSheet("""
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
        
        send_button = QPushButton("Send")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3A80D2;
            }
        """)
        send_button.clicked.connect(self.send_message)
        
        chat_input_layout.addWidget(self.chat_input)
        chat_input_layout.addWidget(send_button)
        
        chat_layout.addWidget(self.chat_history)
        chat_layout.addLayout(chat_input_layout)
        
        main_layout.addWidget(chat_frame)
        main_layout.addStretch()
        
        # Action buttons at the bottom
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #D1D5DB;
                color: #1E3A8A;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #9CA3AF;
            }
        """)
        
        create_button = QPushButton("Create Mission")
        create_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3A80D2;
            }
        """)
        
        cancel_button.clicked.connect(self.cancel_mission)
        create_button.clicked.connect(self.create_mission)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(create_button)
        
        main_layout.addLayout(button_layout)
    
    def send_message(self):
        """Send a message to the chat"""
        message = self.chat_input.text().strip()
        if message:
            # Add user message to chat history
            self.chat_history.append(f"<b>You:</b> {message}")
            
            # Clear input field
            self.chat_input.clear()
            
            # Simulate response (in a real app, this would call the NLP service)
            self.simulate_response(message)
    
    def simulate_response(self, message):
        """Simulate a response from the system (placeholder for NLP)"""
        # This is just a placeholder - would be replaced with actual NLP processing
        response = f"I'll set up a search mission based on: '{message}'. Please provide additional details or confirm to create the mission."
        
        # Add system response to chat history
        self.chat_history.append(f"<b>System:</b> {response}")
    
    def cancel_mission(self):
        """Cancel mission creation and return to home screen"""
        # Clear inputs
        self.name_input.clear()
        self.chat_history.clear()
        self.chat_input.clear()
        
        # Emit signal to navigate back (will be connected in main window)
        self.mission_created.emit("", "")
    
    def create_mission(self):
        """Create the mission and move to mission screen"""
        mission_name = self.name_input.text().strip()
        mission_description = self.chat_history.toPlainText()
        
        if not mission_name:
            # Show error message (in a real app, use a proper dialog)
            self.chat_history.append("<b>System:</b> Please provide a name for the mission.")
            return
        
        # Emit signal to create mission and navigate
        self.mission_created.emit(mission_name, mission_description)
        
        # Clear inputs
        self.name_input.clear()
        self.chat_history.clear()
        self.chat_input.clear()
    
    def go_home(self):
        """Return to home screen"""
        # Clear inputs
        self.name_input.clear()
        self.chat_history.clear()
        self.chat_input.clear()
        
        # Signal to return home (empty strings indicate cancellation)
        self.mission_created.emit("", "")