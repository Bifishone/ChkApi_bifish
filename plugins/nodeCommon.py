import os
import re
import uuid
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import ipaddress
import requests
import json
import time
from queue import Queue
from time import strftime,gmtime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tldextract import tldextract

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import math
import datetime
import logging
from urllib.parse import urlparse
import threading
import json
from traceback import print_exc

TIMEOUT = 30

# 完善黑名单功能
apiRootBlackList=["\\","#","$","@","*","+","-","|","!","%","^","~","[","]"]#api根黑名单，这里的值不可能出现在根API 起始值 中
apiRootBlackListDuringSpider=[x for x in apiRootBlackList if x!="#"]#过滤爬取中 api根

urlblacklist=[".js?", ".css?", ".jpeg?", ".jpg?", ".png?", ".gif?", "github.com", "www.w3.org", "example.com","example.org", "<", ">", "{", "}", "[", "]", "|", "^", ";", "/js/", "location.href", "javascript:void"]

fileExtBlackList=["exe","apk","mp4","mkv","mp3","flv","js","css","less","woff","vue","svg","png","jpg","jpeg","tif","bmp","gif","psd","exif","fpx","avif","apng","webp","swf",",","ico","svga","html","htm","shtml","ts","eot","lrc","tpl","cur","success","error","complete",]
urlextblacklist=["."+x if not x.startswith(",") else x for x in fileExtBlackList]

self_api_path = ['add', 'ls', 'focus', 'calc', 'download', 'bind', 'execute', '1', 'logininfo', 'create', 'decrypt', 'new', 'update', 'click', 'shell', 'export', 'menu', 'retrieve', 'on', 'message', 'admin', 'calculate', 'append', 'check', 'crypt', 'rename', 'exec', 'detail', 'clone', 'query', 'verify', 'is', 'authenticate', 'move', 'toggle', 'make', 'modify', 'upload', 'help', 'demo', 'with', 'alert', 'mode', 'gen', 'msg', 'edit', 'vrfy', 'enable', 'run', 'open', 'post', 'proxy', 'subtract', 'initiate', 'read', 'encrypt', 'auth', 'snd', 'view', 'save', 'config', 'get', 'alter', 'forceLogout', 'build', 'list', 'show', 'online', 'test', 'pull', 'notice',  'change', 'put', 'to', 'status', 'search', 'mod', '0', 'send', 'load', ]

# staticUrl_exts = ['.html', '.htm', '.jsp', '.jspx', '.asp', '.aspx', '.php']
staticExtBlackList=["pdf","docx","doc", "exe","apk","mp4","mkv","mp3","flv","css","less","woff","vue","svg","png","jpg","jpeg","tif","bmp","gif","psd","exif","fpx","avif","apng","webp","swf","ico","svga","ts","eot","lrc","tpl","cur","success","error","complete","zip","rar","7z"]
staticUrlExtBlackList=[f".{ext}" for ext in staticExtBlackList]

staticFileExtBlackList = ["pdf","docx","doc", "exe","apk","mp4","mkv","mp3","flv","css","less","woff","vue","svg","png","jpg","jpeg","tif","bmp","gif","psd","exif","fpx","avif","apng","webp","swf","ico","svga","ts","eot","lrc","tpl","cur","success","error","complete",]
staticFileExtBlackList = [f".{ext}" for ext in staticFileExtBlackList]



#移除敏感高危接口  delete remove drop update shutdown restart
#todo 这里需要修改为在api中判断而不是在url中，域名中有可能出现列表中的值
#todo 识别非webpack站点，仅输出js信息 输出匹配敏感信息?
dangerApiList=["del","delete","insert","logout","remove","drop","shutdown","stop","poweroff","restart","rewrite","terminate","deactivate","halt","disable"]

requestMethodRegex = [
    {"regex": r'request method\s\'get\'\snot supported', "tag": "missing", "desc": "method not supported"},
    {"regex": r'request method\s\'post\'\snot supported', "tag": "missing", "desc": "method not supported"},
    {"regex": r'invalid request method', "tag": "missing", "desc": "method not supported"},
    {"regex":r'不支持get请求方法，支持以下post',"tag":"missing","desc":"不支持的方法"},
    {"regex":r'(不支持\w*?(请求)|(方式)|(方法))',"tag":"missing","desc":"不支持的方法"},
]

