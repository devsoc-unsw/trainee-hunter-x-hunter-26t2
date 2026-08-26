from uuid import UUID

from fastapi import APIRouter

from deps import Conn, CurrentUser
from models import SubmitRequest, SubmitResponse

router = APIRouter(prefix="/questions", tags=["submissions"])


@router.post("/{question_id}/submit", response_model=SubmitResponse)
async def submit(question_id: UUID, body: SubmitRequest, conn: Conn, user: CurrentUser):
    # the big one. roughly:
    #   404 if the question doesn't exist
    #   get ALL test cases (not just samples)
    #   judge.run_submission(code, function_name, tests)
    #   if every test passed -> mark_solved
    #   if that was the first solve -> add_coins(rewards.coins_for_solve(...))
    #   return the results either way, they want to see which tests failed
    #
    # solving something twice pays nothing. mark_solved tells you which it is
    raise NotImplementedError
