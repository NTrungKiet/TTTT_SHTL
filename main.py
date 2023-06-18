import os
import cv2
import numpy as np

from paddleocr import PaddleOCR
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from pdf2image import convert_from_path


from PIL import Image, ImageDraw, ImageFont


class OCR:
    def __init__(self) -> None:
        # VietOCR config
        self.config = Cfg.load_config_from_name('vgg_seq2seq')
        self.config['cnn']['pretrained']=False
        self.config['device'] = 'cpu'
        self.viet = Predictor(config=self.config)
        # PaddleOCR config
        self.paddle = PaddleOCR(use_angle_cls=True, lang='en')

    def sort(self, boxs):
        for i in range(0, len(boxs[0])):
            for j in range(i+1, len(boxs[0])):
                box_i = np.array(boxs[0][i], dtype=np.int32)
                box_j = np.array(boxs[0][j], dtype=np.int32)
                if(min(box_i[:,1])>min(box_j[:,1])):
                    temp = boxs[0][i]  
                    boxs[0][i]=boxs[0][j]
                    boxs[0][j]=temp
        return boxs
    
    def convert(self, box):
        # Chuẩn hóa tọa độ :
        # x bên trái:
        box[0][0] = box[3][0] = min(box[0][0], box[3][0]) 
        # y trên:
        box[0][1] = box[1][1] = min(box[0][1], box[1][1]) 
        # x bên phải:
        box[1][0] = box[2][0] = max(box[1][0], box[2][0])
        # y dưới:
        box[2][1] = box[3][1] = max(box[2][1], box[3][1]) 
        # print(box_of_ocr, '\n => \n', points_of_ocr) 
        return box 

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
            # trường hợp nhóm các dòng văn bản:
            # 1.lấy top của tọa độ hiện tại trừ cho bottom của tọa độ trước đó < 50.
            # 2. top bằng nhau hoặc sắp sĩ bằng nhau .
            # Do file pdf có thể bị lệch nên không lấy thẳng mà lấy chéo theo file pdf.
            if((current_box[0][1] - previous_box[3][1]) < 30):
                left_top = [min(previous_box[0][0],current_box[0][0]), min(previous_box[0][1], current_box[0][1])] 
                left_bottom = [min(previous_box[3][0], current_box[3][0]), max(previous_box[3][1], current_box[3][1])]
                right_top = [max(previous_box[1][0], current_box[1][0]), min(previous_box[1][1], current_box[1][1])]
                right_bottom = [max(previous_box[2][0], current_box[2][0]), max(previous_box[2][1], current_box[2][1])]
                new_boxs[j]= [left_top, right_top, right_bottom, left_bottom]
                flag = 1
            elif (flag == 0):
                j+=1
                new_boxs[j]=current_box
            i+=1
        new_boxs = np.delete(new_boxs, list(range(j+1, max_length)), axis = 0)
        return new_boxs.tolist()


    def ocr_by_vietocr(self, cropped_img):
        results = []
        boxs_of_ocr=self.paddle.ocr(cropped_img,cls=False, det=True, rec=False)
        boxs_of_ocr = self.sort(boxs_of_ocr)
        # pre_img = Image.fromarray(cropped_img)  
        # draw123 = ImageDraw.Draw(pre_img) 
        for box_of_ocr in boxs_of_ocr[0]:         

            # for i in range(0, len(box_of_ocr)):
            #     draw123.line(box_of_ocr[i] + (box_of_ocr[(i + 1) % len(box_of_ocr)]), fill='red', width=3)
            points_of_ocr = np.array(box_of_ocr, dtype=np.int32)
            points_of_ocr = self.convert(points_of_ocr)        
                            

            width_of_ocr = int(np.sqrt((points_of_ocr[1][0] - points_of_ocr[0][0])**2 + (points_of_ocr[1][1] - points_of_ocr[0][1])**2))
            height_of_ocr = int(np.sqrt((points_of_ocr[2][0] - points_of_ocr[1][0])**2 + (points_of_ocr[2][1] - points_of_ocr[1][1])**2))
            x_of_ocr = int(min(points_of_ocr[:,0]))
            y_of_ocr = int(min(points_of_ocr[:,1]))
                            

            cropped_img_of_ocr = cropped_img[y_of_ocr: y_of_ocr+height_of_ocr, x_of_ocr: x_of_ocr+width_of_ocr]
            pre_img_of_ocr = Image.fromarray(cropped_img_of_ocr)
            # pre_img_of_ocr.show()
            ocrResult = self.viet.predict(pre_img_of_ocr)
            ocrResult
            results.append(ocrResult)
        return results
    

    def _ocr_from_pdf(self, pdf_path):
        list_results = []
        pages = convert_from_path(pdf_path, poppler_path=r'D:\poppler-23.05.0\Library\bin')
        folder_name = os.path.join('pdf', os.path.basename(pdf_path)[:-4])
        for idx, page in enumerate(pages):
            os.makedirs(folder_name, exist_ok=True)
            page.save(os.path.join(folder_name, 'page_{}.jpg'.format(idx)), 'JPEG')
            try:
                # Đọc ảnh
                image = cv2.imread(os.path.join(folder_name, 'page_{}.jpg'.format(idx)))
                boxs = self.paddle.ocr(image, cls=False, det=True, rec=False)
