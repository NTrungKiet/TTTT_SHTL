from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings
from .todo.routes import router as todo_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get('/')
def read_root():
    return {"hello":"world"}

app.include_router(todo_router, tags=["tasks"], prefix="/task")

@app.on_event("startup")
async def startup_db():
    app.mongodb_client = AsyncIOMotorClient(settings.DB_URL)
    app.mongodb = app.mongodb_client[settings.DB_NAME]


@app.on_event("shutdown")
async def shutdown_db():
    app.mongodb_client.close()



# Endpoint /pdf_ocr
# @app.post('/pdf_ocr')
# async def pdf_ocr(file: UploadFile = File(...)):
#     if file.filename.endswith('.pdf'):
#         # Tạo thư mục pdf để chứa file upload nếu chưa tồn tại
#         os.makedirs('pdf', exist_ok=True)
#         # Lưu file vào thư mục pdf
#         pdf_file = os.path.join('pdf', file.filename)
#         with open(pdf_file, 'wb') as pdf:
#             content = await file.read()
#             pdf.write(content)
#         return JSONResponse(content={'results': ocr._ocr_from_pdf(pdf_file)}, status_code=200)
#     else:
#         return JSONResponse(content={'results': 'error'}, status_code=401)