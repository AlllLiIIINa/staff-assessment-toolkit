import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import CompanyInvitations, User, CompanyMembers
from app.depends.exceptions import InviteToOwnCompany, ErrorRetrievingUser, AlreadyExistsInvitation, \
    AlreadyExistsMember, ErrorCreatingInvitation, InvitationNotFound, NoPermission, ErrorHandleInvitation, \
    InvalidAction, ErrorRetrievingInvited, NotOwner, ErrorRetrievingMembershipUser, \
    ErrorRetrievingMembershipCompany, ErrorRetrievingInvitation
from app.schemas.company import CompanyInvitationCreate
from app.services.companies import CompanyService


class InvitationService:
    model = CompanyInvitations

    def __init__(self, session: AsyncSession):
        self.session = session
        self.company_service = CompanyService(self.session)

    async def create(self, user_id: str, invitation_data: CompanyInvitationCreate):
        try:
            if invitation_data.recipient_id == user_id:
                raise InviteToOwnCompany

            result = await self.session.scalars(select(User).filter(User.user_id == invitation_data.recipient_id))

            if not result.first():
                logging.error(f"Error retrieving User with ID {invitation_data.recipient_id}")
                raise ErrorRetrievingUser(e=invitation_data.recipient_id)

            result = await self.session.scalars(select(self.model).filter(
                self.model.sender_id == user_id, self.model.recipient_id == invitation_data.recipient_id,
                self.model.company_id == invitation_data.company_id))

            if result.first():
                logging.error("The invitation is already exist")
                raise AlreadyExistsInvitation

            result = await self.session.scalars(select(CompanyMembers).filter(
                CompanyMembers.company_id == invitation_data.company_id,
                CompanyMembers.user_id == invitation_data.recipient_id
            ))

            if result.first():
                logging.error("The invited user is already a member of the company")
                raise AlreadyExistsMember

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
            raise ErrorCreatingInvitation(e)

    async def handle(self, user_id: str, invitation_id: str, action: str):
        try:
            existing_invitation = await self.session.scalars(select(self.model).filter(
                self.model.invitation_id == invitation_id
            ))
            invitation = existing_invitation.first()

            if not invitation:
                raise InvitationNotFound(invitation_id)

            if user_id != invitation.sender_id and user_id != invitation.recipient_id:
                raise NoPermission

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
                logging.error("Use 'accept' or 'reject'")
                raise InvalidAction

        except Exception as e:
            logging.error(f"Error during handle the invitation for company: {e}")
            raise ErrorHandleInvitation(e)

    async def invited_users(self, company_id: str, user_id: str, page: int = 1, items_per_page: int = 10):
        try:
            company = await self.company_service.get_by_id(company_id, user_id)

            if company.owner_id != user_id:
                logging.error("You are not the owner of this company")
                raise NotOwner

            offset = (page - 1) * items_per_page
            result = await self.session.scalars(select(self.model).filter(
                (self.model.company_id == company_id) &
                (self.model.sender_id == user_id)
            ).offset(offset).limit(items_per_page))
            invitations = result.all()

            return invitations

        except Exception as e:
            logging.error(f"Error getting invited users for company with ID {company_id}: {e}")
            raise ErrorRetrievingInvited(e)

    async def membership_requests(self, company_id: str, user_id: str, page: int = 1, items_per_page: int = 10):
        try:
            company = await self.company_service.get_by_id(company_id, user_id)

            if company.owner_id != user_id:
                raise NotOwner

            offset = (page - 1) * items_per_page
            result = await self.session.scalars(select(self.model).filter(
                (self.model.company_id == company_id) &
                (self.model.recipient_id == user_id) &
                (self.model.sender_id != user_id)).offset(offset).limit(items_per_page))
            membership_requests = result.all()

            return membership_requests

        except Exception as e:
            logging.error(f"Error getting membership requests for company with ID {company_id}: {e}")
            raise ErrorRetrievingMembershipCompany(e)

    async def user_requests(self, user_id: str, page: int = 1, items_per_page: int = 10):
        try:
            offset = (page - 1) * items_per_page
            result = await self.session.scalars(select(self.model).filter(
                (self.model.recipient_id == user_id) &
                (self.model.sender_id != user_id)).offset(offset).limit(items_per_page))
            return result.all()

        except Exception as e:
            logging.error(f"Error getting membership requests for user with ID {user_id}: {e}")
            raise ErrorRetrievingMembershipUser(e)

    async def user_invitations(self, user_id: str, page: int = 1, items_per_page: int = 10):
        try:
            offset = (page - 1) * items_per_page
            result = await self.session.scalars(select(self.model).filter(
                (self.model.sender_id == user_id)).offset(offset).limit(items_per_page))
            return result.all()

        except Exception as e:
            logging.error(f"Error getting invitations for user with ID {user_id}: {e}")
            raise ErrorRetrievingInvitation(e)
