from datetime import datetime, timezone
from sqlalchemy import delete

from celery import shared_task

from database import ActivationTokenModel
from database.session_postgresql import SyncSessionLocal


@shared_task
def delete_expired_tokens() -> str:
    with SyncSessionLocal() as session:
        try:
            stmt = delete(ActivationTokenModel).where(
                ActivationTokenModel.expires_at < datetime.now(timezone.utc),
            )
            result = session.execute(stmt)
            deleted_count = result.rowcount
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error deleting expired tokens: {e}")
            raise

    return f"Deleted {deleted_count} expired tokens."
