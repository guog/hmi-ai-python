from fastapi import Form
from pydantic import BaseModel, Field


class UserInput(BaseModel):
  """
  User input schema for image2hmi.
  """

  clientId: str = Field(
    ...,
    description="客户端ID.",
    min_length=1,
    max_length=250,
  )
  projectId: str = Field(
    ...,
    description="项目ID.",
    min_length=1,
    max_length=250,
  )
  stream: bool = Field(
    ...,
    description="启用流式(stream)响应.",
  )

  @classmethod
  def as_form(
    cls,
    clientId: str = Form(...),
    projectId: str = Form(...),
    stream: bool = Form(...),
  ):
    return cls(clientId=clientId, projectId=projectId, stream=stream)
