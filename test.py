# import re

# text = "số: 123213/CV-BGDĐT- asdawdwdasd ádasdasd, ngày 10/05/2022"
# pattern = r"^số:(.*)"
# match = re.search(pattern, text)
# if re.search(r"^số:(.*)", text):
#     content = match.group(1)
#     print(content)

# import re

# pattern = r'[^,]{0,11}, ngày (\d{1,2}) tháng (\d{1,2}) năm (\d{4})'
# text = 'Quảng Ngãi, ngày 10 tháng 06 năm 2022'
# match = re.search(pattern, text)

# if match:
#     print(match.group())

# import re

# pattern = r'^(tờ trình|văn bản|công văn|quyết định|thông báo|thông tư)$'
# text = 'tờ trình'
# match = re.search(pattern, text)

# if match:
#     content = match.group()
#     print(content)  # Kết quả: tờ trình

# import re

# pattern = r'^(về việc|v/v|vlv)(.*)'
# text = 'Về Việc Hướng dẫn mức chi tạo lập thông tin điện từ nhằm duy trì hoạt động thường'
# text = text.lower()
# print(text)
# match = re.search(pattern, text)
# print(match)

# if match:
#     content = match.group()
#     print(content)  # Kết quả: v/v

# import numpy as np

# # Mảng 3 chiều
# my_array_3d = np.array([[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]])

# # Chuyển đổi mảng 3 chiều thành mảng 1 chiều
# my_array_1d = my_array_3d.reshape(-1)

# print(my_array_1d)

import uuid
from fastapi import FastAPI
from pymongo import MongoClient
from bson import Binary

app = FastAPI()
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["your_database"]
collection = db["your_collection"]

# @app.post("/create_document")
# async def create_document():
    # Tạo một UUID ngẫu nhiên
text = [["Nguyễn Trung Kiệt"], ["Nguyễn Trung Tín"]]
A = []
B = [i for i in text[0]]
A.append(B)
for i in A:
    print(i)