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
    ErrorUserScoreCompany, NotSelf, ErrorUserScoreCompanies, ErrorUsersScoreCompanies
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
            result_str = ""

            for user in user_scores:
                user_id = user.result_user_id
                quiz_id = user.result_quiz_id
                formatted_scores = {}

                if user_id not in formatted_scores:
                    formatted_scores[user_id] = {
                        'question_ids': {}
                    }

                if quiz_id not in formatted_scores[user_id]['question_ids']:
                    formatted_scores[user_id]['question_ids'][quiz_id] = await (
                        self.quiz_service.get_question_ids_for_quiz(quiz_id))

                for user_id, user_data in formatted_scores.items():
                    for quiz_id, question_ids in user_data['question_ids'].items():
                        for question_id in question_ids:
                            if export_format:
                                filename = f"user_score_company_results.{export_format.lower()}"
                                await export_redis_data(user_id, quiz_id, question_id, export_format, filename)

                average_score = round(user.average_score, 2)
                result_str = f"{user_id}: {average_score}; "
            return f"Your score in company with ID {company_id}: {result_str}"

        except Exception as e:
            logging.error(f"Error retrieving average scores for user in company with ID {company_id}: {e}")
            raise ErrorUserScoreCompany(company_id, e)

    async def user_result_companies(self, user_id: str, export_format: str, user: str) -> str:
        try:
            if str(user) != user_id:
                logging.error("You are not the owner or admin of this company")
                raise NotSelf

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
                result_str = str(round(average_across_companies, 2))

            return f"Your average score across all companies for user with ID {user_id}: {result_str}"

        except Exception as e:
            logging.error(f"Error retrieving average scores for user in companies: {e}")
            raise ErrorUserScoreCompanies(e)

    async def company_results(self, company_id: str, export_format: str, user_id: str) -> str:
        try:
            await check_company_owner_or_admin(self.session, user_id, company_id)
            query = await self.session.execute(
                select(
                    self.model.result_quiz_id,
                    self.model.result_user_id,
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

                if user_id not in formatted_scores:
                    formatted_scores[user_id] = {
                        'total_right_count': 0,
                        'total_question_count': 0,
                        'question_ids': {}
                    }

                if quiz_id not in formatted_scores[user_id]['question_ids']:
                    formatted_scores[user_id]['question_ids'][quiz_id] = await (
                        self.quiz_service.get_question_ids_for_quiz(quiz_id))

            result_str = ""

            for user_id, user_data in formatted_scores.items():
                for quiz_id, question_ids in user_data['question_ids'].items():
                    for question_id in question_ids:
                        if export_format:
                            filename = f"company_results.{export_format.lower()}"
                            await export_redis_data(user_id, quiz_id, question_id, export_format, filename)

                result_str = ", ".join(
                    [f"{score.result_user_id}: {round(score.average_score, 2)}" for score in user_scores])
            return f"Average scores for company with ID {company_id}: {result_str.strip()}"

        except Exception as e:
            logging.error(f"Error retrieving results for all users: {e}")
            raise ErrorUserScoreCompanies(e)

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
            formatted_scores = []

            for user in user_scores:
                total_right_count = user.total_right_count or 0
                total_question_count = user.total_question_count or 0
                average_score = round(total_right_count / total_question_count, 2) if total_question_count > 0 else 0
                formatted_scores.append(f"{user.result_user_id}: {average_score}")

            result_str = ", ".join(formatted_scores) if formatted_scores else None
            return f"Average scores for all users: {result_str}"

        except Exception as e:
            logging.error(f"Error retrieving average scores for all users: {e}")
            raise ErrorUsersScoreCompanies(e)

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
