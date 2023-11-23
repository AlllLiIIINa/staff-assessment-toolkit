import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


class QuestionBase(BaseModel):
    question_id: UUID = Field(json_schema_extra={"primary_key": True, "unique": True}, default_factory=uuid4,
                              title="ID")
    question_text: str = Field(None, title="Text")
    question_answers: List[str] = Field(None, title="Answers")
    question_correct_answer: List[str] = Field(None, title="Correct Answer")
    quiz_id: UUID = Field(default=None, title="Quiz id")
    question_company_id: UUID = Field(default=None, title="QuestionCompany id")
    question_created_by: UUID = Field(default=None, title="Created by")
    question_updated_by: Optional[UUID] = Field(default=None, title="Created by")
    question_created_at: datetime.datetime = Field(None, title="Created")
    question_updated_at: datetime.datetime = Field(None, title="Updated")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "quiz_id": "",
                "question_text": "1. Do you like your company?",
                "question_answers": ["Yes", "No", "May be"],
                "question_correct_answer": ["Yes; No"]
            }
        }
    )


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_answers: Optional[str] = None
    question_correct_answer: Optional[str] = None
    question_updated_by: Optional[UUID] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "question_text": "",
                "question_answers": "",
                "question_correct_answer": "",
            }
        }
    )


class QuizBase(BaseModel):
    quiz_id: UUID = Field(json_schema_extra={"primary_key": True, "unique": True}, default_factory=uuid4, title="ID")
    quiz_name: str = Field(None, title="Name")
    quiz_title: Optional[str] = Field(None, title="Title")
    quiz_description: Optional[str] = Field(None, title="Description")
    quiz_frequency: Optional[int] = Field(None, title="Frequency")
    company_id: UUID = Field(default=None, title="QuizCompany id")
    quiz_created_by: UUID = Field(default=None, title="Created by")
    quiz_updated_by: Optional[UUID] = Field(default=None, title="Updated by")
    quiz_created_at: datetime.datetime = Field(None, title="Created")
    quiz_updated_at: datetime.datetime = Field(None, title="Updated")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "company_id": "",
                "quiz_name": "Quiz Name",
                "quiz_title": "Quiz Title",
                "quiz_description": "Quiz Description"
            }
        }
    )


class QuizUpdate(BaseModel):
    quiz_name: Optional[str] = None
    quiz_title: Optional[str] = None
    quiz_description: Optional[str] = None
    quiz_updated_by: Optional[UUID] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "quiz_name": "",
                "quiz_title": "",
                "quiz_description": ""
            }
        }
    )


class QuizPass(BaseModel):
    answers: Optional[List[str]] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                    "answers": [
                        "yes",
                        "yes; no"
                    ]
            }
        }
    )
