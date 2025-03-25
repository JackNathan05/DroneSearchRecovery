# src/utils/restore_util.py
import os
import logging
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)

def list_available_backups(backup_dir="data/backup"):
    """List available database backups"""
    backups = []
    
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.startswith("drone_search_") and filename.endswith(".db"):
                filepath = os.path.join(backup_dir, filename)
                timestamp = os.path.getmtime(filepath)
                size = os.path.getsize(filepath)
                
                backups.append({
                    "filename": filename,
                    "path": filepath,
                    "timestamp": datetime.fromtimestamp(timestamp),
                    "size": size
                })
    
    # Sort by timestamp (newest first)
    backups.sort(key=lambda b: b["timestamp"], reverse=True)
    return backups

def restore_from_backup(backup_path, current_db_path="data/drone_search.db"):
    """Restore database from a backup file"""
    try:
        if not os.path.exists(backup_path):
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # Create a backup of the current database first
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_restore_backup = f"data/backup/pre_restore_{timestamp}.db"
        os.makedirs(os.path.dirname(pre_restore_backup), exist_ok=True)
        
        if os.path.exists(current_db_path):
            shutil.copy2(current_db_path, pre_restore_backup)
            logger.info(f"Created pre-restore backup at {pre_restore_backup}")
        
        # Copy backup to current database
        shutil.copy2(backup_path, current_db_path)
        logger.info(f"Restored database from {backup_path}")
        
        return True
    except Exception as e:
        logger.error(f"Restore failed: {str(e)}")
        return False