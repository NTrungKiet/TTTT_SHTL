import os
import cv2
import numpy as np

from paddleocr import PaddleOCR
from easyocr import Reader
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from pdf2image import convert_from_path


import uvicorn
from PIL import Image, ImageDraw, ImageFont
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask, render_template

class OCR:
    def __init__(self) -> None:
        # VietOCR config
        self.config = Cfg.load_config_from_name('vgg_seq2seq')
        self.config['cnn']['pretrained']=False
        self.config['device'] = 'cpu'
        self.viet = Predictor(config=self.config)
        # EasyOCR config
        self.easy = Reader(['vi'])
        # PaddleOCR config
        self.paddle = PaddleOCR(use_angle_cls=True, lang='en')

    def sort(self, boxs):
        for i in range(0, len(boxs[0])):
            # print('lần lặp {}'.format(i+1))
            # print('boxs là ', boxs[0])
            for j in range(i+1, len(boxs[0])):
                box_i = np.array(boxs[0][i], dtype=np.int32)
                # print('min hiện tại là ', min(box_i[:,1]))
                box_j = np.array(boxs[0][j], dtype=np.int32)
                if(min(box_i[:,1])>min(box_j[:,1])):
                    temp = boxs[0][i]  
                    boxs[0][i]=boxs[0][j]
                    boxs[0][j]=temp
                    # print('đổi ', min(box_i[:,1]), ' cho ', min(box_j[:,1]))
        return boxs

    def text_partition(self, boxs):
        previous_box = np.array(boxs[0][0])
        max_length = len(boxs[0])
        new_boxs = np.array(np.empty((max_length, 4, 2)), dtype=np.int32)
        i = 1
        j = 0
        new_boxs[j] = previous_box
        while( i < max_length):
            flag = 0
            if (i > 1):
                previous_box = np.array(new_boxs[j])
            current_box = np.array(boxs[0][i])
            # if(i==8)
            # trường hợp nhóm các dòng văn bản:
            # 1.lấy top của tọa độ hiện tại trừ cho bottom của tọa độ trước đó < 50.
            # 2. top bằng nhau hoặc sắp sĩ bằng nhau .
            # print('Lần thứ {}'.format(i))
            # print('TH1: ','TOP = ',min(current_box[:, 1]),' Bottom = ', max(previous_box[:, 1]), '=> ',min(current_box[:, 1]) - max(previous_box[:, 1]))
            if((min(current_box[:, 1]) - max(previous_box[:, 1])) < 30):
                flag = 1
            # print('TH2: ','Current_TOP = ',min(current_box[:, 1]),' Previous_Top = ', min(previous_box[:, 1]), '=> ',min(current_box[:,1]) - min(previous_box[:,1]))
            elif((min(current_box[:,1]) - min(previous_box[:,1])) <= 3 and (min(current_box[:,1]) - min(previous_box[:,1])) >=0):
                flag = 1
            if (flag == 0):
                j+=1
                new_boxs[j]=current_box
                # new_boxs.append(current_box.tolist())
            else:
                # print("previous_box = ",  previous_box)
                # print("current_box = ",  current_box)
                x_left = min(min(previous_box[:,0]), min(current_box[:,0])) 
                x_right = max(max(previous_box[:,0]), max(current_box[:,0]))
                y_top = min(min(previous_box[:,1]), min(current_box[:,1]))
                y_bottom = max(max(previous_box[:,1]), max(current_box[:,1]))
                new_boxs[j]=[[x_left,y_top], [x_right,y_top], [x_right, y_bottom], [x_left, y_bottom]]
                # print('box mới ', [[x_left,y_top], [x_right,y_top], [x_right, y_bottom], [x_left, y_bottom]])
                # new_boxs.append([[x_left,y_top], [x_right,y_top], [x_right, y_bottom], [x_left, y_bottom]])
            i+=1

        new_boxs = np.delete(new_boxs, list(range(j+1, max_length)), axis = 0)
        # print(len(new_boxs))
        return new_boxs.tolist()

    def _ocr_from_pdf(self, pdf_path):
        results = []
        pages = convert_from_path(pdf_path, poppler_path=r'D:\poppler-23.05.0\Library\bin')
        folder_name = os.path.join('pdf', os.path.basename(pdf_path)[:-4])
        for idx, page in enumerate(pages):
            os.makedirs(folder_name, exist_ok=True)
            page.save(os.path.join(folder_name, 'page_{}.jpg'.format(idx)), 'JPEG')
            try:
                image = cv2.imread(os.path.join(folder_name, 'page_{}.jpg'.format(idx)))
                boxs = self.paddle.ocr(image, cls=False, det=True, rec=False)

                # Đọc ảnh
                # img = Image.open(os.path.join(folder_name, 'page_{}.jpg'.format(idx)))

                # Khởi tạo một đối tượng vẽ trên ảnh
                # draw = ImageDraw.Draw(img)
                
                #sắp xếp lại ocr
                boxs=self.sort(boxs)
                
