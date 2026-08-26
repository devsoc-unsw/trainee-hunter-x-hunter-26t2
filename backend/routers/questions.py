from uuid import UUID

from fastapi import APIRouter

from deps import Conn, CurrentUser
from models import QuestionDetail, QuestionSummary

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=list[QuestionSummary])
async def list_questions(conn: Conn, user: CurrentUser):
    # every question, with solved=True for the ones this user has done.
    # get the solved ids once with list_solved_ids, don't query per question
    raise NotImplementedError


@router.get("/{question_id}", response_model=QuestionDetail)
async def get_question(question_id: UUID, conn: Conn, user: CurrentUser):
    # one question + its SAMPLE test cases. 404 if it doesn't exist.
    # do not put the hidden test cases in the response, people can read it
    raise NotImplementedError
