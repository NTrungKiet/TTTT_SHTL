from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from .models import TaskModel, UpdateTaskModel

router = APIRouter()

#Lấy ALL list
@router.get("/", response_description="List all tasks")
async def List_tasks(request: Request):
    tasks = []
    for doc in await request.app.mongodb["tasks"].find().to_list(length=100):
        tasks.append(doc)
    return tasks

# Lấy theo id
@router.get("/{id}", response_description="Get task detail")
async def get_task(id: str, request: Request):
    if(task := await request.app.mongodb['tasks'].find_one({"_id":id})) is not None:
        return task
    
    raise HTTPException(status_code=404, detail= f"Tag {id} not found")

# Update

@router.put("/{id}", response_description="Update a task")
async def update_task(id:str, request:Request, task: UpdateTaskModel = Body(...)):
    task = {k: v for k, v in task.dict().items() if v is not None}

    if(len(task) >= 1):
        update_task_resulut = await request.app.mongodb['tasks'].update_one({"_id":id}, {"$set": task})
        if (update_task_resulut.modified_count == 1):
            if(update_task := await request.app.mongodb['tasks'].find_one({"_id":id})) is not None:
                return update_task
            
    if(existing_task := await request.app.mongodb["tasks"].find_one({"_id":id})) is not None:
        return existing_task
    
    raise HTTPException(status_code=404, detail=f"task {id} not found")

@router.delete('/{id}', response_description="Delete a task")
async def delete_task(id:str, request:Request):
    delete_task = await request.app.mongodb['tasks'].delete_one({"_id":id})
    if delete_task.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={'tc':"Update completed"})
    
    raise HTTPException(status_code=404, detail=f"task {id} not found")


    