from typing import Optional
import uuid 
from pydantic import BaseModel, Field

class TaskModel(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(...)
    completed: bool = False
    # Địhn nghĩa class default
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example":{
                "name": "Learn Farm stack",
                "completed": False
            }
        }



class UpdateTaskModel(BaseModel):
    name: Optional[str]
    complete: Optional[bool]
    
    class Config:
        schema_extra = {
            "example":{
                "name": "Learn Farm stack",
                "completed": True
            }
        }
