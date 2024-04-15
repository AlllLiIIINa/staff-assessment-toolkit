import logging
from datetime import datetime
from typing import List, Union
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Quiz, CompanyMembers, Question
from app.depends.exceptions import ErrorRetrievingList, AlreadyExistsQuiz, NotOwnerOrAdmin, ErrorCreatingQuiz, \
    QuizNotFound, ErrorRetrievingQuiz, NotMember, ErrorUpdatingQuiz, ErrorDeletingQuiz, ErrorPassQuiz, EmptyAnswer, \
    LessThen2Questions, QuizNotAvailable
from app.schemas.quiz import QuizBase, QuizUpdate, QuizPass


async def check_company_owner_or_admin(session: AsyncSession, user_id: str, quiz_id: str):
    quiz_company_id = await session.scalar(select(Quiz.company_id).filter(Quiz.quiz_id == quiz_id))
    result = await session.scalars(select(CompanyMembers).filter(
        CompanyMembers.user_id == user_id, CompanyMembers.company_id == quiz_company_id,
        CompanyMembers.is_admin == True))
    logging.debug(f"result: {result}")

    if not result:
        logging.error("You are not the owner or admin of this company")
        raise NotOwnerOrAdmin

    return True


class QuizService:
    model = Quiz

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, company_id: str, user_id: str, page: int = 1, items_per_page: int = 10) -> List[QuizBase]:
        try:
            offset = (page - 1) * items_per_page
            result = await self.session.scalars(select(CompanyMembers)
                                                .filter(CompanyMembers.user_id == user_id,
                                                        CompanyMembers.company_id == company_id))
            if not result.first():
                logging.error("You are not member of this company")
                raise NotMember

            quizzes = await self.session.scalars(select(self.model).filter(self.model.company_id == company_id)
                                                 .offset(offset).limit(items_per_page))
            logging.info("Getting quiz list processed successfully")
            return [QuizBase(**quiz.__dict__) for quiz in quizzes.all()]

        except Exception as e:
            logging.error(f"Error retrieving quiz list: {e}")
            raise ErrorRetrievingList(e)

    async def get_by_id(self, quiz_id: str, user_id: str) -> Quiz:
        try:
            result = await self.session.scalars(select(self.model).filter(self.model.quiz_id == quiz_id))
            quiz = result.first()

            if not quiz:
                logging.error(f"Quiz with ID {quiz_id} not found")
                raise QuizNotFound(quiz_id)

            await check_company_owner_or_admin(self.session, user_id, quiz_id)
            logging.info("Getting quiz processed successfully")
            return quiz

        except Exception as e:
            logging.error(f"Error retrieving quiz with ID {quiz_id}: {e}")
            raise ErrorRetrievingQuiz(e)

    async def create(self, user_id: str, quiz_data: QuizBase) -> Quiz:
        try:
            result = await (self.session.scalars(select(self.model)
                                                 .filter(self.model.quiz_name == quiz_data.quiz_name)))

            if result.first():
                logging.error("Quiz already exist")
                raise AlreadyExistsQuiz

            await check_company_owner_or_admin(self.session, user_id, str(quiz_data.quiz_id))
            quiz_data.quiz_created_by = user_id
            new_quiz = self.model(**quiz_data.model_dump())
            self.session.add(new_quiz)
            await self.session.commit()
            logging.info(f"Quiz created: {new_quiz}")
            logging.info("Creating quiz processed successfully")
            return new_quiz

        except Exception as e:
            logging.error(f"Error creating quiz: {e}")
            raise ErrorCreatingQuiz(e)

    async def update(self, quiz_id: str, quiz_data: QuizUpdate, user_id: str) -> Quiz:
        try:
            await check_company_owner_or_admin(self.session, user_id, quiz_id)
            quiz_data.quiz_updated_by = user_id
            logging.info(quiz_data)
            quiz_dict = quiz_data.model_dump(exclude_none=True)
            await self.session.execute(update(self.model).where(self.model.quiz_id == quiz_id)
                                       .values(quiz_dict).returning(self.model.quiz_id))
            await self.session.commit()
            logging.info(f"Company update successful for quiz ID: {quiz_id}")
            return await self.get_by_id(quiz_id, user_id)

        except Exception as e:
            logging.error(f"Error during user update for quiz ID: {quiz_id}: {e}")
            raise ErrorUpdatingQuiz(e)

    async def delete(self, quiz_id: str, user_id: str):
        try:
            await check_company_owner_or_admin(self.session, user_id, quiz_id)
            quiz = await self.get_by_id(quiz_id, user_id)
            await self.session.delete(quiz)
            await self.session.commit()
            logging.info("Deleting quiz processed successfully")

        except Exception as e:
            logging.error(f"Error deleting quiz with ID {quiz_id}: {e}")
            raise ErrorDeletingQuiz(e)

    async def quiz_pass(self, quiz_id: str, quiz_data: QuizPass, user_id: str) -> List[Union[str, List[str]]]:
        try:
            await check_company_owner_or_admin(self.session, user_id, quiz_id)

            if not quiz_data.answers:
                logging.error("Answer is empty")
                raise EmptyAnswer

            result = await self.session.scalars(select(Question).filter(Question.quiz_id == quiz_id))
            quiz_questions = result.all()

            if len(quiz_questions) < 2:
                logging.error("There should be at least 2 questions in the quiz")
                raise LessThen2Questions

            feedback = []
            quiz = await self.get_by_id(quiz_id, user_id)

            if quiz.quiz_frequency is not None:
                quiz_start_time = datetime.now()
                logging.info(f"Current time: {quiz_start_time}")
                logging.info(f"Quiz frequency: {quiz.quiz_frequency}")

                if quiz_start_time > quiz.quiz_frequency:
                    logging.error("Quiz is not available at the moment")
                    raise QuizNotAvailable

            for index, (question, user_answer) in enumerate(zip(quiz_questions, quiz_data.answers)):
                correct_answers = [answer.lower() for answer in question.question_correct_answer]
                user_answers = user_answer.split(',')
                user_answers_lower = [ans.lower() for ans in user_answers]

                if any(ans in correct_answers for ans in user_answers_lower):
                    feedback.append(f"Question {index + 1}: Correct!")
                else:
                    correct_answers_str = "; ".join(correct_answers)
                    feedback.append(
                        f"Question {index + 1}: Incorrect. Correct answer(s) is/are '{correct_answers_str}'"
                    )

            return feedback

        except Exception as e:
            logging.error(f"Error passing quiz with ID {quiz_id}: {e}")
            raise ErrorPassQuiz(e)
