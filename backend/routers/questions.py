from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from deps import Conn, CurrentUser
from models import QuestionDetail, QuestionSummary
from queries.progress import list_solved_ids
from queries.questions import get_question as get_question_row
from queries.questions import get_test_cases
from queries.questions import list_questions as list_question_rows

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=list[QuestionSummary])
async def list_questions(conn: Conn, user: CurrentUser):
    # every question, with solved=True for the ones this user has done.
    # get the solved ids once with list_solved_ids, don't query per question
    questions = await list_question_rows(conn)
    solved_ids = await list_solved_ids(conn, user.id)
    return [
        QuestionSummary(**q, solved=q["id"] in solved_ids)
        for q in questions
    ]


@router.get("/{question_id}", response_model=QuestionDetail)
async def get_question(question_id: UUID, conn: Conn, user: CurrentUser):
    # one question + its SAMPLE test cases. 404 if it doesn't exist.
    # do not put the hidden test cases in the response, people can read it
    question = await get_question_row(conn, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    samples = await get_test_cases(conn, question_id, samples_only=True)
    solved_ids = await list_solved_ids(conn, user.id)

    return QuestionDetail(**question, samples=samples, solved=question_id in solved_ids)