#=========================                Phân đoạn văn bản               =============================
                new_boxs = self.text_partition(boxs)

                for box in new_boxs:
                    # polygons = box        
                    # Vẽ hình chữ nhật bao quanh từ hoặc đoạn văn bản
                    # for i in range(0, len(polygons)):
                    #     draw.line(polygons[i] + (polygons[(i + 1) % len(polygons)]), fill='red', width=3)

                    # Chuyển tọa độ về kiểu int
                    points = np.array(box, dtype=np.int32)
                    # Tính toán kích thước của hình chữ nhật
                    width = int(np.sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2))
                    height = int(np.sqrt((points[2][0] - points[1][0])**2 + (points[2][1] - points[1][1])**2))

                    # Tọa độ góc trái trên của hình chữ nhật
                    x = int(min(points[:,0]))
                    y = int(min(points[:,1]))
                    # Cắt ảnh theo vùng đã tính toán được
                    # print(x,y, height, width)
                    cropped_img = image[y: y+height, x: x+width]
                    pre_img = Image.fromarray(cropped_img)  
                    # pre_img.show()
#==================              Cắt ảnh rồi đem predict             ===========================                        
                    boxs_of_ocr=self.paddle.ocr(cropped_img,cls=False, det=True, rec=False)
                    # print(boxs_of_ocr)

                    draw123 = ImageDraw.Draw(pre_img)   
                    for box_of_ocr in boxs_of_ocr[0]:          
                        polygons123 = box_of_ocr        

                        for i in range(0, len(polygons123)):
                            draw123.line(polygons123[i] + (polygons123[(i + 1) % len(polygons123)]), fill='red', width=3)
                        points_of_ocr = np.array(box_of_ocr, dtype=np.int32)

                        width_of_ocr = int(np.sqrt((points_of_ocr[1][0] - points_of_ocr[0][0])**2 + (points_of_ocr[1][1] - points_of_ocr[0][1])**2))
                        height_of_ocr = int(np.sqrt((points_of_ocr[2][0] - points_of_ocr[1][0])**2 + (points_of_ocr[2][1] - points_of_ocr[1][1])**2))
                        x_of_ocr = int(min(points_of_ocr[:,0]))
                        y_of_ocr = int(min(points_of_ocr[:,1]))
                        cropped_img_of_ocr = image[y_of_ocr: y_of_ocr+height_of_ocr, x_of_ocr: x_of_ocr+width_of_ocr]
                        pre_img_of_ocr = Image.fromarray(cropped_img_of_ocr)

                        ocrResult = self.viet.predict(pre_img_of_ocr)
                        results.append(ocrResult)

                    pre_img.show()
            except Exception as e:
                results.append(e)
            break
            # img.show()
        # print(results)
        return results
ocr = OCR()
readtext=ocr._ocr_from_pdf(r"C:\Users\ASUS\Downloads\VD1.pdf")
# readtext=ocr._ocr_from_pdf(r"C:\Users\ASUS\Downloads\NLNKHMT12.pdf")
print(readtext)


 
# #================================================================================================================================================
# # import uvicorn
# # from PIL import Image
# # from fastapi import FastAPI, File, UploadFile, Form
# # from fastapi.responses import JSONResponse
# # from fastapi.middleware.cors import CORSMiddleware
# # from fastapi.middleware.wsgi import WSGIMiddleware
# # from flask import Flask, render_template


# # flask_app = Flask(__name__)
# # app = FastAPI()

# # app.mount('/home', WSGIMiddleware(flask_app))

# # #http://127.0.0.1:8000/home/
# # @flask_app.get('/')
# # def blog_page():
# #     return "Nguyễn Trung Kiệt"






# # app.add_middleware(
# #         CORSMiddleware,
# #         allow_origins=['*'],
# #         allow_credentials=True,
# #         allow_methods=['*'],
# #         allow_headers=['*']
# #     )

# # # Endpoint /pdf_ocr
# # @app.post('/pdf_ocr')
# # async def pdf_ocr(file: UploadFile = File(...)):
# #     if file.filename.endswith('.pdf'):
# #         # Tạo thư mục pdf để chứa file upload nếu chưa tồn tại
# #         os.makedirs('pdf', exist_ok=True)
# #         # Lưu file vào thư mục pdf
# #         pdf_file = os.path.join('pdf', file.filename)
# #         with open(pdf_file, 'wb') as pdf:
# #             content = await file.read()
# #             pdf.write(content)
# #         return JSONResponse(content={'results': ocr._ocr_from_pdf(pdf_file)}, status_code=200)
# #     else:
# #         return JSONResponse(content={'results': 'error'}, status_code=401)

# # # http://127.0.0.1:8000/
# # @app.get('/')
# # def read_root():
# #     return {'Kiệt':'nè'}
# # if __name__ == '__main__':
# #     uvicorn.run(app, host='127.0.0.1', port=8000)
 
