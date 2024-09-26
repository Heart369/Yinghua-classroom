# example.py
import ddddocr

ocr = ddddocr.DdddOcr(beta=True)  # 切换为第二套ocr模型

image = open("img.png", "rb").read()
result = ocr.classification(image)
print(result)