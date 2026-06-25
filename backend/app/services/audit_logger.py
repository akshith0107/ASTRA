import logging
from sqlalchemy.orm import Session
from app.database.models.audit_logs import AuditLog

logger = logging.getLogger(__name__)

class AuditLogger:
    @staticmethod
    def log_action(db: Session, action: str, user_id: int = None):
        """
        Logs an action to the audit_logs table.
        """
        try:
            log = AuditLog(user_id=user_id, action=action)
            db.add(log)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
            db.rollback()

audit_logger = AuditLogger()
