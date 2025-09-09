
from datetime import datetime
from flask import g
from models import db, AuditLog

def log_event(user_id, action, resource_type, resource_id, metadata=None):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        metadata=metadata or {},
        timestamp=datetime.utcnow()
    )
    db.session.add(entry)
    db.session.commit()
