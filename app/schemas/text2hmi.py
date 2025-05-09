from pydantic import BaseModel, Field


class UserInput(BaseModel):
  """
  User input schema for text2hmi.
  """

  clientId: str = Field(
    ...,
    description="客户端ID.",
    min_length=1,
    max_length=250,
  )
  content: str = Field(
    ..., description="用户输入.", min_length=1, max_length=500
  )
  projectId: str = Field(
    ...,
    description="项目ID.",
    min_length=1,
    max_length=250,
  )
