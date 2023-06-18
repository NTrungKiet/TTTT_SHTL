from fastapi import FastAPI, File, UploadFile, Form, Body, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.templating import Jinja2Templates
from .config import settings
from .todo.routes import router as todo_router


import sys
sys.path.append(r"D:\TTTT\main.py")

import os
from main import OCR

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

@app.get("/upload/", response_class=HTMLResponse)
async def upload(request: Request):
    results = {"1":[
                    ["CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM","Độc lập - Tự do - Hạnh phúc"],
                    ["HỢP ĐỒNG CUNG CẤP GIẢI PHÁP PHẦN MỀM CNTT","HỢP ĐỒNG CUNG CÁP DỊCH VỤ QUẢN LÝ KHÁM CHỮA BỆNH VNPT HIS",
                    "Số: 230104-04/VNPT VNP. VLG KH TCDN/HĐVN TT TIT"],
                    ["Căn cử Bộ luật dân sự số 91/2015/QH13 và các văn bản hướng dẫn thi hành;",
                    "Căn cứ Luật thương mại số 36/2005/QH11 và các văn bản hướng dẫn thi hành;",
                    "Căn cứ Luật viễn thông số 41/2009/QH12 và các văn bản hướng dẫn thi hành;",
                    "Cấn cứ Luật công nghệ thông tin số 67/2006/QH11 và các văn bản hướng dẫn thi hành;",
                    "Căn cứ các văn bản pháp luật khác có liên quan;","Căn cứ khả năng và điều kiện của các bên,",
                    "Hợp đồng cung cấp giải pháp phần mềm NTT (\" Hợp đồng') được lập và ký kết ngày",
                    "144 tháng 01 năm 2023, tại Trung tâm Y tế huyện Mang Thít, giữa các Bên dưới đây","B. BÊN SỬ DỤNG: TRUNG TÂM Y TẾ HUYỆN MANG THÍT",
                    "Địa chỉ","Khóm 4, Thị trấn Cái Nhum, huyện Mang Thít, Tỉnh Vĩnh Long","Điện thoại","02703840012","Fax","02703930071",
                    "Tài khoản","9523.2.1015211?9527.2.1015211/3714.0.1015211","Tại","Kho bạc Nhà nước huyện Mang Thít","Mã số thuế","1500476127",
                    "Người đại diện: Ông Bùi MINH TUẤN","Chức vụ","GIÁM ĐỐC","(Trong Hợp đồng gọi tắt là ?Bên A?)","Và",
                    "II. BÊN CUNG CẤP: TRUNG TÂM KINH DOANH LONG","CHI NHÁNH TỔNG CÔNG TY DỊCH VỤ VIỄN THÔNG","Địa chỉ",
                    "Số 03 đường Trưng Nữ Vương, phường 1, Tp Vĩnh Long, tỉnh Vĩnh Long","Điện thoại","02703338005","Fax","0270 3838959",
                    "Tài khoản","7300201005166","Tại","Ngân hàng Nông nghiệp & Phát triển nông thôn tỉnh Vĩnh Long","Mã số thuế","0106869738-039",
                    "Người đại diện : Ông PHAN HOÀNG QUÂN","Chức vụ","PHÓ GIÁM ĐỐC","(Theo giấy ủy quyền số 03/GUQ-TTKD VLG ? NSTH, Ngày 03/01/2023)"],
                    ["(Trong Hợp đồng gọi tắt là ?Bên B?"],
                    ["Sau khi thỏa thuận và thống nhất, các bên đồng ý ký kết Hợp đồng với các điều tru",
                    "khoản và điều kiện như sau:","1/27"]
                    ]}
    content = {'request': request, 'results':results}
    return templates.TemplateResponse("upload.html", content)

@app.post('/save_ocr')
async def save_ocr()

# Endpoint /pdf_ocr
@app.post('/pdf_ocr')
async def pdf_ocr(file: UploadFile = File(...)):
    ocr = OCR()
    if file.filename.endswith('.pdf'):
        # Tạo thư mục pdf để chứa file upload nếu chưa tồn tại
        os.makedirs('pdf', exist_ok=True)
        # Lưu file vào thư mục pdf
        pdf_file = os.path.join('pdf', file.filename)
        with open(pdf_file, 'wb') as pdf:
            content = await file.read()
            pdf.write(content)
        return JSONResponse(content= {'results' : ocr._ocr_from_pdf(pdf_file)}, status_code=200)
    else:
        return JSONResponse(content={'results': 'error'}, status_code=401)
    

# {"results":{"1":[["CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM","Độc lập - Tự do - Hạnh phúc"],
# ["HỢP ĐỒNG CUNG CẤP GIẢI PHÁP PHẦN MỀM CNTT","HỢP ĐỒNG CUNG CÁP DỊCH VỤ QUẢN LÝ KHÁM CHỮA BỆNH VNPT HIS","Số: 
# 230104-04/VNPT VNP. VLG KH TCDN/HĐVN TT TIT"],
# ["Căn cử Bộ luật dân sự số 91/2015/QH13 và các văn bản hướng dẫn thi hành;",
# "Căn cứ Luật thương mại số 36/2005/QH11 và các văn bản hướng dẫn thi hành;",
# "Căn cứ Luật viễn thông số 41/2009/QH12 và các văn bản hướng dẫn thi hành;",
# "Cấn cứ Luật công nghệ thông tin số 67/2006/QH11 và các văn bản hướng dẫn thi hành;",
# "Căn cứ các văn bản pháp luật khác có liên quan;","Căn cứ khả năng và điều kiện của các bên,",
# "Hợp đồng cung cấp giải pháp phần mềm NTT (\" Hợp đồng') được lập và ký kết ngày",
# "144 tháng 01 năm 2023, tại Trung tâm Y tế huyện Mang Thít, giữa các Bên dưới đây","B. BÊN SỬ DỤNG: TRUNG TÂM Y TẾ HUYỆN MANG THÍT",
# "Địa chỉ","Khóm 4, Thị trấn Cái Nhum, huyện Mang Thít, Tỉnh Vĩnh Long","Điện thoại","02703840012","Fax","02703930071",
# "Tài khoản","9523.2.1015211?9527.2.1015211/3714.0.1015211","Tại","Kho bạc Nhà nước huyện Mang Thít","Mã số thuế","1500476127",
# "Người đại diện: Ông Bùi MINH TUẤN","Chức vụ","GIÁM ĐỐC","(Trong Hợp đồng gọi tắt là ?Bên A?)","Và",
# "II. BÊN CUNG CẤP: TRUNG TÂM KINH DOANH LONG","CHI NHÁNH TỔNG CÔNG TY DỊCH VỤ VIỄN THÔNG","Địa chỉ",
# "Số 03 đường Trưng Nữ Vương, phường 1, Tp Vĩnh Long, tỉnh Vĩnh Long","Điện thoại","02703338005","Fax","0270 3838959",
# "Tài khoản","7300201005166","Tại","Ngân hàng Nông nghiệp & Phát triển nông thôn tỉnh Vĩnh Long","Mã số thuế","0106869738-039",
# "Người đại diện : Ông PHAN HOÀNG QUÂN","Chức vụ","PHÓ GIÁM ĐỐC","(Theo giấy ủy quyền số 03/GUQ-TTKD VLG ? NSTH, Ngày 03/01/2023)"],
# ["(Trong Hợp đồng gọi tắt là ?Bên B?"],["Sau khi thỏa thuận và thống nhất, các bên đồng ý ký kết Hợp đồng với các điều tru",
# "khoản và điều kiện như sau:","1/27"]]}}
    