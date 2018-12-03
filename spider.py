from urllib.parse import urlencode
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError
from multiprocessing import Pool
from bs4 import BeautifulSoup
from hashlib import md5
from config import *
import requests
import pymongo
import json
import time
import re
import os

client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]


def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': '3',
        'from': 'gallery',
        'pd': '',
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求索引页出错")
        return None


def parse_page_index(html):
    try:
        data = json.loads(html)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                yield item.get('article_url')
    except JSONDecodeError:
        return None


def get_page_detail(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求详情页出错", url)
        return None


def parse_page_detail(html, url):
    try:
        soup = BeautifulSoup(html, 'lxml')
        title = soup.select('title')[0].get_text()
        images_pattern = re.compile('JSON.parse\((.*?)\)', re.S)
        result = re.search(images_pattern, html)
        if result:
            data = json.loads(result.group(1))
            data = json.loads(data)
            if data and 'sub_images' in data.keys():
                sub_images = data.get('sub_images')
                images = [item.get('url') for item in sub_images]
                for image in images:
                    download_image(image)
                return {
                    'title': title,
                    'url': url,
                    'images': images
                }
    except JSONDecodeError:
        return None


def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print("存储到MongoDB成功", result)
        return True
    return False


def download_image(url):
    print("正在下载", url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content)
        return None
    except RequestException:
        print("请求图片出错", url)
        return None


def save_image(content):
    file_path = '{0}/image/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)


def main(offset):
    html = get_page_index(offset, KEYWORD)
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html, url)
            if result:
                save_to_mongo(result)
        time.sleep(5)


if __name__ == '__main__':
    groups = [x*20 for x in range(GROUP_START, GROUP_END+1)]
    pool = Pool()
    pool.map(main, groups)
