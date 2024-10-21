import json
import threading
from time import sleep
from playwright.sync_api import sync_playwright
import urllib.request
import ddddocr
from b import crawl_courses_list
import re
import time

from py import password

# 读取用户信息
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# 获取所有用户
users = config['users']

# username = users[0]['username']
# password = users[0]['password']
base_url = "https://zswxy.yinghuaonline.com"


def download_image(url, filename):
    # 下载验证码图片并保存
    urllib.request.urlretrieve(url, filename)


# 将字符串的cookie转换为字典
def cookie2dict(cookie):
    # 先分割;符号
    cookie = cookie.split(';')
    cookie_dict = {}
    for item in cookie:
        # 再分割=符号
        cookie_dict[item.split('=')[0]] = item.split('=')[1]
    return cookie_dict


# 监听响应以捕获验证码图像
def handle_response(response,page):
    if "code" in response.url:  # 根据响应 URL 判断是否是验证码请求
        print(f"Response URLBBB: {response.url}, Status: {response.status}")
        if response.status == 200:
            print(f"Response URLBBBC: {response.url}, Status: {response.status}")
            # 保存验证码图像
            with open("captcha.png", "wb") as f:
                f.write(response.body())
            print("验证码图片已保存为 'captcha.png'")
            login_ocr(page)
        else:
            print('失败了？')

# 监听响应以捕获验证码图像
def handle_response_video(response,page):
    if "code" in response.url:  # 根据响应 URL 判断是否是验证码请求
        print(f"Response URLZZZ: {response.url}, Status: {response.status}")
        if "aa" in response.url:
            print(f"Response URLAA: {response.url}, Status: {response.status}")
            if response.status == 200:
                # 保存验证码图像
                with open("captcha.png", "wb") as f:
                    f.write(response.body())
                print("验证码图片已保存为 'captcha.png'")
                inputCode(page)
            else:
                print('失败了？')


def inputCode(page):
    sleep(5)
    ocr = ddddocr.DdddOcr(beta=True)
    with open("captcha.png", "rb") as image_file:
        image = image_file.read()
        result = ocr.classification(image)
    print(f"识别的验证码123: {result}")
    page.fill('input[placeholder="请输入验证码"]:nth-of-type(2)', result)
    page.click(".layui-layer-btn0")

def login(page, username, passwords):
    page.fill('#username', value=username)
    page.fill('#password', value=passwords)



def login_ocr(page):
        print("进行识别")
        sleep(4)
        # 验证码识别
        ocr = ddddocr.DdddOcr(beta=True)
        with open("captcha.png", "rb") as image_file:
            image = image_file.read()
            result = ocr.classification(image)
        print(f"识别的验证码: {result}")
        page.fill('#code', value=result)
        page.click(".btn")

        sleep(2)  # 等待页面加载
        # 检查是否有验证码错误提示
        page.click(".layui-layer-btn0")
        if page.query_selector("#layui-layer1") and page.is_visible("#layui-layer1 .layui-layer-btn0"):
            page.click("#layui-layer1 .layui-layer-btn0")
            print("验证码错误，重新尝试登录...")
            return

        # 登录成功检查
        try:
            page.wait_for_selector(".user-course", timeout=2000)
            print("登录成功！")
            # 获取登录后的 cookie
            cookies = page.context.cookies()
            print(f"登录后的 cookies: {cookies}")

            # 保存 cookies 到文件，方便后续使用
            with open("cookies.json", "w") as cookie_file:
                json.dump(cookies, cookie_file)
            return
        except:
            print("登录失败，验证码可能错误。重新尝试...")
            page.click("#layui-layer1 .layui-layer-btn0")
            return


def monitor_video_time(page):
    # 等待匹配部分类名的元素加载
    page.wait_for_selector('[class*="timetext"]')
    total_time = None

    while True:
        try:
            time_text = page.locator('[class*="timetext"]').inner_text()
            match = re.search(r'(\d{2}:\d{2})\s*/\s*(\d{2}:\d{2})', time_text)
            if match:
                current_time = match.group(1)
                total_time = match.group(2)
                print(f"当前播放时间: {current_time} / 总时长: {total_time}")

            if current_time == total_time:
                print("播放完成！")
                break

            time.sleep(1)

        except Exception as e:
            print(f"错误: {e}")
            break

    return total_time


def click_play_button(page):
    # 点击播放按钮和静音按钮
    try:
        play_button = page.query_selector('[data-title="点击播放"]')
        mute_button = page.query_selector('[data-title="点击静音"]')

        if play_button:
            play_button.click()
            print("成功点击播放按钮。")
            if mute_button:
                mute_button.click()
                print("成功点击静音按钮。")
            else:
                print("静音按钮未找到。")
        else:
            print("播放按钮未找到。")

    except Exception as e:
        print(f"点击播放按钮时出错: {e}")


def play_next_node(page, node_ids, current_index, base_url):
    # 播放下一个小节
    if current_index < len(node_ids) - 1:
        next_node_id = node_ids[current_index + 1]
        next_url = f"{base_url}/user/node?nodeId={next_node_id}"
        print(f"即将跳转到下一个小节: {next_url}")
        page.goto(next_url)
        page.wait_for_load_state('load')

        # 跳转到后下一个播放
        click_play_button(page)
        return True
    else:
        print("所有小节已播放完成。")
        return False


