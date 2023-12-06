from http import HTTPStatus
from fastapi import APIRouter, Depends, Query
from app.db.models import User
from app.depends.depends import get_quiz_service, get_question_service
from app.schemas.quiz import QuizBase, QuizUpdate, QuestionUpdate, QuestionBase, QuizPass
from app.services.auth import AuthService
from app.services.questions import QuestionService
from app.services.quizzes import QuizService, get_redis_data

quiz_router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@quiz_router.get("/", operation_id="quizzes", )
async def quiz_list(company_id: str, user: User = Depends(AuthService.get_current_user),
                    page: int = Query(default=1, description="Page number", ge=1),
                    quiz_per_page: int = Query(default=10, description="Items per page", le=100),
                    quiz_service: QuizService = Depends(get_quiz_service)):
    return await quiz_service.get_all(company_id, user.user_id, page, quiz_per_page)


@quiz_router.get("/{quiz_id}", operation_id="quiz_get_by_id")
async def quiz_get_by_id(quiz_id: str, user: User = Depends(AuthService.get_current_user),
                         quiz_service: QuizService = Depends(get_quiz_service)):
    return await quiz_service.get_by_id(quiz_id, user.user_id)


@quiz_router.post("/", status_code=HTTPStatus.CREATED, operation_id="quiz_create")
async def quiz_create(quiz_data: QuizBase, user: User = Depends(AuthService.get_current_user),
                      quiz_service: QuizService = Depends(get_quiz_service)):
    return await quiz_service.create(user.user_id, quiz_data)


@quiz_router.put("/{quiz_id}", operation_id="quiz_update")
async def quiz_update(quiz_id: str, quiz_data: QuizUpdate, user: User = Depends(AuthService.get_current_user),
                      quiz_service: QuizService = Depends(get_quiz_service)):
    return await quiz_service.update(quiz_id, quiz_data, user.user_id)


@quiz_router.delete("/{quiz_id}", status_code=HTTPStatus.NO_CONTENT, operation_id="quiz_delete")
async def quiz_delete(quiz_id: str, user: User = Depends(AuthService.get_current_user),
                      quiz_service: QuizService = Depends(get_quiz_service)):
    return await quiz_service.delete(quiz_id, user.user_id)


@quiz_router.get("/questions/", operation_id="get_questions", )
async def question_list(company_id: str, user: User = Depends(AuthService.get_current_user),
                        page: int = Query(default=1, description="Page number", ge=1),
                        question_per_page: int = Query(default=10, description="Items per page", le=100),
                        question_service: QuestionService = Depends(get_question_service)):
    return await question_service.get_all(company_id, user.user_id, page, question_per_page)


@quiz_router.get("/{question_id}/", operation_id="question_get_by_id")
async def question_get_by_id(question_id: str, user: User = Depends(AuthService.get_current_user),
                             question_service: QuestionService = Depends(get_question_service)):
    return await question_service.get_by_id(question_id, user.user_id)


@quiz_router.post("/question", status_code=HTTPStatus.CREATED, operation_id="question_create")
async def question_create(question_data: QuestionBase, user: User = Depends(AuthService.get_current_user),
                          question_service: QuestionService = Depends(get_question_service)):
    return await question_service.create(user.user_id, question_data)


@quiz_router.put("/{question_id}/", operation_id="question_update")
async def question_update(question_id: str, question_data: QuestionUpdate,
                          user: User = Depends(AuthService.get_current_user),
                          question_service: QuestionService = Depends(get_question_service)):
    return await question_service.update(question_id, question_data, user.user_id)


@quiz_router.delete("/{question_id}/", status_code=HTTPStatus.NO_CONTENT, operation_id="question_delete")
async def question_delete(question_id: str, user: User = Depends(AuthService.get_current_user),
                          question_service: QuestionService = Depends(get_question_service)):
    return await question_service.delete(question_id, user.user_id)


@quiz_router.get("/{quiz_id}/questions", operation_id="get_quiz_questions")
async def quiz_questions(quiz_id: str, user: User = Depends(AuthService.get_current_user),
                         question_service: QuestionService = Depends(get_question_service)):
    return await question_service.quiz_questions(quiz_id, user.user_id)


@quiz_router.post("/{quiz_id}/quiz", operation_id="question_pass")
async def quiz_pass(quiz_id: str, quiz_data: QuizPass, user: User = Depends(AuthService.get_current_user),
                    quiz_service: QuizService = Depends(get_quiz_service)):
    return await quiz_service.quiz_pass(quiz_id, quiz_data, user.user_id)


@quiz_router.get("/score/company", operation_id="user_quiz_score_company")
async def user_score_company(company_id: str, user_id: str, export_format: str = None, user: User = Depends(AuthService.get_current_user),
                             quiz_service: QuizService = Depends(get_quiz_service)):
    return await quiz_service.user_score_company(company_id, user_id, export_format, user.user_id)


@quiz_router.get("/score/companies", operation_id="user_quiz_score_companies")
async def user_score_companies(user_id: str, export_format: str = None, user: User = Depends(AuthService.get_current_user),
                               quiz_service: QuizService = Depends(get_quiz_service)):
    return await quiz_service.user_score_companies(user_id, export_format, user.user_id)


@quiz_router.get("/score/company/", operation_id="company_rating")
async def company_rating(company_id: str, export_format: str = None, quiz_service: QuizService = Depends(get_quiz_service),
                         user: User = Depends(AuthService.get_current_user)):
    return await quiz_service.company_results(company_id, export_format, user.user_id)


@quiz_router.get("/score/rating", operation_id="user_quiz_rating")
async def user_rating(quiz_service: QuizService = Depends(get_quiz_service)):
    return await quiz_service.score_all_users()


@quiz_router.get("/score/redis", operation_id="user_redis")
async def get_redis_data_(quiz_id: str, user_id: str, question_id: str):
    return await get_redis_data(quiz_id, user_id, question_id)
