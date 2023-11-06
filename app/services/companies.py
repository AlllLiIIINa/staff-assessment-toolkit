import logging
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Company, CompanyMembers
from app.schemas.company import CompanyBase, CompanyUpdate
from app.services.users import UserService


class CompanyService:
    model = Company

    def __init__(self, session: AsyncSession):
        self.session = session

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
            raise HTTPException(status_code=500, detail=f"Error retrieving company list: {e}")

    async def get_by_id(self, company_id: str, user_id: str):
        try:
            result = await self.session.execute(select(self.model).filter(self.model.company_id == company_id))
            company = result.scalars().first()
        except Exception as e:
            logging.error(f"Error retrieving company with ID {company_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving company with ID {company_id}: {e}")

        if not company:
            raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")

        if company.owner_id != user_id and not company.company_is_visible:
            raise HTTPException(status_code=404, detail=f"Company with ID {company_id} is hidden")

        logging.info("Getting company processed successfully")
        return company

    async def create(self, company_data: CompanyBase, user_id):
        try:
            company_data.owner_id = user_id
            new_company = self.model(**company_data.model_dump())
            self.session.add(new_company)
            await self.session.commit()
            await self.session.close()
            logging.info(f"Company created: {new_company}")
            logging.info("Creating company processed successfully")
            return new_company

        except Exception as e:
            logging.error(f"Error creating company: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating company: {e}")

    async def update(self, company_id: str, company_data: CompanyUpdate, user_id: str):
        company = await self.get_by_id(company_id, user_id)

        if company.owner_id != user_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this company")

        try:
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
            raise HTTPException(status_code=500, detail=f"Error updating company: {e}")

    async def delete(self, company_id: str, user_id: str):
        company = await self.get_by_id(company_id, user_id)

        if company.owner_id != user_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this company")

        try:
            await self.session.delete(company)
            await self.session.commit()

            logging.info("Deleting user processed successfully")
            return company

        except Exception as e:
            logging.error(f"Error deleting user with ID {company_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error deleting company with ID {company_id}: {e}")

    async def get_company_members(self, company_id: str, page: int = 1, items_per_page: int = 10):
        try:
            offset = (page - 1) * items_per_page
            query = (select(CompanyMembers).filter(CompanyMembers.company_id == company_id)
                     .offset(offset).limit(items_per_page))
            result = await self.session.execute(query)
            logging.info("Getting member list processed successfully")
            members = result.scalars().all()
            user_ids = [member.user_id for member in members]
            members_with_user_data = []

            for user_id in user_ids:
                user_repo = UserService(self.session)
                user = await user_repo.get_by_id(user_id)
                if user:
                    member_data = {**user.__dict__}
                    members_with_user_data.append(member_data)

            return members_with_user_data

        except Exception as e:
            logging.error(f"Error retrieving member list: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving member list: {e}")

    async def remove_member(self, company_id: str, user_id: str, member_id: str):
        try:
            result = await self.session.execute(select(CompanyMembers).filter(
                CompanyMembers.company_id == company_id, CompanyMembers.user_id == member_id))
            member = result.scalars().first()
            await self.session.delete(member)
            await self.session.commit()

        except Exception as e:
            logging.error(f"Error retrieving company with ID {company_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving company with ID {company_id}: {e}")

        if not member:
            raise HTTPException(status_code=404, detail=f"User with ID {member_id} is not a member of this company")

        company_repo = CompanyService(self.session)
        company = await company_repo.get_by_id(company_id, user_id)

        if company.owner_id != user_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this company")

        if user_id == member_id:
            raise HTTPException(status_code=400, detail="Owner cannot remove yourself from the company")

        return f"User has been successfully removed from your company"

    async def leave_company(self, company_id: str, user_id: str):
        try:
            result = await self.session.execute(select(CompanyMembers).filter(
                CompanyMembers.company_id == company_id, CompanyMembers.user_id == user_id))
            member = result.scalars().first()
            await self.session.delete(member)
            await self.session.commit()
            company_repo = CompanyService(self.session)
            company = await company_repo.get_by_id(company_id, user_id)

        except Exception as e:
            logging.error(f"Error leaving company with ID {company_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error leaving company with ID {company_id}: {e}")

        if not member:
            raise HTTPException(status_code=404, detail="You are not a member of this company")

        if company.owner_id == user_id:
            raise HTTPException(status_code=400, detail="Company owner cannot leave the company")

        return f"You have left the company with ID {company_id}"
