import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Company, CompanyMembers, User
from app.depends.exceptions import ErrorRetrievingList, ErrorRetrievingCompany, CompanyNotFound, \
    ErrorHiddenCompany, ErrorCreatingCompany, NotOwner, ErrorUpdatingCompany, ErrorDeletingCompany, \
    ErrorRetrievingMember, ErrorRemovingMember, OwnerLeave, ErrorLeavingCompany, NotMember, AlreadyExistsCompany, \
    ErrorRetrievingAdmin, ErrorSettingRoleAdmin, ErrorChangeOwnerAdminRole
from app.schemas.company import CompanyBase, CompanyUpdate, CompanyMemberResponse, CompanyAdmin
from app.services.users import UserService


async def check_company_owner(company: Company, user_id: str):

    if company.owner_id != user_id:
        logging.error("You are not the owner of this company")
        raise NotOwner()

    return True


class CompanyService:
    model = Company

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_service = UserService(self.session)

    async def get_all(self, page: int = 1, items_per_page: int = 10):
        try:
            offset = (page - 1) * items_per_page
            query = (select(self.model).filter(self.model.company_is_visible == True).
                     offset(offset).limit(items_per_page))
            result = await self.session.execute(query)
            logging.info("Getting company list processed successfully")
            return [CompanyBase(**user.__dict__) for user in result.scalars().all()]

        except Exception as e:
            logging.error(f"Error retrieving company list: {e}")
            raise ErrorRetrievingList(e)

    async def get_by_id(self, company_id: str, user_id: str):
        try:
            result = await self.session.scalars(select(self.model).filter(self.model.company_id == company_id))
            company = result.first()

            if not company:
                logging.error(f"Company with ID {company_id} not found")
                raise CompanyNotFound(company_id)

            if company.owner_id != user_id and not company.company_is_visible:
                logging.error(f"Company with ID {company_id} is hidden")
                raise ErrorHiddenCompany(company_id)

            logging.info("Getting company processed successfully")
            return company

        except Exception as e:
            logging.error(f"Error retrieving company with ID {company_id}: {e}")
            raise ErrorRetrievingCompany(e)

    async def create(self, company_data: CompanyBase, user_id):
        try:
            result = await (self.session.scalars
                            (select(self.model).filter(self.model.company_name == company_data.company_name)))

            if result.first():
                logging.error("Company is already exist")
                raise AlreadyExistsCompany

            company_data.owner_id = user_id
            new_company = self.model(**company_data.model_dump())
            self.session.add(new_company)
            await self.session.commit()

            company_member = CompanyMembers(company_id=new_company.company_id, user_id=user_id, is_admin=True)
            self.session.add(company_member)
            await self.session.commit()
            logging.info(f"Company created: {new_company}")
            logging.info("Creating company processed successfully")
            return new_company

        except Exception as e:
            logging.error(f"Error creating company: {e}")
            raise ErrorCreatingCompany(e)

    async def update(self, company_id: str, company_data: CompanyUpdate, user_id: str):
        try:
            company = await self.get_by_id(company_id, user_id)
            await check_company_owner(company, user_id)
            logging.info(company_data)
            company_dict = company_data.model_dump(exclude_none=True)
            query_company = (update(self.model).where(self.model.company_id == company_id)
                             .values(company_dict).returning(self.model.company_id))
            await self.session.execute(query_company)
            await self.session.commit()
            logging.info(f"Company update successful for company ID: {company_id}")
            return await self.get_by_id(company_id, user_id)

        except Exception as e:
            logging.error(f"Error during user update for company ID: {company_id}: {e}")
            raise ErrorUpdatingCompany(e)

    async def delete(self, company_id: str, user_id: str):
        try:
            company = await self.get_by_id(company_id, user_id)

            if company.owner_id != user_id:
                logging.error("You are not the owner of this company")
                raise NotOwner()

            await self.session.delete(company)
            await self.session.commit()
            logging.info("Deleting user processed successfully")
            return company

        except Exception as e:
            logging.error(f"Error deleting user with ID {company_id}: {e}")
            raise ErrorDeletingCompany(e)

    async def get_company_members(self, company_id: str, page: int = 1, items_per_page: int = 10):
        try:
            offset = (page - 1) * items_per_page
            query = await self.session.execute(
                select(CompanyMembers.user_id, User.user_email, User.user_firstname, User.user_lastname)
                .join(User, CompanyMembers.user_id == User.user_id)
                .filter(CompanyMembers.company_id == company_id)
                .offset(offset).limit(items_per_page)
            )
            logging.info("Getting member list processed successfully")
            rows = query.all()
            members_with_user_data = [
                CompanyMemberResponse(
                    user_id=row[0],
                    user_email=row[1],
                    user_firstname=row[2],
                    user_lastname=row[3]
                )
                for row in rows
            ]
            return members_with_user_data

        except Exception as e:
            logging.error(f"Error retrieving member list: {e}")
            raise ErrorRetrievingMember(e)

    async def get_user_companies(self, user_id: str):
        try:
            result = await self.session.execute(select(CompanyMembers).filter((CompanyMembers.user_id == user_id)))
            member = result.scalars().first()
            return member

        except Exception as e:
            logging.error(f"Error retrieving member with ID {user_id}: {e}")
            raise ErrorRetrievingCompany(e)

    async def remove_member(self, company_id: str, user_id: str, member_id: str):
        try:
            result = await self.session.scalars(select(CompanyMembers).filter(
                CompanyMembers.company_id == company_id, CompanyMembers.user_id == member_id))
            member = result.first()

            if not member:
                logging.error("You are not the member of this company")
                raise NotMember

            await self.get_by_id(company_id, user_id)

            if user_id == member_id:
                logging.error("Owner cannot remove yourself from the company")
                raise OwnerLeave

            await self.session.delete(member)
            await self.session.commit()
            return "User has been successfully removed from your company"

        except Exception as e:
            logging.error(f"Error retrieving company with ID {company_id}: {e}")
            raise ErrorRemovingMember(member_id, e)

    async def leave_company(self, company_id: str, user_id: str):
        try:
            result = await self.session.scalars(select(CompanyMembers).filter(
                CompanyMembers.company_id == company_id, CompanyMembers.user_id == user_id))
            member = result.first()
            company = await self.get_by_id(company_id, user_id)

            if not member:
                raise NotMember

            if company.owner_id == user_id:
                logging.error("Owner cannot leave the company")
                raise OwnerLeave

            await self.session.delete(member)
            await self.session.commit()
            return f"You have left the company with ID {company_id}"

        except Exception as e:
            logging.error(f"Error leaving company with ID {company_id}: {e}")
            raise ErrorLeavingCompany(company_id, e)

    async def get_admins(self, company_id: str, page: int = 1, admin_per_page: int = 10):
        try:
            offset = (page - 1) * admin_per_page
            query = (
                select(CompanyMembers, User)
                .join(User, CompanyMembers.user_id == User.user_id)
                .filter(
                    (CompanyMembers.company_id == company_id) &
                    (CompanyMembers.is_admin == True)
                )
                .offset(offset)
                .limit(admin_per_page)
            )
            result = await self.session.execute(query)
            admins_with_user_data = []

            for record in result:
                company_member, user = record
                admin_data = {**user.__dict__}
                admins_with_user_data.append(admin_data)

            return admins_with_user_data

        except Exception as e:
            logging.error(f"Error retrieving admins for company {company_id}: {e}")
            raise ErrorRetrievingAdmin(e)

    async def set_admin_status(self, admin_data: CompanyAdmin, user_id: str):
        try:
            result = await self.session.scalars(select(self.model).filter(self.model.company_id == admin_data.company_id))
            company = result.first()

            await self.get_by_id(company.company_id, user_id)

            if admin_data.user_id == company.owner_id:
                logging.error("Error change admin role for owner")
                raise ErrorChangeOwnerAdminRole

            member = await self.get_user_companies(admin_data.user_id)
            member.is_admin = admin_data.is_admin
            await self.session.commit()
            action = "set" if admin_data.is_admin else "removed from"
            return (f"User with ID {admin_data.user_id} has been {action}"
                    f"admin status for the company with ID {admin_data.company_id}")

        except Exception as e:
            logging.error(f"Error setting admin role for User: {e}")
            raise ErrorSettingRoleAdmin(e)
