from fastapi import FastAPI, File, UploadFile, Form, Body, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.templating import Jinja2Templates
from .config import settings
from .todo.routes import router as todo_router
from typing import List
import copy
import re
import numpy as np

import sys
sys.path.append(r"D:\TTTT\main.py")
# sys.path.append(r"D:\TTTT\app\todo\models.py")

import os
from main import OCR
from .todo.models import DocumentModel, TaskModel

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

app.include_router(todo_router, tags=["tasks"], prefix="/task")

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


@app.post("/save")
async def save_ocr(inputs: List[str] = Form(...)):
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
            titletext = ' '.join(copied_results[0])
            copied_results.pop(0)
            continue
        else:
            content.append(text)
        copied_results[0].pop(0)

    values = np.array([value for key, value in results.items() if key not in ['1']])
    content += list(values.reshape(-1))

    model = DocumentModel(typetext=typetext, number=number, titletext=titletext, datetext=datetext, content=content)
    await app.mongodb['Documents'].insert_one(model.dict())

    return JSONResponse(content={'results': results}, status_code=200)
    # return model



    
    