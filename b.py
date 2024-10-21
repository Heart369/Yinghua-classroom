import time
import requests
import re
from bs4 import BeautifulSoup


def crawl_courses_list(courseId, cookie):
    cookie = "; ".join([f"{item}={cookie[item]}" for item in cookie])
    host = 'https://zswxy.yinghuaonline.com'
    url = f"{host}/user/course?courseId={courseId}"
    page_index = 1
    # cookie = '__root_domain_v=.yinghuaonline.com; _qddaz=QD.129327079655855; token=sid.HAttnovayAhh0y7dTFomukOuQAVeY7; _qddab=3-zac3cp.m2fm5ys8; tgw_l7_route=1da6220a8c6aee8fae7fcb8ec6e1299a'
    current_timestamp = int(time.time())
    # study_record_url = f'https://zswxy.yinghuaonline.com/user/study_record.json?courseId={courseId}&page={page_index}&_={current_timestamp}'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh-HK;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': cookie,
        'Referer': f"{host}/user/index",
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    try:
        response = requests.get(url, headers=headers, proxies={"http": None, "https": None}).text
        nodeid = response.split("nodeId=")[1].split("\"")[0]
        url = host + "/user/node?nodeId=" + nodeid
        response = requests.get(url, headers=headers, proxies={"http": None, "https": None}).text
        node_ids = re.findall(r'nodeId=(\d+)', response)
        print('提取到的 nodeId:', node_ids)  # 打印提取出的 nodeId 列表

        node_ids = list(set(node_ids))  # 去重
        node_ids.sort(key=int)  # 按数值排序
        print('去重和排序后的 nodeId:', node_ids)
        return node_ids
    except requests.exceptions.RequestException as e:
        print("ERROR: 获取节点ID失败:", e)
        return []
    except IndexError as e:
        print("ERROR: 解析节点ID失败:", e)
        return []
