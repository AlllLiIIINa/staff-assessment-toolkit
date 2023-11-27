import logging
from datetime import datetime
from sqlalchemy import update, select, func, String, desc, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Quiz, CompanyMembers, Question, Result
from app.depends.exceptions import ErrorRetrievingList, AlreadyExistsQuiz, NotOwnerOrAdmin, ErrorCreatingQuiz, \
    QuizNotFound, ErrorRetrievingQuiz, NotMember, ErrorUpdatingQuiz, ErrorDeletingQuiz, ErrorPassQuiz, EmptyAnswer, \
    LessThen2Questions, QuizNotAvailable, NotOwnerOrAdminOrSelf, NotSelf, ErrorUserScoreCompany, \
    ErrorUserScoreCompanies, ErrorUsersScoreCompanies
from app.schemas.quiz import QuizBase, QuizUpdate, QuizPass


async def check_company_owner_or_admin(session: AsyncSession, user_id: str, company_id: str):
    result = await session.scalars(select(CompanyMembers).filter(
        CompanyMembers.user_id == user_id, CompanyMembers.company_id == company_id,
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

    async def get_all(self, company_id: str, user_id: str, page: int = 1, items_per_page: int = 10):
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

    async def get_by_id(self, quiz_id: str, user_id: str):
        try:
            result = await self.session.scalars(select(self.model).filter(self.model.quiz_id == quiz_id))
            quiz = result.first()

            if not quiz:
                logging.error(f"Quiz with ID {quiz_id} not found")
                raise QuizNotFound(quiz_id)

            quiz_company_id = await self.session.scalar(select(Quiz.company_id).filter(Quiz.quiz_id == quiz_id))
            await check_company_owner_or_admin(self.session, user_id, quiz_company_id)
            logging.info("Getting quiz processed successfully")
            return quiz

        except Exception as e:
            logging.error(f"Error retrieving quiz with ID {quiz_id}: {e}")
            raise ErrorRetrievingQuiz(e)

    async def create(self, user_id: str, quiz_data: QuizBase):
        try:
            result = await (self.session.scalars(select(self.model)
                                                 .filter(self.model.quiz_name == quiz_data.quiz_name)))

            if result.first():
                logging.error("Quiz already exist")
                raise AlreadyExistsQuiz

            quiz_company_id = await self.session.scalar(
                select(Quiz.company_id).filter(Quiz.quiz_id == quiz_data.quiz_id))
            await check_company_owner_or_admin(self.session, user_id, quiz_company_id)
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

    async def update(self, quiz_id: str, quiz_data: QuizUpdate, user_id: str):
        try:
            quiz_company_id = await self.session.scalar(select(Quiz.company_id).filter(Quiz.quiz_id == quiz_id))
            await check_company_owner_or_admin(self.session, user_id, quiz_company_id)
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
            quiz_company_id = await self.session.scalar(select(Quiz.company_id).filter(Quiz.quiz_id == quiz_id))
            await check_company_owner_or_admin(self.session, user_id, quiz_company_id)
            quiz = await self.get_by_id(quiz_id, user_id)
            await self.session.delete(quiz)
            await self.session.commit()
            logging.info("Deleting quiz processed successfully")
            return quiz

        except Exception as e:
            logging.error(f"Error deleting quiz with ID {quiz_id}: {e}")
            raise ErrorDeletingQuiz(e)

    async def quiz_pass(self, quiz_id: str, quiz_data: QuizPass, user_id: str):
        try:
            quiz_company_id = await self.session.scalar(select(Quiz.company_id).filter(Quiz.quiz_id == quiz_id))
            await check_company_owner_or_admin(self.session, user_id, quiz_company_id)

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

            right_count = 0
            total_count = len(quiz_questions)

            for index, (question, user_answer) in enumerate(zip(quiz_questions, quiz_data.answers)):
                correct_answers = [answer.lower() for answer in question.question_correct_answer]
                user_answers = user_answer.split(',')
                user_answers_lower = [ans.lower() for ans in user_answers]

                if any(ans in correct_answers for ans in user_answers_lower):
                    feedback.append(f"Question {index + 1}: Correct!")
                    right_count += 1
                else:
                    correct_answers_str = "; ".join(correct_answers)
                    feedback.append(
                        f"Question {index + 1}: Incorrect. Correct answer(s) is/are '{correct_answers_str}'"
                    )

            logging.info("Passing quiz processed successfully")
            query = await self.session.scalars(select(Result)
                                               .filter(Result.result_user_id == user_id,
                                                       Result.result_quiz_id == quiz_id))
            existing_result = query.first()
            logging.info(existing_result)

            if existing_result:
                existing_result.result_right_count = (existing_result.result_right_count + right_count) / 2
                logging.info(existing_result.result_right_count)
                existing_result.result_total_count = total_count
                existing_result.result_created_at = datetime.utcnow()
            else:
                result_instance = Result(
                    result_user_id=user_id,
                    result_company_id=quiz.company_id,
                    result_quiz_id=quiz_id,
                    result_created_at=datetime.utcnow(),
                    result_right_count=right_count,
                    result_total_count=total_count,
                )
                self.session.add(result_instance)

            await self.session.commit()

            return feedback

        except Exception as e:
            logging.error(f"Error passing quiz with ID {quiz_id}: {e}")
            raise ErrorPassQuiz(e)

    async def user_score_company(self, company_id: str, user_id: str, user: str):
        try:
            if str(user) != user_id or await check_company_owner_or_admin(self.session, str(user), company_id) != True:
                logging.error("You are not the owner or admin of this company")
                raise NotOwnerOrAdminOrSelf

            query = await self.session.scalars(
                select(func.avg(Result.result_right_count / Result.result_total_count)
                       .label('average_score'))
                .filter(Result.result_user_id == user_id, Result.result_company_id == company_id)
                .group_by(Result.result_quiz_id)
            )
            average_scores = query.all()
            result = round(sum(average_scores) / len(average_scores), 1) if average_scores else None
            return f"Your score in company with ID {company_id}: {result}"

        except Exception as e:
            logging.error(f"Error retrieving average scores for user in company with ID {company_id}: {e}")
            raise ErrorUserScoreCompany(company_id, e)

    async def user_score_companies(self, user_id: str, user: str):
        try:
            if user != user_id:
                logging.error("You are not the owner or admin of this company")
                raise NotSelf

            query = await self.session.scalars(
                select(func.avg(Result.result_right_count / Result.result_total_count)
                       .label('average_score'))
                .filter(Result.result_user_id == user_id)
                .group_by(Result.result_company_id)
            )

            average_scores = query.all()
            result = round(sum(average_scores) / len(average_scores), 1) if average_scores else None
            return f"Your average score across all companies: {result}"

        except Exception as e:
            logging.error(f"Error retrieving average scores for user in companies: {e}")
            raise ErrorUserScoreCompanies(e)

    async def score_all_users(self):
        try:
            result = await self.session.execute(
                select(
                    Result.result_user_id,
                    func.sum(Result.result_right_count).label('total_right_count'),
                    func.sum(Result.result_total_count).label('total_question_count'),
                    func.avg(Result.result_right_count / Result.result_total_count).label('average_score')
                )
                .group_by(Result.result_user_id, Result.result_company_id)
                .order_by(desc(text('average_score')))
            )

            user_scores = result.all()
            formatted_scores = []

            for user in user_scores:
                total_right_count = user.total_right_count or 0
                total_question_count = user.total_question_count or 0

                average_score = round(total_right_count / total_question_count, 3) if total_question_count > 0 else 0
                formatted_scores.append(f"{user.result_user_id}: {average_score}")

            result = ", ".join(formatted_scores) if formatted_scores else None
            return f"Average scores for all users in companies: {result}"

        except Exception as e:
            logging.error(f"Error retrieving average scores for all users in companies: {e}")
            raise ErrorUsersScoreCompanies(e)
