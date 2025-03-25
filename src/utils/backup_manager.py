# src/utils/backup_manager.py
import os
import logging
import threading
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BackupManager:
    """Manages automatic backups of the database"""
    
    def __init__(self, database, config=None):
        """Initialize backup manager"""
        self.database = database
        self.config = config or {}
        
        # Default configuration
        self.backup_directory = self.config.get('backup_directory', 'data/backup')
        self.max_backups = self.config.get('max_backups', 10)
        self.backup_interval = self.config.get('backup_interval', 24)  # hours
        
        # Ensure backup directory exists
        os.makedirs(self.backup_directory, exist_ok=True)
        
        # Track last backup time
        self.last_backup_time = None
        
        # Background thread
        self.backup_thread = None
        self.stop_flag = threading.Event()
    
    def start_scheduled_backups(self):
        """Start scheduled backup thread"""
        if self.backup_thread and self.backup_thread.is_alive():
            logger.warning("Backup schedule already running")
            return
        
        self.stop_flag.clear()
        self.backup_thread = threading.Thread(target=self._backup_scheduler)
        self.backup_thread.daemon = True
        self.backup_thread.start()
        logger.info(f"Automatic backups scheduled every {self.backup_interval} hours")
    
    def stop_scheduled_backups(self):
        """Stop scheduled backup thread"""
        if self.backup_thread and self.backup_thread.is_alive():
            self.stop_flag.set()
            self.backup_thread.join(timeout=1.0)
            logger.info("Automatic backups stopped")
    
    def _backup_scheduler(self):
        """Background thread to perform scheduled backups"""
        while not self.stop_flag.is_set():
            # Perform a backup if none has been done yet or interval has passed
            if (not self.last_backup_time or 
                datetime.now() - self.last_backup_time > timedelta(hours=self.backup_interval)):
                self.perform_backup()
            
            # Check every 5 minutes
            self.stop_flag.wait(300)
    
    def perform_backup(self):
        """Perform a database backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"drone_search_{timestamp}.db"
            backup_path = os.path.join(self.backup_directory, filename)
            
            # Perform backup
            self.database.backup(backup_path)
            self.last_backup_time = datetime.now()
            
            logger.info(f"Automatic backup created at {backup_path}")
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            return backup_path
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return None
    
    def _cleanup_old_backups(self):
        """Remove old backups if we exceed max_backups"""
        try:
            # Get all backup files
            backup_files = [os.path.join(self.backup_directory, f) for f in os.listdir(self.backup_directory)
                          if f.startswith("drone_search_") and f.endswith(".db")]
            
            # Sort by modification time (oldest first)
            backup_files.sort(key=lambda f: os.path.getmtime(f))
            
            # Remove the oldest backups if we have too many
            while len(backup_files) > self.max_backups:
                oldest = backup_files.pop(0)
                os.remove(oldest)
                logger.info(f"Removed old backup: {oldest}")
        except Exception as e:
            logger.error(f"Backup cleanup failed: {str(e)}")