def start():
    with sync_playwright() as p:
        # 指定本地浏览器路径
        browser = p.chromium.launch(executable_path="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                                    headless=False)
        page = browser.new_page()
        page.goto('https://zswxy.yinghuaonline.com/user/node')
        username = users[0]['username']
        passwords = users[0]['password']
        # 监听请求
        page.on("request", lambda request: print(f"Request: {request.url}"))
        # 监听响应以捕获验证码图像
        page.on("response",lambda response: handle_response(response, page))
        login(page, username, passwords)
        # sleep(5)
        page.wait_for_selector(".user-course")  # 确保课程信息已经加载

        # 获取所有课程的 div
        courses = page.query_selector_all(".user-course .item")

        # 遍历每个课程并提取信息
        for course in courses:
            # 获取课程url
            course_link = course.query_selector(".name a")
            course_url = course_link.get_attribute("href")

            # 获取课程名称
            course_name = course.query_selector(".name a").inner_text()

            # 获取课程老师
            teacher = course.query_selector(".tags span").inner_text()

            # 获取学习进度
            progress = course.query_selector(".progress .txt").inner_text()

            # 获取课程学分
            credits = course.query_selector(".note .number .red").inner_text()

            # 获取开课时间
            start_time = course.query_selector(".time").inner_text()

            # 获取课程类型
            course_type = course.query_selector(".note .kind span").inner_text()

            # 打印提取的信息
            print(f"课程url: {course_url}")
            print(f"课程名称: {course_name}")
            print(f"授课教师: {teacher}")
            print(f"学习进度: {progress}")
            print(f"课程学分: {credits}")
            print(f"开课时间: {start_time}")
            print(f"课程类型: {course_type}")
            print("-" * 30)

            # 获取课程 id
            course_id = course_url.split('courseId=')[1]
            cookie = '__root_domain_v=.yinghuaonline.com; _qddaz=QD.129327079655855; token=sid.HAttnovayAhh0y7dTFomukOuQAVeY7; tgw_l7_route=951974fb5e8d768f7b1c8869abacfe8a; _qdda=3-1.2ppqli; _qddab=3-cod69x.m2fst830'
            cookie = cookie2dict(cookie)  # 将字符串的cookie转换为字典

            if progress != '100%':
                # 第一种处理方法：点击继续学习
                full_url = f"{base_url}{course_url}"

                # 第二种处理方法：获取学习记录中
                # c_status = page.query_selector('.status a')
                # c_record = c_status.get_attribute("href")
                # full_url = f"{base_url}{c_record}"

                # 跳转到新页面
                page.goto(full_url)

                # 等待页面加载完成
                page.wait_for_load_state('load')

                # 等待 "继续学习" 按钮出现
                page.wait_for_selector(".btn1")
                # 定位 "继续学习" 按钮
                # continue_button = page.query_selector(".btn1")
                continue_button = page.query_selector_all(".btn1")

                if continue_button and len(continue_button) > 1:
                    # print(continue_button[0]) # 问题答疑
                    # print(continue_button[1]) # 继续学习
                    continue_url = continue_button[1].get_attribute("href")

                    # 构建完整的 URL
                    full_continue_url = f"{base_url}{continue_url}"
                    # 直接跳转到 "继续学习" 链接
                    print(f"跳转到: {full_continue_url}")
                    page.goto(full_continue_url)

                    # 等待新页面加载完成
                    page.wait_for_load_state('load')

                    # 课程列表
                    # https://zswxy.yinghuaonline.com/user/node?nodeId=1457316
                    # nodeId = page.query_selector_all(".node-id")
                    # full_course_url = f"{base_url}{course_url}"

                    # 点击播放和静音按钮
                    click_play_button(page)

                    # 获取当前nodeid
                    init_nodeid = full_continue_url.split('nodeId=')[1]
                    print('获取当前nodeid', init_nodeid)

                    # 获取课程所有的nodeid（课程的小节）
                    node_ids = crawl_courses_list(course_id, cookie)

                    # 播放当前小节，并监控视频播放时间
                    current_index = node_ids.index(init_nodeid)

                    page.on("request", lambda request: print(f"Request: {request.url}"))

                    # 监听响应以捕获验证码图像
                    page.on("response", lambda response: handle_response_video(response, page))


                    while current_index < len(node_ids):
                        monitor_video_time(page)  # 监控视频播放时间

                        # 播放结束，切换到下一个小节
                        if not play_next_node(page, node_ids, current_index, base_url):
                            break  # 如果所有小节播放完成，跳出循环
                        current_index += 1
                else:
                    print("未找到 '继续学习' 按钮")
                    input("Press Enter to close the browser...")

                break  # 只处理第一个不满100%的课程，处理完后跳出循环

    # page.close()
    # browser.close()
    print("所有课程的学习进度均为100%。")


if __name__ == '__main__':
    start()