#                 # Khởi tạo một đối tượng vẽ trên ảnh
                img = Image.open(os.path.join(folder_name, 'page_{}.jpg'.format(idx)))
                draw = ImageDraw.Draw(img)
#                #sắp xếp lại ocr
                boxs=self.sort(boxs)
#=========================                Phân đoạn văn bản               =============================
                new_boxs = self.text_partition(boxs)
                results = []
                for box in new_boxs:       
                    # Vẽ hình chữ nhật bao quanh từ hoặc đoạn văn bản
                    for i in range(0, len(box)):
                        draw.line(box[i] + (box[(i + 1) % len(box)]), fill='red', width=3)
                    # Chuyển tọa độ về kiểu int
                    points = np.array(box, dtype=np.int32)
                    # do là vẽ khung theo theo pdf nên có thể khung sẽ bị lệch. lúc này cần đưa khung ngay lại, không thì lúc cắt ảnh sẽ bị thiếu chữ.
                    points = self.convert(points)
                    # Tính toán kích thước của hình chữ nhật
                    width = int(np.sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2))
                    height = int(np.sqrt((points[2][0] - points[1][0])**2 + (points[2][1] - points[1][1])**2))
                    # Tọa độ góc trái trên của hình chữ nhật
                    x = int(min(points[:,0]))
                    y = int(min(points[:,1]))
                    # Cắt ảnh theo vùng đã tính toán được
                    cropped_img = image[y: y+height, x: x+width] 

#==================              Cắt ảnh rồi đem predict             ===========================        
#                 
                    results.append(self.ocr_by_vietocr(cropped_img))
                list_results.append({idx+1:results})
                # print(list_results)
                img.show()
                break
            except Exception as e:
                list_results.append({idx+1:e})
                # continue
                
        return list_results
# ocr = OCR()
# # readtext=ocr._ocr_from_pdf(r"C:\Users\ASUS\Downloads\VD1.pdf")
# # readtext=ocr._ocr_from_pdf(r"C:\Users\ASUS\Downloads\NLNKHMT12.pdf")
# # print(readtext)
# # C:\Users\ASUS/.cache\torch\hub\checkpoints\vgg19_bn-c79401a0.pth

# def typeCheck(text):
#     text =  text.lower()
#     dateText = ['ngày', 'tháng', 'năm']
#     typeText = ['tờ trình', 'văn bản', 'công văn', 'quyết định', 'thông báo', 'thông tư', 'hợp đồng', 'nghị định', 'nghị quyết']
#     titleText = ['về việc', 'v/v', 'vlv']
#     if len(text) > 300:
#         return 'noi_dung'
    
#     if 'số' in text:
#         return 'so_van_ban'
#     if any(word in text for word in dateText):
#         return 'ngay_van_ban'
#     if any(word in text for word in typeText):
#         return 'loai_van_ban'
#     if any(word in text for word in titleText):
#         return 'trich_yeu'
    
#     return 'noi_dung'


 
# #================================================================================================================================================

import uvicorn


if __name__ == '__main__':
    uvicorn.run('app.api:app', host= '0.0.0.0', port=8000, reload=True)
 