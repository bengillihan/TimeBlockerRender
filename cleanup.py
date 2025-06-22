import os
from datetime import datetime, timedelta
from app import db, DailyPlan, TimeBlock, Priority, ToDo
from app_factory import create_app

def cleanup_old_data():
    """
    Deletes data older than a specified retention period to keep the database size
    within free tier limits.
    """
    app = create_app()
    with app.app_context():
        retention_days = 60
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # Delete old daily plans and associated data
        old_plans = DailyPlan.query.filter(DailyPlan.date < cutoff_date.date()).all()
        for plan in old_plans:
            # Manually delete related items to trigger cascades if they are not set up
            Priority.query.filter_by(daily_plan_id=plan.id).delete()
            TimeBlock.query.filter_by(daily_plan_id=plan.id).delete()
            db.session.delete(plan)

        # Delete old completed ToDos
        ToDo.query.filter(
            ToDo.completed == True,
            ToDo.completed_at < cutoff_date
        ).delete()

        db.session.commit()
        print(f"Successfully cleaned up data older than {retention_days} days.")

if __name__ == "__main__":
    cleanup_old_data()