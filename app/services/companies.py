import logging
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Company
from app.schemas.company import CompanyBase, CompanyUpdate


class CompanyService:
    model = Company

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, page: int = 1, items_per_page: int = 10):
        try:
            offset = (page - 1) * items_per_page
            query = select(self.model).filter(self.model.company_is_visible == True).offset(offset).limit(items_per_page)
            result = await self.session.execute(query)

            logging.info("Getting company list processed successfully")
            return [CompanyBase(**user.__dict__) for user in result.scalars().all()]

        except Exception as e:

            logging.error(f"Error retrieving company list: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving company list: {e}")

    async def get_by_id(self, company_id: str):
        try:
            result = await self.session.execute(select(Company).filter(Company.company_id == company_id, Company.company_is_visible == True))

            if not result:
                raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")

            logging.info("Getting company processed successfully")
            return result.scalars().first()

        except Exception as e:
            logging.error(f"Error retrieving company with ID {company_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving company with ID {company_id}: {e}")

    async def create(self, company_data: CompanyBase, user_id):
        try:
            company_data.owner_id = user_id
            new_company = Company(**company_data.model_dump())
            self.session.add(new_company)

            try:
                await self.session.commit()
            except Exception as e:

                logging.error(f"Error committing transaction: {str(e)}")
                await self.session.rollback()
            finally:
                await self.session.close()
            logging.info(f"Company created: {new_company}")
            logging.info("Creating company processed successfully")
            return new_company

        except Exception as e:
            logging.error(f"Error creating company: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating company: {e}")

    async def update(self, company_id: str, company_data: CompanyUpdate, user_id: str):
        try:
            company = await self.get_by_id(company_id)

            if company.owner_id != user_id:
                raise HTTPException(status_code=403, detail="You are not the owner of this company")

            if not company:
                logging.error(f"Error retrieving company with ID {company_id}")
                raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")

            logging.info(company_data)
            company_dict = company_data.model_dump()
            updated_company_dict = {key: value for key, value in company_dict.items() if value is not None}
            query_company = update(self.model).where(self.model.company_id == company_id).values(updated_company_dict).returning(self.model.company_id)
            await self.session.execute(query_company)
            await self.session.commit()

            logging.info(f"Company update successful for company ID: {company_id}")
            return await self.get_by_id(company_id)

        except Exception as e:
            logging.error(f"Error during user update for company ID: {company_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error updating company: {e}")

    async def delete(self, company_id: str, user_id: str):
        try:
            company = await self.get_by_id(company_id)

            if company is None:
                raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")

            if company.owner_id != user_id:
                raise HTTPException(status_code=403, detail="You are not the owner of this company")

            await self.session.delete(company)
            await self.session.commit()

            logging.info("Deleting user processed successfully")
            return company

        except Exception as e:
            logging.error(f"Error deleting user with ID {company_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error deleting company with ID {company_id}: {e}")
