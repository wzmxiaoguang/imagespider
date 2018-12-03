from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit
from win32api import GetSystemMetrics
from urllib.parse import urlencode
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError
from hashlib import md5
from socket_jpg import img as socket
import base64 
import requests 
import json
import sys 
import re
import os


class Runthread(QtCore.QThread):

    upimage = QtCore.pyqtSignal(str)

    def __init__(self, words):
        super(Runthread, self).__init__()
        self.words = words
        self.count = 0

    def run(self):
        key = ""
        for word in self.words:
            key += word + ' '

        dir_path = '{0}/images'.format(os.getcwd())
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        groups = [(x*20, key) for x in range(0, 21)]
        for param in groups:
            self.main(param)

    def get_page_index(self, offset, keyword):
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
            return None

    def parse_page_index(self, html):
        try:
            data = json.loads(html)
            if data and 'data' in data.keys():
                for item in data.get('data'):
                    yield item.get('article_url')
        except JSONDecodeError:
            return None

    def get_page_detail(self, url):
        try:
            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            return None
        except RequestException:
            return None

    def parse_page_detail(self, html):
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
                        self.download_image(image)
        except JSONDecodeError:
            return None

    def download_image(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.save_image(response.content)
            return None
        except RequestException:
            return None

    def save_image(self, content):
        file_path = '{0}/images/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as f:
                f.write(content)
        if self.count % 2 == 0:
            self.upimage.emit(file_path)
        self.count += 1

    def main(self, param):
        offset, key = param
        html = self.get_page_index(offset, key)
        for url in self.parse_page_index(html):
            html = self.get_page_detail(url)
            if html:
                self.parse_page_detail(html)


class MyWidget(QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        self.setWindowTitle("图片下载器")
        self.setGeometry(GetSystemMetrics(0)/2 - 350, GetSystemMetrics(1)/2 - 350, 700, 700)
        self.label1 = QLabel(self)
        self.label1.setText("关键字：")
        self.label1.setFont(QtGui.QFont("", 20, QtGui.QFont.Bold))
        self.label1.setGeometry(150, 90, 100, 50)
        self.line1 = QLineEdit(self)
        self.line1.setFont(QtGui.QFont("", 20, QtGui.QFont.Bold))
        self.line1.setGeometry(250, 90, 300, 50)
        self.line1.returnPressed.connect(self.search)

    def search(self):
        self.line1.returnPressed.disconnect()
        words = self.line1.text().split()
        self.label1.hide()
        self.line1.hide()
        self.myThread = Runthread(words)
        self.myThread.upimage.connect(self.Display)
        self.myThread.start()

    def Display(self, path):
        self.setbackground(path)

    def setbackground(self, path):
        pale1 = QtGui.QPalette()
        pix1 = QtGui.QPixmap(path)
        pix1 = pix1.scaled(self.width(), self.height())
        pale1.setBrush(self.backgroundRole(), QtGui.QBrush(pix1))
        self.setPalette(pale1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myshow = MyWidget()
    myshow.show()

    tmp = open('socket.jpg', 'wb')
    tmp.write(base64.b64decode(socket))
    tmp.close()
    myshow.setbackground(os.getcwd()+'/socket.jpg')
    os.remove('socket.jpg')

    sys.exit(app.exec_())
