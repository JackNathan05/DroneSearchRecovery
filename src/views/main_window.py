# src/views/main_window.py (updated version)
import os
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QStackedWidget, QLabel, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont
from datetime import datetime

# Import our custom widgets
from src.views.mission_planner import MissionPlannerWidget
from src.views.mission_view import MissionViewWidget
from src.views.login_view import LoginWidget
from src.views.map_view import MapViewWidget
from src.views.drone_status_view import DroneStatusWidget
from src.models.database import Database
from src.models.user import User
from src.repositories.user_repository import UserRepository


logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowTitle("Drone Search & Recovery")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            QPushButton#sidebar_button {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton#sidebar_button:hover {
                background-color: #3A80D2;
            }
            QPushButton#new_mission_button {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#new_mission_button:hover {
                background-color: #3A80D2;
            }
        """)
        
        # Central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create sidebar
        self.setup_sidebar()
        
        # Create content area with stacked widget for different screens
        self.content_area = QStackedWidget()
        self.main_layout.addWidget(self.content_area)
        
        # Add screens to the stacked widget
        self.setup_home_screen()
        self.setup_mission_planner_screen()
        self.setup_mission_screen()
        self.setup_map_view_screen()
        self.setup_drone_status_screen()
        
        # Start with the home screen
        self.content_area.setCurrentIndex(0)
        
        logger.info("Main window initialized")
    
    def setup_sidebar(self):
        """Set up the sidebar navigation menu"""
        self.sidebar_container = QWidget()
        self.sidebar_container.setFixedWidth(250)
        self.sidebar_container.setStyleSheet("""
            background-color: #1E3A8A;
            color: white;
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar_container)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        # Add toggle button at the top
        toggle_btn = QPushButton("≡")
        toggle_btn.setFixedSize(40, 40)
        toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3A80D2;
            }
        """)
        toggle_btn.clicked.connect(self.toggle_sidebar)
        
        # Horizontal layout for the toggle button
        toggle_layout = QHBoxLayout()
        toggle_layout.addWidget(toggle_btn)
        toggle_layout.addStretch()
        sidebar_layout.addLayout(toggle_layout)

         # Add logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #D1D5DB;
                color: #1E3A8A;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #9CA3AF;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        sidebar_layout.addSpacing(20)
        
        # Account section
        account_label = QLabel("Account")
        account_label.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        sidebar_layout.addWidget(account_label)
        
        # User info placeholder - make it a class variable so we can update it
        self.user_info_label = QLabel("User: Not logged in")
        self.user_info_label.setStyleSheet("color: #D1D5DB;")
        sidebar_layout.addWidget(self.user_info_label)
        
        # Missions section
        missions_label = QLabel("Missions")
        missions_label.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        sidebar_layout.addWidget(missions_label)
        
        # Mission list (placeholder for now)
        self.mission_buttons_layout = QVBoxLayout()
        sidebar_layout.addLayout(self.mission_buttons_layout)
        
        # Add spacer at the bottom
        sidebar_layout.addStretch()

        # Add sidebar to main layout
        self.main_layout.addWidget(self.sidebar_container)
    
    def add_mission_to_sidebar(self, mission_name):
        """Add a mission button to the sidebar"""
        mission_btn = QPushButton(mission_name)
        mission_btn.setObjectName("sidebar_button")
        mission_btn.clicked.connect(lambda checked, m=mission_name: self.open_mission(m))

        # Enable context menu
        mission_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        mission_btn.customContextMenuRequested.connect(lambda pos, m=mission_name, btn=mission_btn: self._show_mission_context_menu(pos, m, btn))

        self.mission_buttons_layout.addWidget(mission_btn)
        return mission_btn
    
    def _show_mission_context_menu(self, pos, mission_name, button):
        """Show context menu for mission button"""
        context_menu = QMenu(self)
        
        # Add menu actions
        delete_action = context_menu.addAction("Delete Mission")
        rename_action = context_menu.addAction("Rename Mission")
        
        # Show the menu and get selected action
        action = context_menu.exec(button.mapToGlobal(pos))
        
        # Handle the selected action
        if action == delete_action:
            self._delete_mission(mission_name, button)
        elif action == rename_action:
            self._rename_mission(mission_name, button)

    def _delete_mission(self, mission_name, button):
        """Delete a mission after confirmation"""
        # Show confirmation dialog
        reply = QMessageBox.question(
            self, 
            'Delete Mission',
            f'Are you sure you want to delete the mission "{mission_name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Get mission from database
            mission = self.mission_repository.get_by_name_and_user(mission_name, self.current_user_id)
            
            if mission:
                # Delete from database
                self.mission_repository.delete(mission)
                logger.info(f"Deleted mission from database: {mission_name}")
            else:
                logger.warning(f"Could not find mission in database: {mission_name}")
            
            # Remove from sidebar
            if button == self.active_mission_button:
                self.active_mission_button = None
                self.go_to_home()
            
            self.mission_buttons_layout.removeWidget(button)
            button.deleteLater()
            
            logger.info(f"Deleted mission from UI: {mission_name}")

    def _rename_mission(self, mission_name, button):
        """Rename a mission"""
        from PyQt6.QtWidgets import QInputDialog
        
        # Show input dialog to get new name
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Mission",
            "Enter new mission name:",
            text=mission_name
        )
        
        if ok and new_name:
            # Get mission from database
            mission = self.mission_repository.get_by_name_and_user(mission_name, self.current_user_id)
            
            if mission:
                # Update in database
                mission.name = new_name
                self.mission_repository.update(mission)
                logger.info(f"Renamed mission in database from '{mission_name}' to '{new_name}'")
                
                # Update button text
                button.setText(new_name)
                
                # If this is the active mission, update the mission view title
                if button == self.active_mission_button:
                    self.mission_view.set_mission_data(new_name, "")
                
                logger.info(f"Renamed mission in UI from '{mission_name}' to '{new_name}'")
            else:
                logger.warning(f"Could not find mission in database: {mission_name}")
                QMessageBox.warning(self, "Rename Failed", 
                                f"Could not find mission '{mission_name}' in database.")

    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar_container.width() == 250:
            self.sidebar_container.setFixedWidth(50)
        else:
            self.sidebar_container.setFixedWidth(250)
    
    def open_mission(self, mission_name, button=None):
        """Open a specific mission and highlight it in the sidebar"""
        logger.info(f"Opening mission: {mission_name}")
        
        # Get mission data from database
        mission = self.mission_repository.get_by_name_and_user(mission_name, self.current_user_id)
        
        if mission:
            # Update active mission styling
            self._update_active_mission(button)
            
            # Set mission data and switch to mission VIEW screen (not planner)
            self.mission_view.set_mission_data(mission_name, mission.description or "")
            self.content_area.setCurrentIndex(self.MISSION_VIEW_SCREEN)
        else:
            logger.warning(f"Mission not found in database: {mission_name}")
            QMessageBox.warning(self, "Mission Not Found", 
                            f"Could not find mission '{mission_name}' in database.")

    def setup_home_screen(self):
        """Set up the home screen with New Mission and Import Mission buttons"""
        home_widget = QWidget()
        home_layout = QVBoxLayout(home_widget)
        
        # Add a welcome label
        welcome_label = QLabel("Welcome to Drone Search & Recovery")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E3A8A;")
        
        # Create buttons
        new_mission_btn = QPushButton("New Mission")
        new_mission_btn.setObjectName("new_mission_button")
        new_mission_btn.setFixedSize(200, 60)
        new_mission_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3A80D2;
            }
        """)
        new_mission_btn.clicked.connect(self.new_mission)
        
        import_mission_btn = QPushButton("Import Mission")
        import_mission_btn.setObjectName("new_mission_button")  # Using the same style
        import_mission_btn.setFixedSize(200, 60)
        import_mission_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3A80D2;
            }
        """)
        import_mission_btn.clicked.connect(self.import_mission)

        # Add Drone Status button
        drone_status_btn = QPushButton("Drone Status")
        drone_status_btn.setObjectName("new_mission_button")
        drone_status_btn.setFixedSize(200, 60)
        drone_status_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3A80D2;
            }
        """)
        drone_status_btn.clicked.connect(self.show_drone_status)
        
        # Add map view button
        map_view_btn = QPushButton("Map View")
        map_view_btn.setObjectName("new_mission_button")
        map_view_btn.setFixedSize(200, 60)
        map_view_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3A80D2;
            }
        """)
        map_view_btn.clicked.connect(self.show_map_view)

        # Center the buttons horizontally
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(new_mission_btn)
        button_layout.addSpacing(20)  # Add space between buttons
        button_layout.addWidget(import_mission_btn)
        button_layout.addSpacing(20)
        button_layout.addWidget(drone_status_btn)
        button_layout.addSpacing(20)
        button_layout.addWidget(map_view_btn)
        button_layout.addStretch()
        
        # Add widgets to layout
        home_layout.addStretch()
        home_layout.addWidget(welcome_label)
        home_layout.addSpacing(30)
        home_layout.addLayout(button_layout)
        home_layout.addStretch()
        
        # Add to stacked widget
        self.content_area.addWidget(home_widget)
    
    def setup_mission_planner_screen(self):
        """Set up the new mission planner screen"""
        self.mission_planner = MissionPlannerWidget()
        
        # Connect the mission creation signal
        self.mission_planner.mission_created.connect(self.handle_mission_created)
        
        # Add to stacked widget
        self.content_area.addWidget(self.mission_planner)
    
    def setup_mission_screen(self):
        """Set up the active mission screen with map"""
        self.mission_view = MissionViewWidget(self)  # Pass self as main_window
        
        # Connect back button
        self.mission_view.back_button.clicked.connect(self.go_to_home)
        
        # Add to stacked widget
        self.content_area.addWidget(self.mission_view)
        
    def new_mission(self):
        """Create a new mission and switch to planner screen"""
        logger.info("Creating new mission")
        # Clear any previous input in the mission planner
        self.mission_planner.name_input.clear()
        self.mission_planner.chat_history.clear()
        self.mission_planner.chat_input.clear()
    
        # Switch to mission planner screen
        self.content_area.setCurrentIndex(self.MISSION_PLANNER_SCREEN)

    def handle_mission_created(self, mission_name, mission_description):
        """Handle when a mission is created from the planner"""
        if mission_name:
            logger.info(f"Mission created: {mission_name}")
            
            # Save to database
            mission = self.mission_repository.create_mission(
                name=mission_name,
                user_id=1,  # For now, hardcode user_id (in real app, get from current user)
                description=mission_description
            )
            
            if mission:
                # If the mission has chat history, save it
                if mission_description:
                    self.mission_repository.add_chat_message(
                        mission_id=mission.id,
                        message=mission_description,
                        sender_type="user",
                        user_id=1  # Again, hardcoded for now
                    )
                
                # Add to sidebar
                mission_btn = self.add_mission_to_sidebar(mission_name)
                
                # Set mission data in view
                self.mission_view.set_mission_data(mission_name, mission_description)
                
                # Switch to mission view
                self.content_area.setCurrentIndex(self.MISSION_VIEW_SCREEN)
            else:
                # Mission creation failed (name might be duplicate)
                QMessageBox.warning(self, "Mission Creation Failed", 
                                "Could not create mission. Name may already exist.")
                return
        else:
            # Cancel was pressed, go back to home
            self.content_area.setCurrentIndex(self.HOME_SCREEN)

    def import_mission(self):
        """Import an existing mission"""
        logger.info("Import mission button clicked")
        
        # In a real implementation, this would open a file dialog
        # For now, we'll create a mission with a unique name
        
        # Generate a unique name
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        mission_name = f"Imported Mission {timestamp}"
        mission_description = "This is a simulated imported mission."
        
        # Save to database
        mission = self.mission_repository.create_mission(
            name=mission_name,
            user_id=self.current_user_id,
            description=mission_description,
            mission_type="imported"
        )
        
        if mission:
            # Add chat message
            self.mission_repository.add_chat_message(
                mission_id=mission.id,
                message=mission_description,
                sender_type="system"
            )
            
            # Add to sidebar
            mission_btn = self.add_mission_to_sidebar(mission_name)
            
            # Set mission data in view
            self.mission_view.set_mission_data(mission_name, mission_description)
            
            # Switch to mission view
            self.content_area.setCurrentIndex(self.MISSION_VIEW_SCREEN)
        else:
            QMessageBox.warning(self, "Import Failed", "Could not import mission.")

    def __init__(self, db):
        super().__init__()

        # Store database instance
        self.db = db
        self.session = db.get_session()
        
        # Create repositories
        from repositories.user_repository import UserRepository
        from repositories.mission_repository import MissionRepository
        
        self.user_repository = UserRepository(self.session)
        self.mission_repository = MissionRepository(self.session)
            
        # Window setup
        self.setWindowTitle("Drone Search & Recovery")
        self.setMinimumSize(1200, 800)
        # ... existing style setup ...
        
        # Track current active mission and user
        self.active_mission_button = None
        self.current_user = None
        
        # Central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create sidebar (hidden initially)
        self.setup_sidebar()
        self.sidebar_container.hide()  # Hide until login
        
        # Create content area with stacked widget for different screens
        self.content_area = QStackedWidget()
        self.main_layout.addWidget(self.content_area)

         # Define screen indices as constants for clarity
        self.LOGIN_SCREEN = 0
        self.HOME_SCREEN = 1
        self.MISSION_PLANNER_SCREEN = 2
        self.MISSION_VIEW_SCREEN = 3
        self.MAP_VIEW_SCREEN = 4  
        self.DRONE_STATUS_SCREEN = 5
            
        # Add login screen
        self.setup_login_screen()
        self.setup_home_screen()
        self.setup_mission_planner_screen()
        self.setup_mission_screen()
        self.setup_map_view_screen()
        self.setup_drone_status_screen()
        
        # Start with the login screen
        self.content_area.setCurrentIndex(self.LOGIN_SCREEN)
        
        logger.info("Main window initialized")

    def setup_login_screen(self):
        """Set up the login screen"""
        self.login_widget = LoginWidget(self.user_repository)
        self.login_widget.login_successful.connect(self.handle_login)
        self.content_area.addWidget(self.login_widget)

    def handle_login(self, username):
        """Handle successful login"""
        logger.info(f"User logged in: {username}")
        self.current_user = username
        
        # Get user from database
        user = self.user_repository.get_by_username(username)
        if user:
            # Store user ID for later use
            self.current_user_id = user.id
            
            # Show the sidebar after login
            self.sidebar_container.show()
            
            # Update user info in sidebar
            self.user_info_label.setText(f"{username}")
            
            # Load missions for this user
            self.load_user_missions(user.id)
            
            # Show the home screen
            self.content_area.setCurrentIndex(self.HOME_SCREEN)

    def logout(self):
        """Log out the current user"""
        reply = QMessageBox.question(
            self, 
            'Logout',
            'Are you sure you want to logout?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info(f"User logged out: {self.current_user}")
            self.current_user = None
            
            # Hide sidebar
            self.sidebar_container.hide()
            
            # Clear active mission
            self.active_mission_button = None
            
            # Clear login inputs
            self.login_widget.username_input.clear()
            self.login_widget.password_input.clear()
            
            # Go back to login screen
            self.content_area.setCurrentIndex(self.LOGIN_SCREEN)

    def add_mission_to_sidebar(self, mission_name):
        """Add a mission button to the sidebar with context menu"""
        mission_btn = QPushButton(mission_name)
        mission_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #3A80D2;
            }
        """)
        mission_btn.setObjectName("sidebar_button")
        mission_btn.clicked.connect(lambda checked, m=mission_name, btn=mission_btn: self.open_mission(m, btn))
        
        # Enable context menu
        mission_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        mission_btn.customContextMenuRequested.connect(lambda pos, m=mission_name, btn=mission_btn: self._show_mission_context_menu(pos, m, btn))
        
        self.mission_buttons_layout.addWidget(mission_btn)
        return mission_btn

    def open_mission(self, mission_name, button=None):
        """Open a specific mission and highlight it in the sidebar"""
        logger.info(f"Opening mission: {mission_name}")
            
        # Update active mission styling
        self._update_active_mission(button)
            
        # Set mission data and switch to mission screen
        self.mission_view.set_mission_data(mission_name, "")
        self.content_area.setCurrentIndex(self.MISSION_VIEW_SCREEN)  # Mission screen index
            
    def _update_active_mission(self, button):
        """Update styling to highlight active mission"""
        # Remove highlight from previous active mission
        if self.active_mission_button:
            self.active_mission_button.setStyleSheet("""
                QPushButton {
                    background-color: #4A90E2;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #3A80D2;
                }
            """)
            
        # Set highlight for new active mission
        if button:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #3A80D2;  /* Darker blue to indicate active */
                    color: white;
                    border-left: 4px solid #FF7E47;  /* Orange accent for visual indicator */
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    text-align: left;
                }
            """)
            self.active_mission_button = button

    def go_to_home(self):
        """Navigate to home screen (not login screen)"""
        logger.info("Navigating to home screen")
        
        # Clear the active mission selection when going home
        if self.active_mission_button:
            self.active_mission_button.setStyleSheet("""
                QPushButton {
                    background-color: #4A90E2;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #3A80D2;
                }
            """)
            self.active_mission_button = None
        
        # Navigate to home screen
        self.content_area.setCurrentIndex(self.HOME_SCREEN)

    def load_user_missions(self, user_id):
        """Load missions for the current user from database"""
        # Clear existing mission buttons (that aren't part of the layout)
        for i in reversed(range(self.mission_buttons_layout.count())): 
            widget = self.mission_buttons_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Get missions from database
        missions = self.mission_repository.get_by_user(user_id)
        
        if missions:
            for mission in missions:
                self.add_mission_to_sidebar(mission.name)
            
            logger.info(f"Loaded {len(missions)} missions from database")
        else:
            logger.info("No missions found for user")

    def setup_drone_status_screen(self):
        """Set up the drone status screen"""
        self.drone_status_widget = DroneStatusWidget()
        self.content_area.addWidget(self.drone_status_widget)

    def show_drone_status(self):
        """Show the drone status screen"""
        self.content_area.setCurrentIndex(self.DRONE_STATUS_SCREEN)  # Define this index constant

    def setup_map_view_screen(self):
        """Set up the map view screen"""
        self.map_view = MapViewWidget(self)
        self.content_area.addWidget(self.map_view)

    def show_map_view(self):
        """Show the map view screen"""
        self.content_area.setCurrentIndex(self.MAP_VIEW_SCREEN)