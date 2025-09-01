import json
import warnings
from urllib.parse import urlparse
from traceback import print_exc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
try:
    from plugins.nodeCommon import *
except Exception as e:
    from nodeCommon import *


warnings.filterwarnings("ignore")


def create_webdriver(cookies):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--ignore-certificate-errors')  # 忽略证书错误
    options.add_argument('--ignore-ssl-errors')  # 忽略SSL错误
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    service = Service(executable_path=r"/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    # Set user agent
    driver.execute_cdp_cmd(
        'Network.setUserAgentOverride',
        {
            "userAgent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    )

    if cookies:
        # Set cookie header
        driver.execute_cdp_cmd(
            'Network.setExtraHTTPHeaders',
            {"headers": {"Cookie": cookies}}
        )

    return driver
def check_network_url(url):
    if not url or url.count('?') > 1 or not url.startswith('http'):
        return False, ''
    url_parse = urlparse(url)
    path = url_parse.path
    # print(path)
    if path.lower().endswith(".js"):
        return 'js', url
    if url.startswith('data'):
        return False, ''
    if '.' not in path.lower().rsplit('/')[-1]:
        return 'no_js', f"{url_parse.scheme}://{url_parse.netloc}{url_parse.path}"
    return False, ''


def process_network_events(log_entries):
    all_load_url = []
    for entry in log_entries:
        try:
            log = json.loads(entry['message'])['message']
            if 'Network.requestWillBeSent' in log['method']:
                params_request = log['params'].get("request", {})
                url = params_request.get("url", "")
                referer = params_request.get("headers", {}).get("Referer", "")
                url_type, new_url = check_network_url(url)
                if url_type:
                    print(f"URL: {new_url}\tReferer: {referer}\t{url_type}")
                    all_load_url.append({'url': new_url.rstrip('/'), 'referer': referer, 'url_type': url_type})
        except Exception as e:
            print(print_exc())

    return all_load_url


def get_final_url(driver, url):
    driver.get(url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    return driver.current_url


def webdriverFind(url, cookies):
    all_load_url = []
    driver = create_webdriver(cookies)
    try:
        final_url = get_final_url(driver, url)
        logger_print_content(f"最终跳转URL: {final_url}")

        logs = driver.get_log('performance')
        all_load_url = process_network_events(logs)
    except Exception as e:
        driver.quit()
    finally:
        driver.quit()

    return all_load_url
