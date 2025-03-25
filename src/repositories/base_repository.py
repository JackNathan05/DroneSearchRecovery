# src/repositories/base_repository.py
import logging

logger = logging.getLogger(__name__)

class BaseRepository:
    """Base repository class for database operations"""
    
    def __init__(self, session, model_class):
        self.session = session
        self.model_class = model_class
    
    def get_by_id(self, entity_id):
        """Get entity by ID"""
        return self.session.query(self.model_class).filter(self.model_class.id == entity_id).first()
    
    def get_all(self):
        """Get all entities"""
        return self.session.query(self.model_class).all()
    
    def add(self, entity):
        """Add a new entity"""
        try:
            self.session.add(entity)
            self.session.commit()
            logger.debug(f"Added new {self.model_class.__name__}: {entity}")
            return entity
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error adding entity: {str(e)}")
            raise

    def update(self, entity):
        """Update an entity"""
        try:
            self.session.add(entity)
            self.session.commit()
            logger.debug(f"Updated {self.model_class.__name__}: {entity}")
            return entity
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating entity: {str(e)}")
            raise

    def delete(self, entity):
        """Delete an entity"""
        try:
            self.session.delete(entity)
            self.session.commit()
            logger.debug(f"Deleted {self.model_class.__name__}: {entity}")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting entity: {str(e)}")
            raise
    
    def delete_by_id(self, entity_id):
        """Delete entity by ID"""
        entity = self.get_by_id(entity_id)
        if entity:
            self.delete(entity)
            return True
        return False