from typing import Optional
import uuid 
from pydantic import BaseModel, Field
from typing import List

class DocumentModel(BaseModel):
    typetext: str 
    datetext: str 
    titletext: str 
    number: str 
    content: List[str] 


class UpdateDocumentModel(BaseModel):
    typetext: Optional[str]
    datetext: Optional[str]
    titletext: Optional[str]
    number: Optional[str]
    content: Optional[List[str]]


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
