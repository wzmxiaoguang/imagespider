from urllib.parse import urlencode
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError
from multiprocessing import Pool
from hashlib import md5
import requests
import json
import time
import sys
import re
import os


def get_page_index(offset, keyword):
    try:
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
    try:
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求详情页出错", url)
        return None


def parse_page_detail(html):
    try:
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
    except JSONDecodeError:
        return None


def download_image(url):
    try:
        print("正在下载", url)
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content)
        return None
    except RequestException:
        print("请求图片出错", url)
        return None


def save_image(content):
    file_path = '{0}/images/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)


def main(param):
    offset, key = param
    html = get_page_index(offset, key)
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            parse_page_detail(html)
        time.sleep(5)


if __name__ == '__main__':
    key = ""
    for word in sys.argv[1:]:
        key += word + ' '

    dir_path = '{0}/images'.format(os.getcwd())
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    
    groups = [(x*20, key) for x in range(0, 21)]
    # 多线程
    # pool = Pool()
    # pool.map(main, groups)
    # 单线程
    for param in groups:
        main(param)
