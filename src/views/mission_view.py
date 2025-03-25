# src/views/mission_view.py
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QFrame, QSplitter
)
from PyQt6.QtCore import Qt
from src.views.mission_planner import MissionPlannerWidget

logger = logging.getLogger(__name__)

class MissionViewWidget(QWidget):
    """Mission view screen with chat and map"""
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel for chat
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with mission title and back button
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
        # We'll connect this in the main window
        self.back_button = back_button
        header_layout.addWidget(back_button)
        
        # Mission title
        self.mission_title = QLabel("Mission Name")
        self.mission_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E3A8A;")
        header_layout.addWidget(self.mission_title)
        header_layout.addStretch()
    
        left_layout.addLayout(header_layout)
        
        # Chat history
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
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                font-size: 14px;
            }
        """)
        
        # Chat input
        chat_input_layout = QHBoxLayout()
        self.chat_input = QTextEdit()
        self.chat_input.setPlaceholderText("Type your message...")
        self.chat_input.setMaximumHeight(80)
        self.chat_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #D1D5DB;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #4A90E2;
            }
        """)
        
        send_button = QPushButton("Send")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
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
        
        left_layout.addWidget(chat_frame)
        
        # Right panel for map
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        map_frame = QFrame()
        map_frame.setFrameShape(QFrame.Shape.StyledPanel)
        map_frame.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 2px solid #D1D5DB;
                border-radius: 10px;
            }
        """)
        map_layout = QVBoxLayout(map_frame)
        
        # Placeholder for the map (will be replaced with actual map in later phases)
        map_placeholder = QLabel("Interactive Map View")
        map_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        map_placeholder.setStyleSheet("font-size: 18px; color: #1E3A8A;")
        map_layout.addWidget(map_placeholder)
        
        right_layout.addWidget(map_frame)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set initial sizes (1:2 ratio)
        splitter.setSizes([300, 600])
        
        main_layout.addWidget(splitter)
    
    def set_mission_data(self, mission_name, mission_description):
        """Set mission data in the UI"""
        self.mission_title.setText(mission_name)
        
        # Debug connection
        self.debug_connection()
        
        # Load chat history from database if connection is valid
        if self.main_window:
            self.load_chat_history(mission_name)
        else:
            # Add a message indicating the issue
            self.chat_history.clear()
            self.chat_history.append("<b>System:</b> Error: Database connection not available.")
        
        # If description is provided (new mission) and chat history is empty,
        # add it to the chat
        if mission_description and self.chat_history.toPlainText().strip() == "":
            self.chat_history.append(f"<b>Mission Description:</b> {mission_description}")

    def send_message(self):
        """Send a message from the chat input"""
        message = self.chat_input.toPlainText().strip()
        if not message:
            return
            
        logger.debug(f"Sending message: {message}")
        
        # Add user message to chat history
        self.chat_history.append(f"<b>You:</b> {message}")
        
        if not self.main_window:
            logger.warning("Main window reference not set, message not saved to database")
            response = "System error: Message could not be saved to database."
            self.chat_history.append(f"<b>System:</b> {response}")
            self.chat_input.clear()
            return
        
        try:
            # Get mission from the main window repository
            mission = self.main_window.mission_repository.get_by_name_and_user(
                self.mission_title.text(),
                self.main_window.current_user_id
            )
            
            if mission:
                # Save message to database
                self.main_window.mission_repository.add_chat_message(
                    mission_id=mission.id,
                    message=message,
                    sender_type="user",
                    user_id=self.main_window.current_user_id
                )
                
                # Process message (in a real app, this would call the NLP service)
                response = self.simulate_response(message)
                
                # Validate response is not None
                if response is None:
                    logger.error("Response was None, using default message")
                    response = "Error processing message, please try again."
                
                # Save system response
                self.main_window.mission_repository.add_chat_message(
                    mission_id=mission.id,
                    message=response,
                    sender_type="system"
                )
                
                # Add system response to chat history
                self.chat_history.append(f"<b>System:</b> {response}")
            else:
                logger.warning(f"Mission not found: {self.mission_title.text()}")
                response = "Error: Mission not found in database."
                self.chat_history.append(f"<b>System:</b> {response}")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            # Roll back the session to recover from errors
            if hasattr(self.main_window, 'session'):
                self.main_window.session.rollback()
            response = "System error: Message could not be processed."
            self.chat_history.append(f"<b>System:</b> {response}")
        
        # Clear input field
        self.chat_input.clear()

    def load_chat_history(self, mission_name):
        """Load chat history for a mission"""
        if not self.main_window:
            logger.warning("Main window reference not set")
            return
            
        mission = self.main_window.mission_repository.get_by_name_and_user(
            mission_name,
            self.main_window.current_user_id
        )
        
        if mission:
            # Clear current chat history
            self.chat_history.clear()
            
            # Get chat messages from database
            messages = self.main_window.mission_repository.get_chat_history(mission.id)
            
            logger.info(f"Found {len(messages)} chat messages for mission {mission_name}")
            
            # Add messages to chat history
            for msg in messages:
                if msg.sender_type == "user":
                    self.chat_history.append(f"<b>You:</b> {msg.message}")
                else:
                    self.chat_history.append(f"<b>System:</b> {msg.message}")
                
                # Force update to ensure messages are visible
                self.chat_history.repaint()
            
            logger.info(f"Loaded {len(messages)} chat messages for mission {mission_name}")
        else:
            logger.warning(f"Could not find mission in database: {mission_name}")

    def set_mission_data(self, mission_name, mission_description):
        """Set mission data in the UI"""
        self.mission_title.setText(mission_name)
        
        # Load chat history from database
        self.load_chat_history(mission_name)
    
        # If description is provided (new mission) and chat history is empty,
        # add it to the chat
        if mission_description and self.chat_history.toPlainText().strip() == "":
            self.chat_history.append(f"<b>Mission Description:</b> {mission_description}")

    def simulate_response(self, message):
        """Simulate a response from the system (placeholder for NLP)"""
        # This is just a placeholder - would be replaced with actual NLP processing
        # Make sure we always return a string, never None
        if not message:
            return "I received an empty message."
        
        response = f"I'll process your request: '{message}'. In a real implementation, this would trigger drone commands or mission updates."
        return response  # Ensure this always returns a valid string

    def setup_mission_planner_screen(self):
        """Set up the new mission planner screen"""
        self.mission_planner = MissionPlannerWidget()
        
        # Connect the mission creation signal
        self.mission_planner.mission_created.connect(self.handle_mission_created)
        
        # Add to stacked widget
        self.content_area.addWidget(self.mission_planner)

    def setup_mission_screen(self):
        """Set up the active mission screen with map"""
        self.mission_view = MissionViewWidget()
        
        # Set the main window reference
        self.mission_view.main_window = self

        # Connect back button
        self.mission_view.back_button.clicked.connect(self.go_to_home)

        # Add to stacked widget
        self.content_area.addWidget(self.mission_view)

    def go_to_home(self):
        """Navigate to home screen"""
        self.content_area.setCurrentIndex(0)  # Home screen index

    def debug_connection(self):
        """Debug helper to verify main_window connection"""
        if self.main_window:
            logger.info(f"Main window connection OK: {self.main_window}")
            return True
        else:
            logger.warning("Main window reference not set")
            return False