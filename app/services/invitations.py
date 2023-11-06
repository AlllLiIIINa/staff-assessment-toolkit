import logging
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import CompanyInvitations, User, CompanyMembers
from app.schemas.company import CompanyInvitationCreate
from app.services.companies import CompanyService


class InvitationService:
    model = CompanyInvitations

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: str, invitation_data: CompanyInvitationCreate):
        if invitation_data.recipient_id == user_id:
            raise HTTPException(status_code=404, detail=f"You cannot invite yourself to your own company")

        result = await self.session.execute(select(User).filter(User.user_id == invitation_data.recipient_id))
        recipient = result.scalars().first()
        if not recipient:
            raise HTTPException(status_code=404, detail=f"Error retrieving user with ID {invitation_data.recipient_id}")

        result = await self.session.execute(select(self.model).filter(
            self.model.sender_id == user_id, self.model.recipient_id == invitation_data.recipient_id,
            self.model.company_id == invitation_data.company_id))
        existing_invitation = result.scalars().first()
        if existing_invitation:
            raise HTTPException(status_code=400, detail="The invitation is already exist")

        result = await self.session.execute(select(CompanyMembers).filter(
            CompanyMembers.company_id == invitation_data.company_id,
            CompanyMembers.user_id == invitation_data.recipient_id
        ))
        existing_member = result.scalars().first()
        if existing_member:
            raise HTTPException(status_code=400, detail="The invited user is already a member of the company")

        try:
            invitation_data.sender_id = user_id
            new_invitation = self.model(**invitation_data.model_dump())
            self.session.add(new_invitation)
            await self.session.commit()
            logging.info(f"Invitation created: {new_invitation}")
            logging.info("Creating invitation processed successfully")
            return (f"The invitation for the user with ID {invitation_data.recipient_id} "
                    f"to the company with ID {invitation_data.company_id} was successfully created")

        except Exception as e:
            logging.error(f"Error creating invitation: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating invitation: {e}")

    async def handle(self, user_id: str, invitation_id: str, action: str):
        existing_invitation = await self.session.execute(select(self.model).filter(
            self.model.invitation_id == invitation_id
        ))
        invitation = existing_invitation.scalars().first()

        if not invitation:
            raise HTTPException(status_code=404, detail=f"Invitation with ID {invitation_id} not found")

        if user_id != invitation.sender_id and user_id != invitation.recipient_id:
            raise HTTPException(status_code=403, detail="You don't have permission to manage this invitation")

        try:
            if action == "accept":
                invitation.invitation_accepted = True
                new_member = CompanyMembers(company_id=invitation.company_id, user_id=invitation.recipient_id)
                self.session.add(new_member)
                await self.session.commit()
                return f"Invitation with ID {invitation_id} has been accepted"

            elif action == "reject":
                await self.session.delete(invitation)
                await self.session.commit()
                return f"Invitation with ID {invitation_id} has been canceled"

            else:
                return f"Invalid action. Use 'accept' or 'reject'"

        except Exception as e:
            logging.error(f"Error during handle the invitation for company: {e}")
            raise HTTPException(status_code=500, detail=f"handle the invitation for company: {e}")

    async def invited_users(self, company_id: str, user_id: str, page: int = 1, items_per_page: int = 10):
        try:
            offset = (page - 1) * items_per_page
            result = await self.session.execute(select(self.model).filter(
                (self.model.company_id == company_id) &
                (self.model.sender_id == user_id)
            ).offset(offset).limit(items_per_page))
            invitations = result.scalars().all()

        except Exception as e:
            logging.error(f"Error getting invited users for company with ID {company_id}: {e}")
            raise HTTPException(status_code=500,
                                detail=f"Error getting invited users for company with ID {company_id}: {e}")

        company_repo = CompanyService(self.session)
        company = await company_repo.get_by_id(company_id, user_id)

        if company.owner_id != user_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this company")

        return invitations

    async def membership_requests(self, company_id: str, user_id: str, page: int = 1, items_per_page: int = 10):
        try:
            offset = (page - 1) * items_per_page
            result = await self.session.execute(select(self.model).filter(
                (self.model.company_id == company_id) &
                (self.model.recipient_id == user_id) &
                (self.model.sender_id != user_id)).offset(offset).limit(items_per_page))
            membership_requests = result.scalars().all()

        except Exception as e:
            logging.error(f"Error getting membership requests for company with ID {company_id}: {e}")
            raise HTTPException(status_code=500,
                                detail=f"Error getting membership requests for company with ID {company_id}: {e}")

        company_repo = CompanyService(self.session)
        company = await company_repo.get_by_id(company_id, user_id)

        if company.owner_id != user_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this company")

        return membership_requests

    async def user_requests(self, user_id: str, page: int = 1, items_per_page: int = 10):
        try:
            offset = (page - 1) * items_per_page
            result = await self.session.execute(select(self.model).filter(
                (self.model.recipient_id == user_id) &
                (self.model.sender_id != user_id)).offset(offset).limit(items_per_page))
            membership_requests = result.scalars().all()
            return membership_requests
        except Exception as e:
            logging.error(f"Error getting membership requests for user with ID {user_id}: {e}")
            raise HTTPException(status_code=500,
                                detail=f"Error getting membership requests for user with ID {user_id}: {e}")

    async def user_invitations(self, user_id: str, page: int = 1, items_per_page: int = 10):
        try:
            offset = (page - 1) * items_per_page
            result = await self.session.execute(select(self.model).filter(
                (self.model.sender_id == user_id)).offset(offset).limit(items_per_page))
            invitations = result.scalars().all()
            return invitations
        except Exception as e:
            logging.error(f"Error getting invitations for user with ID {user_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error getting invitations for user with ID {user_id}: {e}")
