import os
import json
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType  # 新增：用于指定架构

# 导入logger，如果没有定义，使用print替代
try:
    from plugins.logger import logger_print_content
except ImportError:
    def logger_print_content(msg):
        print(f"[日志] {msg}")


def check_network_url(url):
    """检查URL类型并返回规范化的URL"""
    url = url.rstrip('/')
    if not url.startswith('http'):
        return False, url
    if url.endswith(('.js', '.js.map')):
        return 'js', url
    if url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.css', '.pdf', '.zip')):
        return 'resource', url
    if url.endswith(('.html', '.htm', '.php', '.jsp', '.aspx')):
        return 'html', url
    return 'other', url


def get_final_url(driver, url):
    """获取最终跳转的URL"""
    try:
        driver.get(url)
        return driver.current_url
    except Exception as e:
        logger_print_content(f"获取最终URL失败: {str(e)}")
        return url


def process_network_events(log_entries):
    """处理网络事件日志，提取所有加载的URL"""
    all_load_url = []
    for entry in log_entries:
        try:
            log = json.loads(entry['message'])['message']
            if 'Network.requestWillBeSent' in log['method']:
                params = log['params'].get("request", {})
                url = params.get("url", "")
                referer = params.get("headers", {}).get("Referer", "")
                url_type, new_url = check_network_url(url)
                if url_type:
                    all_load_url.append({
                        'url': new_url.rstrip('/'),
                        'referer': referer,
                        'url_type': url_type
                    })
        except Exception as e:
            continue
    return all_load_url


def create_webdriver(cookies):
    """创建Chrome WebDriver实例（优化版：强制64位架构+修复Cookies设置）"""
    options = Options()
    # 基础配置（简化，减少冲突）
    options.add_argument('--no-sandbox')  # 禁用沙箱
    options.add_argument('--headless=new')  # 新版无头模式（更稳定）
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    # 禁用图片加载（提速）
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    # 启用性能日志（用于捕获网络请求）
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    # 修复Cookies设置方式（原--cookie参数错误，改用add_cookie）
    # 注意：这里先不设置Cookies，在driver启动后通过add_cookie添加（避免启动参数冲突）

    # 关键：强制下载64位ChromeDriver（匹配系统架构）
    try:
        # 强制指定64位架构（针对Windows）
        service = Service(
            ChromeDriverManager(version='latest', os_type='win64').install()
        )
        logger_print_content("成功加载64位ChromeDriver（自动获取）")
    except Exception as e:
        logger_print_content(f"自动获取64位驱动失败：{str(e)}，尝试手动指定")
        # 手动指定64位驱动路径（请替换为你的实际路径）
        chromedriver_path = r"E:\SRC-Tools\Information\F-JS+Spider+40x\ChkApi_0x727\chromedriver.exe"  # 示例：64位驱动存放路径
        if not os.path.exists(chromedriver_path) or not chromedriver_path.endswith('.exe'):
            raise FileNotFoundError(f"手动驱动路径错误：{chromedriver_path}（请确认是64位.exe文件）")
        service = Service(chromedriver_path)
        logger_print_content(f"使用手动指定的64位驱动：{chromedriver_path}")

    # 启动驱动
    driver = webdriver.Chrome(service=service, options=options)

    # 正确添加Cookies（替代原--cookie参数，避免启动冲突）
    if cookies:
        try:
            # 先导航到目标域名（否则无法设置跨域Cookies）
            driver.get("https://xiaohongshu.com")
            # 解析Cookies（假设格式为"key1=value1; key2=value2"）
            for cookie in cookies.split(';'):
                if '=' in cookie:
                    key, value = cookie.strip().split('=', 1)
                    driver.add_cookie({
                        'name': key,
                        'value': value,
                        'domain': '.xiaohongshu.com'  # 适配目标域名
                    })
            logger_print_content("Cookies设置成功")
        except Exception as e:
            logger_print_content(f"Cookies设置失败：{str(e)}（不影响驱动启动）")

    return driver


def webdriverFind(url, cookies):
    """使用WebDriver获取页面加载的所有URL（优化版）"""
    all_load_url = []
    driver = None
    try:
        driver = create_webdriver(cookies)
        # 获取最终跳转URL并加载页面
        final_url = get_final_url(driver, url)
        logger_print_content(f"页面最终URL：{final_url}")
        # 提取网络请求日志
        logs = driver.get_log('performance')
        all_load_url = process_network_events(logs)
    except Exception as e:
        logger_print_content(f"WebDriver执行错误：{str(e)}")
    finally:
        if driver:
            driver.quit()  # 确保驱动退出
    return all_load_url