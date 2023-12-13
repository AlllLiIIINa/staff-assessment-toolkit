import csv
import json
import logging
import os
from redis import asyncio
from sqlalchemy import select, func, desc, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings
from app.db.models import Result, Quiz
from app.depends.exceptions import ErrorGetRedisData, InvalidExportFormat, ErrorExport, NotOwnerOrAdminOrSelf, \
    NotSelf, ErrorUserResultCompany, ErrorUserResultCompanies, ErrorCompaniesResults, ErrorUsersResults, \
    ErrorQuizResults, ErrorCompanyAverageScoresOverTime, ErrorCompanyLastAttemptTimes, ErrorUserCompletedQuizzes, \
    ErrorUserResultsQuizzesOverTimes
from app.services.quizzes import check_company_owner_or_admin, QuizService


async def get_redis_data(quiz_id: str, user_id: str, question_id: str) -> dict:
    try:
        async with await asyncio.from_url(Settings.REDIS_URL) as redis_client:
            logging.info("Connecting redis processed successfully")
        redis_key = f"quiz_pass:{quiz_id}:{user_id}:question_{question_id}"
        logging.info(f"Redis key: {redis_key}")
        redis_data_str = await redis_client.get(redis_key)

        if redis_data_str is not None:
            redis_data = json.loads(redis_data_str)
            logging.info("Getting redis data processed successfully")
            await redis_client.close()
            logging.info("Disconnecting redis processed successfully")
            return redis_data

        else:
            logging.warning("Redis data not found for key: {redis_key}")
            raise ErrorGetRedisData(e="Redis data not found.")

    except Exception as e:
        logging.error(f"Error retrieving redis data: {e}")
        raise ErrorGetRedisData(e)


