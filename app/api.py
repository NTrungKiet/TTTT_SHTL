from fastapi import FastAPI, File, UploadFile, Form, Request, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.templating import Jinja2Templates
from starlette.responses import Response
from .config import settings
from .todo.routes import router as todo_router
from typing import List
import copy
import re
import numpy as np
import json

import sys
sys.path.append(r"D:\TTTT\main.py")
# sys.path.append(r"D:\TTTT\app\todo\models.py")
from bson import ObjectId
import os
from main import OCR
from .todo.models import DocumentModel, UpdateDocumentModel

'''
import pymongo
# Khoi tao ket noi den mongodb
connection = pymongo.MongoClient('mongodb://127.0.0.1:27017')
myDB = connection["todo"]
col = myDB['Documents']

# Insert
abc = col.insert_one({'datetext': "03/07/2023"})
# Search
result = col.find({}, {'_id': 0})

for i in result:
    print(i)
'''

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# import htmldirectory
#"D:\TTTT\app\templates"
templates = Jinja2Templates(directory="D:/TTTT/app/templates")

app.include_router(todo_router, tags=["Documents"], prefix="/documents")

@app.on_event("startup")
async def startup_db():
    app.mongodb_client = AsyncIOMotorClient(settings.DB_URL)
    app.mongodb = app.mongodb_client[settings.DB_NAME]


@app.on_event("shutdown")
async def shutdown_db():
    app.mongodb_client.close()

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post('/pdf_ocr', response_class=HTMLResponse)
async def pdf_ocr(request: Request,file: UploadFile = File(...)):
    ocr = OCR()
    if file.filename.endswith('.pdf'):
        # Tạo thư mục pdf để chứa file upload nếu chưa tồn tại
        os.makedirs('pdf', exist_ok=True)
        # Lưu file vào thư mục pdf
        pdf_file = os.path.join('pdf', file.filename)
        with open(pdf_file, 'wb') as pdf:
            content = await file.read()
            pdf.write(content)
        global results
        results = ocr._ocr_from_pdf(pdf_file)
        return templates.TemplateResponse("upload.html", {'results':results, 'request':request})
        # return JSONResponse(content= {'results' : ocr._ocr_from_pdf(pdf_file)}, status_code=200)
    else:
        return JSONResponse(content={'results': 'error'}, status_code=401)


@app.post("/save", response_class=HTMLResponse)
async def save_ocr(request: Request ,inputs: List[str] = Form(...)):
    copied_results = copy.deepcopy(results)
    temp = []# lưu các text đẫ xóa
    # i = 1
    #=================================================== Cập nhật thông tin trước khi lưu =======================================
    while(len(inputs)>0):
        try:
            for page in copied_results:
                if(len(copied_results[page]) == 0):
                    copied_results.pop(page)
                elif(len(copied_results[page][0])>0):
                    result = copied_results[page][0]
                    index1 = results[page].index(temp+result) 
                    # print("index = ",index1)
                    if(inputs[0] != result[0]):
                        index2 = results[page][index1].index(result[0])
                        results[page][index1][index2] = inputs[0]
                        temp.append(inputs[0])
                        copied_results[page][0].pop(0)
                    else:
                        temp.append(result[0])
                        copied_results[page][0].pop(0)   
                    inputs.pop(0)
                else :
                    temp = []
                    copied_results[page].pop(0)
                break
        except Exception as e:
            return JSONResponse(content={'results': 'error'}, status_code=401)
#=====================================================Tiến thành lưu văn bản=======================================================================
    
    content = []
    copied_results = copy.deepcopy(results['1'])
    number = ''
    datetext = ''
    typetext = ''
    titletext = ''
    # try:
    while(len(copied_results)>0):
        if(len(copied_results[0])==0):
            copied_results.pop(0)
            continue
        text = copied_results[0][0]
        text =  text.lower()
        if(re.search(r"^số:(.*)", text)):
            number = re.search(r"^số:(.*)", text).group(1)
        elif(re.search( r'[^,]{0,11}, ngày (\d{1,2}) tháng (\d{1,2}) năm (\d{4})', text)):
            datetext = re.search( r'[^,]{0,11}, ngày (\d{1,2}) tháng (\d{1,2}) năm (\d{4})', text).group()
        elif(re.search(r'^(tờ trình|văn bản|công văn|quyết định|thông báo|thông tư)$', text)):
            typetext = re.search(r'^(tờ trình|văn bản|công văn|quyết định|thông báo|thông tư)$', text).group()
        elif(re.search(r'^(về việc|v/v|vlv)(.*)', text)):
            titletext+= ' '.join(copied_results[0])
            copied_results.pop(0)
            continue
        else:
            content.append(text)
        copied_results[0].pop(0)
    for key, values in results.items():
        if (key == '1'):
            continue
        for value in values:
            content+= value
    document = DocumentModel(typetext=typetext, number=number, titletext=titletext, datetext=datetext, content=content)
    await app.mongodb['Documents'].insert_one(document.dict())
    
    model = await app.mongodb['Documents'].find_one({"titletext":document.dict()['titletext']})
    ID = str(model['_id'])  
    url = f"/updated/{ID}"
    return Response(status_code=303, headers={"Location": url})


@app.get('/updated/{ID}', response_class=HTMLResponse)
async def updated(request: Request, ID: str):
    document = await app.mongodb['Documents'].find_one({"_id":ObjectId(ID)})
    document["_id"] = str(document["_id"])
    return templates.TemplateResponse("updated.html", {"request":request, "document":document, "ID":ID})


@app.get("/search")
async def search(request: Request, keyword: str):
    print(keyword)
    list_id = []
    for doc in await app.mongodb["Documents"].find({"titletext": {"$regex": keyword, "$options": "i"}}).to_list(length=None):
        list_id.append(str(doc['_id']))
    return {'list_id': list_id}

@app.get("/search-results")
async def search_results(request: Request, list_id: str):
    list_id = eval(list_id)
    documents = []
    for id in list_id:
        document = await request.app.mongodb['Documents'].find_one({"_id": ObjectId(id)})
        document['_id'] = str(document['_id'])
        documents.append(document)
    return templates.TemplateResponse("search_results.html", {"request": request, "documents": documents})





    
    