import logging
from typing import List, Sequence

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Notification
from app.depends.exceptions import NoPermission, ErrorCreatingNotification, NotificationNotFound, \
    ErrorGetUserNotifications, ErrorHandleUserNotification


class NotificationService:
    model = Notification

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_quiz_notification(self, user_ids: List[str], company_id: str, quiz_name: str) -> List:
        try:
            notifications = [{
                "user_id": user,
                "company_id": company_id,
                "notification_text": f"New quiz in company with ID {company_id} with name {quiz_name} is available!"
            } for user in user_ids]

            await self.session.execute(insert(Notification).values(notifications))
            await self.session.commit()
            return notifications

        except Exception as e:
            logging.error(f"Error creating quiz notifications: {e}")
            raise ErrorCreatingNotification(e)

    async def get_user_notifications(self, user_id: str) -> Sequence[Notification]:
        try:
            result = await self.session.scalars(select(self.model).where(self.model.user_id == user_id))
            notifications = result.all()

            if not notifications:
                raise NotificationNotFound

            for notification in notifications:
                if user_id != notification.user_id:
                    raise NoPermission

            return notifications

        except Exception as e:
            logging.error(f"Error getting user notifications: {e}")
            raise ErrorGetUserNotifications(e)

    async def handle_notifications(self, notification_id: str, action: bool, user_id: str) -> str:
        try:
            result = await self.session.scalars(select(self.model).where(self.model.notification_id == notification_id))
            notification = result.first()

            if not notification:
                raise NotificationNotFound(notification_id)

            if notification.user_id != user_id:
                raise NoPermission

            notification.notification_status = action
            await self.session.commit()
            return f"Notification with ID {notification_id} successfully read."

        except Exception as e:
            logging.error(f"Error getting user notification with ID {notification_id}: {e}")
            raise ErrorHandleUserNotification(notification_id, e)