async def export_redis_data(user_id: str, quiz_id: str, question_id: str, export_format: str, filename: str):
    try:
        logging.info(f"Exported data for user_id: {user_id}, quiz_id: {quiz_id}, question_id: {question_id} to Redis")
        redis_data = await get_redis_data(quiz_id, user_id, question_id)
        logging.info(f" Redis_data: {redis_data}")
        file_path = os.path.join("C:/", "results", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if export_format.lower() == 'json':
            with open(file_path, 'a', encoding='utf-8') as json_file:
                json.dump(redis_data, json_file, ensure_ascii=False, indent=2)
            logging.info("Export redis data with JSON processed successfully")

        elif export_format.lower() == 'csv':
            with open(file_path, mode='a', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=redis_data.keys())

                if csv_file.tell() == 0:
                    writer.writeheader()

                writer.writerow(redis_data)
            logging.info("Export redis data with CSV processed successfully")

        else:
            logging.error(f"Invalid export format '{export_format}'. Supported formats: JSON, CSV.")
            raise InvalidExportFormat

    except ErrorGetRedisData as e:
        logging.error(f"Error exporting data: {e}")
        raise ErrorExport(e)


class ResultService:
    model = Result

    def __init__(self, session: AsyncSession):
        self.session = session
        self.quiz_service = QuizService(self.session)

    async def user_result_company(self, company_id: str, user_id: str, export_format: str, user: str) -> str:
        try:
            if str(user) != user_id or await check_company_owner_or_admin(self.session, str(user), company_id) != True:
                logging.error("You are not the owner or admin of this company")
                raise NotOwnerOrAdminOrSelf

            query = await self.session.execute(
                select(
                    self.model.result_user_id,
                    self.model.result_quiz_id,
                    func.avg(self.model.result_right_count / self.model.result_total_count).label('average_score'))
                .filter(self.model.result_user_id == user_id, self.model.result_company_id == company_id)
                .group_by(self.model.result_user_id, self.model.result_quiz_id)
            )
            user_scores = query.all()
            quiz_scores = {}

            for user in user_scores:
                quiz_id = user.result_quiz_id
                average_score = round(user.average_score, 2)

                if quiz_id not in quiz_scores:
                    quiz_scores[quiz_id] = {
                        'sum_scores': 0,
                        'count_scores': 0
                    }

                quiz_scores[quiz_id]['sum_scores'] += average_score
                quiz_scores[quiz_id]['count_scores'] += 1

                for question_id in await self.quiz_service.get_question_ids_for_quiz(quiz_id):
                    if export_format:
                        filename = f"user_score_company_results.{export_format.lower()}"
                        await export_redis_data(user_id, quiz_id, question_id, export_format, filename)

            result_str = ""
            company_average_score = sum(
                scores['sum_scores'] / scores['count_scores'] for scores in quiz_scores.values()) / len(quiz_scores)
            result_str += f"Average score in company with ID {company_id}: {company_average_score:.2f}"
            return result_str

        except Exception as e:
            logging.error(f"Error retrieving average scores for user in company with ID {company_id}: {e}")
            raise ErrorUserResultCompany(company_id, e)

    async def user_result_companies(self, user_id: str, export_format: str) -> str:
        try:
            query = await self.session.execute(
                select(
                    self.model.result_user_id,
                    self.model.result_company_id,
                    self.model.result_quiz_id,
                    func.avg(self.model.result_right_count / self.model.result_total_count).label('average_score'))
                .filter(self.model.result_user_id == user_id)
                .group_by(self.model.result_company_id, self.model.result_quiz_id, self.model.result_user_id)
            )
            user_scores = query.all()
            formatted_scores = {}
            result_str = ""

            for user in user_scores:
                user_id = user.result_user_id
                quiz_id = user.result_quiz_id

                if user_id not in formatted_scores:
                    formatted_scores[user_id] = {
                        'question_ids': {}
                    }

                if quiz_id not in formatted_scores[user_id]['question_ids']:

                    formatted_scores[user_id]['question_ids'][quiz_id] = await (
                        self.quiz_service.get_question_ids_for_quiz(quiz_id))

                for quiz_id, question_ids in formatted_scores[user_id]['question_ids'].items():
                    for question_id in question_ids:
                        if export_format:
                            filename = f"user_score_companies_results.{export_format.lower()}"
                            await export_redis_data(user_id, quiz_id, question_id, export_format, filename)

                average_across_companies = sum([score.average_score for score in user_scores]) / len(user_scores)
                result_str = round(average_across_companies, 2)
            return f"Your average score across all companies for user with ID {user_id}: {result_str:.2f}"

        except Exception as e:
            logging.error(f"Error retrieving average scores for user in companies: {e}")
            raise ErrorUserResultCompanies(e)

    async def company_results(self, company_id: str, export_format: str, user_id: str) -> str:
        try:
            await check_company_owner_or_admin(self.session, user_id, company_id)
            query = await self.session.execute(
                select(
                    self.model.result_user_id,
                    self.model.result_quiz_id,
                    func.avg(self.model.result_right_count / self.model.result_total_count).label('average_score')
                )
                .filter(self.model.result_company_id == company_id)
                .group_by(self.model.result_user_id, self.model.result_quiz_id)
                .order_by(desc(text('average_score')))
            )
            user_scores = query.all()
            formatted_scores = {}

            for user in user_scores:
                user_id = user.result_user_id
                quiz_id = user.result_quiz_id
                average_score = round(user.average_score, 2)

                if user_id not in formatted_scores:
                    formatted_scores[user_id] = {
                        'sum_scores': 0,
                        'count_scores': 0
                    }

                formatted_scores[user_id]['sum_scores'] += average_score
                formatted_scores[user_id]['count_scores'] += 1

                if export_format:
                    filename = f"company_results.{export_format.lower()}"
                    await export_redis_data(user_id, quiz_id, export_format, filename)

            result_str = ""

            for user_id, scores in formatted_scores.items():
                average_score = scores['sum_scores'] / scores['count_scores']
                result_str += f"{user_id}: {average_score:.2f}, "

            return f"Average scores for company with ID {company_id}: {result_str.rstrip(', ')}"

        except Exception as e:
            logging.error(f"Error retrieving results for all users: {e}")
            raise ErrorCompaniesResults(e)

    async def all_users_results(self) -> str:
        try:
            result = await self.session.execute(
                select(
                    self.model.result_user_id,
                    func.sum(self.model.result_right_count).label('total_right_count'),
                    func.sum(self.model.result_total_count).label('total_question_count'),
                    func.avg(self.model.result_right_count / self.model.result_total_count).label('average_score')
                )
                .group_by(self.model.result_user_id)
                .order_by(desc(text('average_score')))
            )
            user_scores = result.all()
            formatted_scores = {}

            for user in user_scores:
                user_id = user.result_user_id
                average_score = round(user.average_score, 2)

                if user_id not in formatted_scores:
                    formatted_scores[user_id] = {
                        'sum_scores': 0,
                        'count_scores': 0
                    }

                formatted_scores[user_id]['sum_scores'] += average_score
                formatted_scores[user_id]['count_scores'] += 1

            result_str = ""

            for user_id, scores in formatted_scores.items():
                average_score = scores['sum_scores'] / scores['count_scores']
                result_str += f"{user_id}: {average_score:.2f}, "

            return f"Average scores for all users: {result_str.rstrip(', ')}"

        except Exception as e:
            logging.error(f"Error retrieving average scores for all users: {e}")
            raise ErrorUsersResults(e)

    async def quiz_results_for_users(self, quiz_id: str, user_id: str, export_format: str) -> str:
        try:
            company_id = await self.session.scalar(select(Quiz.company_id).filter(Quiz.quiz_id == quiz_id))
            await check_company_owner_or_admin(self.session, user_id, company_id)
            query = await self.session.execute(
                select(
                    self.model.result_user_id,
                    func.avg(self.model.result_right_count / self.model.result_total_count).label('average_score')
                )
                .filter(self.model.result_quiz_id == quiz_id)
                .group_by(self.model.result_user_id)
            )
            formatted_scores = {}

            for user in query.all():
                user_id = user.result_user_id
                if user_id not in formatted_scores:
                    formatted_scores[user_id] = {
                        'question_ids': [],
                        'average_score': user.average_score
                    }
                formatted_scores[user_id]['question_ids'].extend(
                    await self.quiz_service.get_question_ids_for_quiz(quiz_id))

            result_str = ""

            for user_id, user_data in formatted_scores.items():
                for question_id in user_data['question_ids']:
                    if export_format:
                        filename = f"quiz_results.{export_format.lower()}"
                        await export_redis_data(user_id, quiz_id, question_id, export_format, filename)

                user_str = f"{user_id}: {user_data['average_score']:.2f}, "
                result_str += user_str

            return f"Average scores for quiz with ID {quiz_id}: {result_str.rstrip(', ')}"

        except Exception as e:
            logging.error(f"Error retrieving quiz results for all users: {e}")
            raise ErrorQuizResults(e)

    async def user_results_quizzes_over_times(self, user_id: str) -> str:
        try:
            result = await self.session.execute(
                select(
                    self.model.result_company_id,
                    self.model.result_quiz_id,
                    self.model.result_created_at,
                    func.avg(self.model.result_right_count / self.model.result_total_count).label('average_score')
                )
                .filter(self.model.result_user_id == user_id)
                .group_by(self.model.result_company_id, self.model.result_quiz_id, self.model.result_created_at)
                .order_by(desc(self.model.result_created_at))
            )
            formatted_scores = {}

            for user in result.all():
                company_id = user.result_company_id
                quiz_id = user.result_quiz_id
                date = user.result_created_at
                average_score = round(user.average_score, 2)

                if company_id not in formatted_scores:
                    formatted_scores[company_id] = {}

                if quiz_id not in formatted_scores[company_id]:
                    formatted_scores[company_id][quiz_id] = {}

                formatted_scores[company_id][quiz_id][date] = average_score

            result_str = ""

            for company_id, quiz_scores in formatted_scores.items():
                result_str += f" Company with ID {company_id}: "
                quiz_str = ", ".join([f"{quiz_id} {date} - {score}" for quiz_id, date_score in quiz_scores.items()
                                      for date, score in date_score.items()])
                result_str += f"{quiz_str}"

            return result_str.rstrip('')

        except Exception as e:
            logging.error(f"Error retrieving average scores for user for all quizzes with over time: {e}")
            raise ErrorUserResultsQuizzesOverTimes(e)

    async def user_completed_quizzes(self, user_id: str, user: str) -> dict:
        try:
            if str(user) != user_id:
                logging.error("You are not the owner or admin of this company")
                raise NotSelf

            query = await self.session.execute(
                select(self.model.result_quiz_id, func.max(self.model.result_created_at).label("last_completion_date"))
                .where(self.model.result_user_id == user_id)
                .group_by(self.model.result_quiz_id)
            )
            result_list = []

            for result in query.all():
                result_data = {
                    "quiz_id": result.result_quiz_id,
                    "last_completion_date": result.last_completion_date
                }
                result_list.append(result_data)

            user_result = {"user_id": user_id, "completed_quizzes": result_list}
            return user_result

        except Exception as e:
            logging.error(f"Error retrieving completed quizzes for user: {e}")
            raise ErrorUserCompletedQuizzes(e)

    async def company_average_scores_over_times(self, company_id: str, user: str, user_id: str = None) -> dict:
        try:
            await check_company_owner_or_admin(self.session, user, company_id)
            query = await self.session.execute(
                select(
                    self.model.result_created_at,
                    self.model.result_user_id,
                    self.model.result_quiz_id,
                    func.avg(self.model.result_right_count / self.model.result_total_count).label('average_score')
                )
                .where(
                    (self.model.result_company_id == company_id) &
                    (self.model.result_user_id == user_id) if user_id else (self.model.result_company_id == company_id)
                )
                .group_by(self.model.result_user_id, self.model.result_quiz_id, self.model.result_created_at)
                .order_by(self.model.result_user_id, self.model.result_quiz_id, desc(self.model.result_created_at))
            )
            result_data = []
            current_user_data = None

            for result in query.all():
                if current_user_data is None or current_user_data["user_id"] != result.result_user_id:
                    if current_user_data is not None:
                        result_data.append(current_user_data)

                    current_user_data = {
                        "user_id": result.result_user_id,
                        "quiz_id": result.result_quiz_id,
                        "average_scores": [{"average_score": result.average_score, "date": result.result_created_at}]
                    }

                else:
                    current_user_data["average_scores"].append(
                        {"average_score": result.average_score, "date": result.result_created_at})

            if current_user_data is not None:
                result_data.append(current_user_data)

            return {"company_id": company_id, "average_scores_over_time": result_data}

        except Exception as e:
            logging.error(f"Error retrieving average scores over time for company: {e}")
            raise ErrorCompanyAverageScoresOverTime(e)

    async def company_last_attempt_times(self, company_id: str, user_id: str) -> dict:
        try:
            await check_company_owner_or_admin(self.session, user_id, company_id)
            query = await self.session.execute(
                select(
                    self.model.result_user_id,
                    self.model.result_quiz_id,
                    func.max(self.model.result_created_at).label("last_attempt_time")
                )
                .where(
                    (self.model.result_company_id == company_id)
                )
                .group_by(self.model.result_user_id, self.model.result_quiz_id)
            )
            result_data = []

            for result in query.all():
                result_data.append({
                    "user_id": result.result_user_id,
                    "quiz_id": result.result_quiz_id,
                    "last_attempt_time": result.last_attempt_time
                })

            return {"company_id": company_id, "last_attempt_times": result_data}

        except Exception as e:
            logging.error(f"Error retrieving last attempt times for company: {e}")
            raise ErrorCompanyLastAttemptTimes(e)
