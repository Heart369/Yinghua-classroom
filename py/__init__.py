from time import sleep
from playwright.sync_api import sync_playwright
import urllib.request
# example.py
import ddddocr


username = "2024021597"
password = "1306433549aA"

def download_image(url, filename):
    """下载验证码图片并保存"""
    urllib.request.urlretrieve(url, filename)


def start():
    with sync_playwright() as p:
        # 指定本地浏览器路径
        browser = p.chromium.launch(executable_path="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                                    headless=False)
        page = browser.new_page()

        # 监听请求
        page.on("request", lambda request: print(f"Request: {request.url}"))

        # 监听响应以捕获验证码图像
        def handle_response(response):
            if "code" in response.url:  # 根据响应 URL 判断是否是验证码请求
                print(f"Response URL: {response.url}, Status: {response.status}")
                if response.status == 200:
                    # 你可以保存验证码图像
                    with open("captcha_response.png", "wb") as f:
                        f.write(response.body())
                    print("验证码图片已保存为 'captcha_response.png'")

        page.on("response", handle_response)
        # 打开目标网页
        page.goto('https://zswxy.yinghuaonline.com/user/node')
        page.fill('#username', value=username)
        page.fill('#password', value=password)
        # 等待用户输入，保持浏览器打开
        sleep(1)
        ocr = ddddocr.DdddOcr(beta=True)
        image = open("captcha_response.png", "rb").read()
        result = ocr.classification(image)
        print(result)
        page.fill('#code', value=result)
        page.click(".btn")
        input("Press Enter to close the browser...")


if __name__ == '__main__':
    start()
