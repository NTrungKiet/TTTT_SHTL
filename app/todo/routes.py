from fastapi import APIRouter, Form, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from .models import DocumentModel
from bson import ObjectId

router = APIRouter()

#Lấy ALL list
@router.get("/", response_description="List all Documents")
async def List_documents(request: Request):
    documents = []
    for doc in await request.app.mongodb["Documents"].find().to_list(length=None):
        doc['_id'] = str(doc['_id'])
        documents.append(doc)
    return documents

# Lấy theo id
@router.get("/{id}", response_description="Get document detail")
async def get_document(id: str, request: Request):
    if(document := await request.app.mongodb['Documents'].find_one({"_id": ObjectId(id)})) is not None:
        document["_id"] = str(document["_id"])
        return document
    
    raise HTTPException(status_code=404, detail= f"Tag {id} not found")

# Update

@router.put("/update_document/{id}", response_description="Update a document")
async def update_document(id:str, request:Request, number: str = Form(...), datetext: str = Form(...), typetext: str = Form(...), titletext: str = Form(...), 
                  content: str = Form(...)):
    content = content.replace('\r', '')
    content = content.split('\n')
    document = DocumentModel(number=number, datetext=datetext, typetext=typetext, titletext=titletext, content=content).dict()
    await request.app.mongodb['Documents'].update_one({"_id":ObjectId(id)}, {"$set": document})
    return 0
@router.delete('/delete_document/{id}', response_description="Delete a document")
async def delete_document(id:str, request:Request):
    await request.app.mongodb['Documents'].delete_one({"_id":ObjectId(id)})
    return 0


    