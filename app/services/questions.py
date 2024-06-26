import logging
from typing import List, Union, Tuple, Dict
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Question, Company, CompanyMembers, Quiz
from app.depends.exceptions import NotOwnerOrAdmin, AlreadyExistsQuestion, ErrorCreatingQuestion, ErrorRetrievingList, \
    ErrorUpdatingQuestion, ErrorRetrievingQuestion, QuestionNotFound, ErrorDeletingQuestion, LessThen2Answers, NotMember
from app.schemas.quiz import QuestionBase, QuestionUpdate
from app.services.companies import CompanyService


async def check_company_owner_or_admin(session: AsyncSession, user_id: str, company_id: str):
    result = await session.scalars(select(CompanyMembers).filter(
        CompanyMembers.user_id == user_id, CompanyMembers.company_id == company_id,
        CompanyMembers.is_admin == True))

    if not result:
        logging.error("You are not the owner or admin of this company")
        raise NotOwnerOrAdmin

    return True


class QuestionService:
    model = Question

    def __init__(self, session: AsyncSession):
        self.session = session
        self.company_service = CompanyService(self.session)

    async def get_all(self, company_id: str, user_id: str, page: int = 1, items_per_page: int = 10) \
            -> List[QuestionBase]:
        try:
            await check_company_owner_or_admin(self.session, company_id, user_id)
            offset = (page - 1) * items_per_page
            questions = await self.session.scalars(select(self.model).filter(Company.company_id == company_id)
                                                   .offset(offset).limit(items_per_page))
            logging.info("Getting question list processed successfully")
            return [QuestionBase(**question.__dict__) for question in questions.all()]

        except Exception as e:
            logging.error(f"Error retrieving question list: {e}")
            raise ErrorRetrievingList(e)

    async def get_by_id(self, question_id: str, user_id: str) -> Question:
        try:
            result = await self.session.scalars(select(self.model).filter(self.model.question_id == question_id))
            question = result.first()

            if not question:
                logging.error(f"Quiz with ID {question_id} not found")
                raise QuestionNotFound(question_id)

            await check_company_owner_or_admin(self.session, question.question_company_id, user_id)
            logging.info("Getting quiz processed successfully")
            return question

        except Exception as e:
            logging.error(f"Error retrieving quiz with ID {question_id}: {e}")
            raise ErrorRetrievingQuestion(e)

    async def create(self, user_id: str, question_data: QuestionBase) -> Union[Tuple[Question, str], Question]:
        try:
            quiz_company_id = await self.session.scalar(select(Quiz.company_id)
                                                        .filter(Quiz.quiz_id == question_data.quiz_id))
            await check_company_owner_or_admin(self.session, quiz_company_id, user_id)
            exist_question = await self.session.scalars(select(self.model).filter(
                self.model.question_text == question_data.question_text))

            if exist_question.first():
                logging.error("Question already exist")
                raise AlreadyExistsQuestion

            if len(question_data.question_answers) < 2:
                logging.error("There should be at least 2 answers for question")
                raise LessThen2Answers

            question_data.question_created_by = user_id
            question_data.question_company_id = quiz_company_id
            new_question = self.model(**question_data.model_dump())
            self.session.add(new_question)
            await self.session.commit()
            logging.info(f"Question created: {new_question}")
            logging.info("Creating question processed successfully")
            quiz_question_count = await self.session.scalar(
                select(Question).filter(Question.quiz_id == question_data.quiz_id).count())

            if quiz_question_count == 0:
                comment = "Do not forget to add a second question, the quiz must have at least 2 questions"
                logging.warning(comment)
                return new_question, comment

            return new_question

        except Exception as e:
            logging.error(f"Error creating question: {e}")
            raise ErrorCreatingQuestion(e)

    async def update(self, question_id: str, question_data: QuestionUpdate, user_id: str) -> Question:
        try:
            result = await (self.session.scalars(
                select(self.model).filter(self.model.question_id == question_id)))
            question = result.first()
            await check_company_owner_or_admin(self.session, question.question_company_id, user_id)
            question_data.question_updated_by = user_id
            logging.info(question_data)
            question_dict = question_data.model_dump(exclude_none=True)
            await self.session.execute(update(self.model).where(self.model.question_id == question_id)
                                       .values(question_dict).returning(self.model.question_id))
            await self.session.commit()
            logging.info(f"Company update successful for question ID: {question_id}")
            return await self.get_by_id(question_id, user_id)

        except Exception as e:
            logging.error(f"Error during user update for question ID: {question_id}: {e}")
            raise ErrorUpdatingQuestion(e)

    async def delete(self, question_id: str, user_id: str):
        try:
            result = await self.session.scalars(
                select(self.model).filter(self.model.question_id == question_id))
            question = result.first()
            await check_company_owner_or_admin(self.session, question.question_company_id, user_id)
            await self.session.delete(question)
            await self.session.commit()
            logging.info("Deleting quiz processed successfully")

        except Exception as e:
            logging.error(f"Error deleting quiz with ID {question_id}: {e}")
            raise ErrorDeletingQuestion(e)

    async def quiz_questions(self, quiz_id: str, user_id: str) -> List[Dict[str, Union[str, List[str]]]]:
        try:
            quiz_company_id = await self.session.scalar(select(Quiz.company_id).filter(Quiz.quiz_id == quiz_id))
            result = await self.session.scalars(select(CompanyMembers)
                                                .filter(CompanyMembers.user_id == user_id,
                                                        CompanyMembers.company_id == quiz_company_id))

            if not result.first():
                logging.error("You are not the member of this company")
                raise NotMember

            result = await self.session.scalars(select(Question).filter(Question.quiz_id == quiz_id))
            quiz_questions = result.all()

            if not quiz_questions:
                logging.error("No questions found for the given quiz ID")
                raise QuestionNotFound(quiz_id="")

            questions_with_answers = []

            for question in quiz_questions:
                question_data = {
                    "question_text": question.question_text,
                    "question_answers": question.question_answers,
                }
                questions_with_answers.append(question_data)

            return questions_with_answers

        except Exception as e:
            logging.error(f"Error retrieving questions for quiz with ID {quiz_id}: {e}")
            raise ErrorRetrievingQuestion(e)
