from uuid import UUID

from pydantic import BaseModel, ConfigDict

class ResumeResponse(BaseModel):
    id: UUID
    file_name: str
    file_path: str

    model_config = ConfigDict(from_attributes=True)