#todo 扩充参数缺失关键字库
missingRegex=[
            {"regex":r'参数.+不能为空',"tag":"missing","desc":"参数不能为空"},
            {"regex":r'不能为空',"tag":"missing","desc":"参数不能为空"},
            {"regex":r'缺少参数',"tag":"missing","desc":"缺少参数"},
            {"regex":r'is missing',"tag":"missing","desc":"is missing"},
            {"regex":r'parameter.+is not present',"tag":"missing","desc":"is not present"},
            {"regex":r'参数缺失',"tag":"missing","desc":"参数缺失"},
            {"regex":r'参数异常',"tag":"missing","desc":"参数异常"},
            {"regex":r'参数错误',"tag":"missing","desc":"参数错误"},
            {"regex":r'参数不完整',"tag":"missing","desc":"参数不完整"},
            {"regex":r'非法的?参数',"tag":"missing","desc":"非法参数"},
        ]

# 配置日志记录器
logging.basicConfig(filename='ChkApi.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 创建一个日志记录器
logger = logging.getLogger('my_logger')

# logger.debug('这是一个调试信息')
# logger.info('这是一个信息')
# logger.warning('这是一个警告')
# logger.error('这是一个错误')
# logger.critical('这是一个严重错误')

# base url中禁止出现下面的根域名
BLACK_DOMAIN = ['127.0.0.1']
# base url中的host禁止出现下面的聂荣
BLACK_URL = ['127.0.0.1']

# 响应包禁止出现的内容
# BLACK_TEXT = ['''<RecommendDoc>https://api.aliyun.com''', 'FAIL_SYS_API_NOT_FOUNDED::请求API不存在', '"未找到API注册信息"', '"miss header param x-ca-key"', '"message":"No message available"']
BLACK_TEXT = ['''<RecommendDoc>https://api.aliyun.com''', '''<Code>MethodNotAllowed</Code>''', '<Code>AccessDenied</Code>',
              'FAIL_SYS_API_NOT_FOUNDED::请求API不存在', '"未找到API注册信息"', '"status":400,', '"status":403', '"msg":"参数错误"',
              '"miss header param x-ca-key"', '"message":"No message available"', '"code":1003,"message":"The specified token is expired or invalid."',
              '{"csrf":"', '"status":401,"error":"Unauthorized"', '''"Request method 'POST' not supported"''', '"error":"Internal Server Error"',
              '"code":"HttpRequestMethodNotSupported"', '"accessErrorId"', '<status>403</status>', '"code":"AUTHX_01002"']


webChatBotOpen = True          # 开启微信机器人

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
}
headers_post_data = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
    # "Content-Type": "application/x-www-form-urlencoded",
}
headers_post_json = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
    "Content-Type": "application/json",
}

# 打印内容并保存到日志里
def logger_print_content(content):
    print(content)
    logger.info(content)


def getCurrentTime():
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d")
    return currentTime

def getCurrentTime2():
    current_time = str(datetime.datetime.now().strftime('%Y_%m_%d %H:%M:%S')).replace(' ', '_').replace(':', '_')
    return current_time

def getCurrent_time():
    current_time = str(datetime.datetime.now())
    return current_time

def getCurrent_time_folder():
    current_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).replace(' ', '-').replace(':', '-')
    return current_time



# 列表分割
def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def check_url_alive(url):
    try:
        requests.get(url=url, headers=headers, timeout=10, proxies=None, verify=False)
        return True
    except Exception as e:
        return False

# 去重并保持有序
def remove_duplicates(lst):
    # Using dict.fromkeys() to remove duplicates and maintain order
    return list(dict.fromkeys(lst))

def list_files(directory):
    all_files = []  # 创建一个新的列表来存储结果
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith('GET'):
                full_path = os.path.join(root, file)
                # print(full_path)
                all_files.append(full_path)
    return all_files


def is_blacklisted(url):
    """
    检查 URL 的根域名是否在黑名单中。

    参数:
    url (str): 要检查的 URL。
    black_domains (list): 域名黑名单。

    返回:
    bool: 如果域名在黑名单中返回 True，否则返回 False。
    """
    parsed_domain = tldextract.extract(url)
    if parsed_domain.suffix:
        domain = f"{parsed_domain.domain}.{parsed_domain.suffix}"
    # 127.0.0.1
    else:
        domain = f"{parsed_domain.domain}"

    if domain in BLACK_DOMAIN:
        return True

    url_parse = urlparse(url)
    netloc = url_parse.netloc
    for blackurl in BLACK_URL:
        if blackurl in netloc:
            return True

    return False


def save_response_to_file(file_path, text):
    for _ in BLACK_TEXT:
        if _ in text:
            return

    with open(file_path, 'at', encoding='utf-8') as f:
        f.writelines(f"{text}\n")

def is_domain(s):
    domain_regex = r'^(?!\d+\.\d+\.\d+\.\d+$)([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\.?$'
    match = re.match(domain_regex, s)
    if match:
        return True
    return False

# 判断是否是IP
def is_ip(s):
    try:
        ipaddress.ip_address(s)
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    print(getCurrentTime2())