from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.core.text2hmi import create_paper
from app.schemas.text2hmi import UserInput

router = APIRouter()


@router.post(
  "/text2hmi", tags=["demo"], description="这是一个DEMO将文本转换为HMI图纸"
)
async def text2hmi(
  request: Request,
  user_input: UserInput,
):
  return StreamingResponse(
    create_paper(user_input.content), media_type="text/event-stream"
  )
