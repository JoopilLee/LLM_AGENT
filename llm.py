from pydantic import BaseModel, Field

class ResponseFormatter(BaseModel):
    """Always use this tool to structure your response to the user."""
    answer: str = Field(description="The answer to the user's question")
    followup_question: str = Field(description="A followup question the user could ask")

model_with_structure = model.with_structured_output(schema)

structured_output = model_with_structure.invoke(user_input)