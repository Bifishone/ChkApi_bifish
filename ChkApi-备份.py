import os
from optparse import OptionParser
from collections import Counter
import openpyxl
from plugins.nodeCommon import *
from plugins.jsAndStaticUrlFind import *
from plugins.apiPathFind import *
from plugins.saveToExcel import saveToExcel
from plugins.webdriverFind import *
from plugins.apiUrlReqNoParameter import *
from plugins.getParameter import *
from plugins.apiUrlReqWithParameter import *
from plugins.disposeResults import *
import tldextract

def get_base_domain(url):
    ext = tldextract.extract(url)
    return ext.domain

def filter_base_urls(base_domain, url):
    # ip则直接返回
    if is_ip(urlparse(url).netloc):
        return url
    # 域名则需要判断是否是目标的域名
    else:
        if base_domain in url:
            return url
        else:
            logger_print_content(f"[非目标站] {url}")
            return ""


# 获取访问url加载的js url
def indexJsFind(url, cookies):
    if cookies:
        headers['Cookie'] = cookies
    all_load_url = [{'url': url, 'referer': url, 'url_type': 'base_url'}]

    try:
        # 待定：考虑是否要禁用url跳转
        res = requests.get(url=url, headers=headers, timeout=TIMEOUT, verify=False)
        soup = BeautifulSoup(res.text, 'html.parser')
        scripts = soup.find_all('script')
        js_paths = [script['src'] for script in scripts if script.get('src')]
        for js_path in js_paths:
            # print(url, js_path.rstrip('/'))
            all_load_url.append({'url': urljoin(url, js_path.rstrip('/')), 'referer': url, 'url_type': 'js'})
        # ['static/js/elicons.626b260a.js', 'static/js/modules.d59689f1.js', 'static/js/app.397cfa65.js']
        return all_load_url
    except Exception as e:
        return all_load_url

def filter_data(base_domain, all_load_url, all_api_paths):
    """
    从提供的 URL 数据和 API 路径数据中提取并构建基本的 URL 列表。

    参数:
    url_data (list of dicts): 包含 URL 加载信息的字典列表，关键字包括 'url_type' 和 'url'。
    api_data (list of dicts): 包含 API 路径的字典列表，关键字包括 'url_type' 和 'api_path'。

    返回:
    list: 去重后的基本 URL 列表。
    """

    # 从all_load_url提取出base_url: https://aaa.com/dddd
    base_urls = []
    # 从all_load_url提取出根路径：http://bbb.com
    tree_urls = []
    # 从all_load_url提取出路径带有api字符串：http://ccc.com/xxxapi
    path_with_api_urls = []

    # 从all_api_paths提取出有api字符串的接口 ['/gateway/api', '/marketing_api', '/api', '/pages/appdownload/api', '/restapi', '/oapi']
    path_with_api_paths = []
    # 从all_api_paths提取出没有api字符串的接口
    path_with_no_api_paths = []


    '''
    自动加载有：http://x.x.x.x:8082/prod-api/auth/tenant/list
    js的接口里有：/auth/tenant/list
    则获取到base_url为http://x.x.x.x:8082/prod-api
    '''
    for item in all_load_url:
        if item['url_type'] == 'no_js':
            item_url = item['url']
            url_parse = urlparse(item_url)

            # 过滤掉非目标站的url
            if not filter_base_urls(base_domain, item['url']):
                continue

            # http://aaa.com
            if url_parse.path in ['/', '']:
                logger_print_content(f'[根路径] {item_url}')
                tree_urls.append(item_url)
                continue

            # 保存 所有目标资产的根路径url
            tree_url = f"{url_parse.scheme}://{url_parse.netloc}"
            logger_print_content(f'[根路径] {tree_url}')
            tree_urls.append(tree_url)

            # 路径有api/ 字符串的
            api_path_index = url_parse.path.find('api/')
            # print(api_path_index)
            if api_path_index != -1:
                path_with_api_url = f"{url_parse.scheme}://{url_parse.netloc}{url_parse.path[:api_path_index]}api"
                logger_print_content(f'[api] {path_with_api_url}')
                path_with_api_urls.append(path_with_api_url)
                base_url = path_with_api_url.rsplit('/', 1)[0]
                if urlparse(base_url).path:
                    base_urls.append(base_url.rstrip('/'))
                continue

            # 截获base_url, 例如自动加载了https://x.x.x.x/dddd/eee/fff，js获取到的api_path接口有/eee/fff，则base_url为https://x.x.x.x/dddd
            else:
                for api in all_api_paths:
                    if api['url_type'] == 'api_path' and api['api_path'] != '/' and not api['api_path'].startswith('http') and len(api['api_path']) > 2 and url_parse.path != api['api_path']:
                        url_parse = urlparse(item['url'])
                        api_index = url_parse.path.find(api['api_path'])
                        if api_index != -1:
                            base_url = f"{url_parse.scheme}://{url_parse.netloc}{url_parse.path[:api_index]}".rstrip('/')
                            # base_url = item['url'][:api_index]  # 在 API 路径开始的地方截断 URL
                            if not is_blacklisted(base_url) and urlparse(base_url).path:
                                logger_print_content(f'[截获] {base_url}')
                                base_urls.append(base_url.rstrip('/'))
    base_urls = list(set(base_urls))
    tree_urls = list(set(tree_urls))
    path_with_api_urls = list(set(path_with_api_urls))
    logger_print_content(f"自动加载的根路径 {len(tree_urls)} tree_urls = {tree_urls}")
    logger_print_content(f"自动加载的子路径 {len(base_urls)} base_urls = {base_urls}")
    logger_print_content(f"自动加载的API路径 {len(path_with_api_urls)} path_with_api_urls = {path_with_api_urls}")
    # print(len(tree_urls), tree_urls)
    # print(len(path_with_api_urls), path_with_api_urls)

    # 第二次遍历：从 all_api_paths 获取所有带api字符串
    for api in all_api_paths:
        # js_url = api['url']

        # 过滤掉非目标站的url
        # if not filter_base_urls(base_domain, js_url):
        #     continue

        api_path = api['api_path']
        if api['url_type'] == 'api_path' and api_path != '/' and not api_path.startswith('http') and len(api_path) > 2 :
            path_parse = urlparse(api_path)
            # print(api['api_path'], path_parse)
            api_path_index = api_path.find('api/')
            if api_path_index != -1:
                path_with_api_path = f"/{api_path[:api_path_index].lstrip('/')}api"
                path_with_api_paths.append(path_with_api_path)
                # print(f"path_with_api_path = {path_with_api_path}")


                path_with_no_api_path = f"/{api_path[api_path_index+4:]}"
                path_with_no_api_paths.append(path_with_no_api_path)
                # print(f"path_with_no_api_path = {path_with_no_api_path}")
            else:
                path_with_no_api_path = f"/{api_path.lstrip('/')}"
                path_with_no_api_paths.append(path_with_no_api_path)
                # print(f"path_with_no_api_path = {path_with_no_api_path}")

    # 把path_with_api_urls的api路径加进去
    for path_with_api_url in path_with_api_urls:
        path_with_api_paths.append(f"/{urlparse(path_with_api_url).path.lstrip('/')}")
    # 如果path_with_api_paths为空，则手动增加api
    if not path_with_api_paths:
        path_with_api_paths.append('/api')
    path_with_api_paths = list(set(path_with_api_paths))
    path_with_no_api_paths = list(set(path_with_no_api_paths))
    logger_print_content(f"带有API字符串的接口 {len(path_with_api_paths)} path_with_api_paths = {path_with_api_paths}")
    logger_print_content(f"没有API字符串的接口 {len(path_with_no_api_paths)} path_with_no_api_paths = {path_with_no_api_paths}")

    # 组合
    all_path_with_api_urls = []
    for _1 in base_urls + tree_urls:
        if path_with_api_paths == ['/api']:
            all_path_with_api_urls.append(f"{_1}")
        for _2 in path_with_api_paths:
            path_with_api_url = f"{_1}{_2}"
            # print(path_with_api_url)
            all_path_with_api_urls.append(path_with_api_url)
    all_path_with_api_urls = list(set(all_path_with_api_urls))
    logger_print_content(f"根路径和base路径拼接js匹配出来的API字符串接口 {len(all_path_with_api_urls)} all_path_with_api_urls = {all_path_with_api_urls}")
    api_urls = []
    for _1 in all_path_with_api_urls:
        for _2 in path_with_no_api_paths:
            api_url = f"{_1}{_2}"
            # print(api_url)
            api_urls.append(api_url)
        for _3 in self_api_path:
            api_url = f"{_1}/{_3}"
            api_urls.append(api_url)
    api_urls = list(set(api_urls))
    logger_print_content(f"组合出来的所有api路径 {len(api_urls)} ")

    api_info = {
        'tree_urls': tree_urls,
        'base_urls': base_urls,
        'path_with_api_paths': path_with_api_paths,
        'path_with_no_api_paths': path_with_no_api_paths,
        'all_path_with_api_urls': all_path_with_api_urls,
        'api_urls': api_urls,
    }

    for api_url in api_urls:
        print(api_url)

    return api_info


def save_list_to_excel(excelSavePath, excel, title, list_result):
    sheet = saveToExcel(excelSavePath, excel, title)
    sheet.save_list_to_excel(title, list_result)

def save_dict_to_excel(excelSavePath, excel, title, list_dict_result):
    sheet = saveToExcel(excelSavePath, excel, title)
    if list_dict_result:
        sheet.save_dict_to_excel(list_dict_result)

# 第八步：处理结果
def deal_results(excelSavePath, excel, folder_path, filePath_url_info):
    # 第八步：处理结果
    logger_print_content(f" 第八步：处理结果")
    # 整理response结果,差异化
    disposeResults_info = disposeResults_api(folder_path, filePath_url_info)
    with open(f'{folder_path}/所有变量列表.txt', 'at', encoding='utf-8') as f9:
        f9.writelines(f"disposeResults_info = {disposeResults_info}\n")

    diff_response_info = disposeResults_info['diff_response_info']
    diff_response_info_dict = [{"content_hash": _[0], "length": _[1], "size": _[2], "url": _[3], "path": _[4]} for _ in diff_response_info]
    save_dict_to_excel(excelSavePath, excel, '响应包diff_hash', diff_response_info_dict)

    hae_api_info = disposeResults_info['hae_api_info']
    hae_api_info_dict = [{"name": _[0], "matches": str(_[1]), "url": _[2], "file": _[3]} for _ in hae_api_info]
    save_dict_to_excel(excelSavePath, excel, 'hae检测结果', hae_api_info_dict)

    sensitive_data_info = disposeResults_info['sensitive_data_info']
    sensitive_data_info_dict = [{"name": _[0], "matches": str(_[1]), "url": _[2], "file": _[3]} for _ in sensitive_data_info]
    save_dict_to_excel(excelSavePath, excel, '敏感信息检测结果', sensitive_data_info_dict)

    return disposeResults_info

def run_url(url, cookies, chrome, attackType, noApiScan):
    js_paths = []
    static_paths = []

    try:
        # 使用正则表达式替换非字母数字字符为下划线
        folder_name = re.sub(r'[^a-zA-Z0-9\.]', '_', url)
        current_path = os.getcwd()
        folder_path = f"{current_path}/results/{folder_name}"
        # 创建目录
        os.makedirs(folder_path)
    except Exception as e:
        logger_print_content(f"{url} 存在历史扫描记录 {folder_path}")
        # 读取历史项目
        return

    # 判断是否存活
    try:
        if cookies:
            headers['Cookie'] = cookies
        requests.get(url=url, headers=headers, timeout=TIMEOUT, verify=False)
    except Exception as e:
        return

    domain = urlparse(url).netloc
    base_domain = get_base_domain(url)

    excel = openpyxl.Workbook()
    excel.remove(excel[excel.sheetnames[0]])  # 删除第一个默认的表
    excel_name = domain
    excelSavePath = '{}/{}.xlsx'.format(folder_path, excel_name)

    # 文件路径对应的url
    filePath_url_info = {}
    all_load_url = []
    js_and_staticUrl_alive_info = []
    all_api_paths = []
    api_info = {
        'tree_urls': [],
        'base_urls': [],
        'path_with_api_paths': [],
        'path_with_no_api_paths': [],
        'all_path_with_api_urls': [],
        'api_urls': [],
    }
    parameters = []
    all_api_url_xml_json_res = []

    # 第一步先获取该页面加载了哪些js和base url
    if chrome == 'on':
        logger_print_content(f"第一步:调用webdriver获取{url}加载的js和no_js url")
        all_load_url = webdriverFind(url, cookies)
        logger_print_content(f"[*] all_load_url = {all_load_url}")
    else:
        logger_print_content(f"第一步:访问{url}获取js和no_js url")
        all_load_url = indexJsFind(url, cookies)
        logger_print_content(f"[*] all_load_url = {all_load_url}")

    # 自动加载js的url列表
    js_load_urls = []
    # 自动加载base的url列表
    no_js_load_urls = []

    for _ in all_load_url:
        if _.get('url_type', None) == 'js':
            js_load_urls.append(_['url'])
        elif _.get('url_type', None) == 'no_js':
            # IP直接返回，域名则需要判断是否是目标的域名
            if filter_base_urls(base_domain, _['url']):
                no_js_load_urls.append(_['url'])

    js_load_urls = list(set(js_load_urls))
    no_js_load_urls = list(set(no_js_load_urls))
    logger_print_content(f"js_load_urls = {js_load_urls}\n\n")
    logger_print_content(f"no_js_load_urls = {no_js_load_urls}\n\n")

    save_dict_to_excel(excelSavePath, excel, '首页自动加载的所有URL列表', all_load_url)
    save_list_to_excel(excelSavePath, excel, '首页自动加载的JS_URL列表', js_load_urls)
    save_list_to_excel(excelSavePath, excel, '首页自动加载的属于目标的非JS_URL列表', no_js_load_urls)

    with open(f'{folder_path}/1-1首页自动加载的所有URL列表.txt', 'at', encoding='utf-8') as f1, open(f'{folder_path}/1-2首页自动加载的JS_URL列表.txt', 'at', encoding='utf-8') as f2, open(f'{folder_path}/1-3首页自动加载的属于目标的非JS_URL列表.txt', 'at', encoding='utf-8') as f3, open(f'{folder_path}/所有变量列表.txt', 'at', encoding='utf-8') as f9:
        f9.writelines(f"url = {url}\n")
        f9.writelines(f"cookies = {cookies}\n")
        f9.writelines(f"all_load_url = {all_load_url}\n")
        f9.writelines(f"js_load_urls = {js_load_urls}\n")
        f9.writelines(f"no_js_load_urls = {no_js_load_urls}\n")
        f9.writelines(f"-"*100 + '\n')
        for load_url in all_load_url:
            f1.writelines(f"{load_url}\n")
        for js_url in js_load_urls:
            f2.writelines(f"{js_url}\n")
        for no_js_load_url in no_js_load_urls:
            f3.writelines(f"{no_js_load_url}\n")

    # 第二步：访问加载的js和no_js url，提取出新的js
    logger_print_content(f"第二步：访问加载的js和no_js url，提取出新的js")
    # 从加载的js和no_js url，提取出新的js
    js_find_urls = []
    # js_urls = js_load_urls
    # base_urls = base_load_urls
    js_and_staticUrl_info, js_and_staticUrl_alive_info = js_find_api(domain, js_load_urls + no_js_load_urls, cookies, folder_path, filePath_url_info)
    logger_print_content(f"[*] 第二步访问加载的js和base url，提取出新的js和static url\n[*] js_and_staticUrl_info = {js_and_staticUrl_info}")
    for _ in js_and_staticUrl_alive_info:
        if _['url_type'] == 'js_url':
            js_find_urls.append(_['url'])
    js_find_urls = list(set(js_find_urls))
    all_js_urls = list(set(js_load_urls + js_find_urls))
    logger_print_content(f"[*] 获取到的所有js url\n[*] all_js_urls = {all_js_urls}\n\n")

    all_alive_staticUrl = []
    for _ in js_and_staticUrl_alive_info:
        if _['url_type'] == 'static_url':
            all_alive_staticUrl.append(_['url'])

    all_alive_js_and_staticUrl = []
    for _ in js_and_staticUrl_alive_info:
        all_alive_js_and_staticUrl.append(_['url'])

    save_list_to_excel(excelSavePath, excel, '提取出的js路径', js_and_staticUrl_info['js_paths'])
    save_list_to_excel(excelSavePath, excel, '所有存活的js(自动加载的js和拼接的js)', all_js_urls)
    save_list_to_excel(excelSavePath, excel, '所有存活的静态url', all_alive_staticUrl)
    save_list_to_excel(excelSavePath, excel, '所有存活的js和静态url', all_alive_js_and_staticUrl)

    with open(f'{folder_path}/2-1-提取出的js路径.txt', 'at', encoding='utf-8') as f, open(f'{folder_path}/2-2-所有存活的js(自动加载的js和拼接的js).txt', 'at', encoding='utf-8') as f2, open(f'{folder_path}/2-3-所有存活的静态url.txt', 'at', encoding='utf-8') as f3, open(f'{folder_path}/2-4-所有存活的js和静态url.txt', 'at', encoding='utf-8') as f4, open(f'{folder_path}/所有变量列表.txt', 'at', encoding='utf-8') as f9:
        # f9.writelines(f"js_urls = {[url] + js_load_urls}\n")
        f9.writelines(f"js_and_staticUrl_alive_info = {js_and_staticUrl_alive_info}\n")
        f9.writelines(f"js_and_staticUrl_info = {js_and_staticUrl_info}\n")
        f9.writelines(f"js_and_staticUrl_info['js_paths'] = {js_and_staticUrl_info['js_paths']}\n")
        f9.writelines(f"js_and_staticUrl_info['js_url'] = {js_and_staticUrl_info['js_url']}\n")
        f9.writelines(f"js_and_staticUrl_info['static_paths'] = {js_and_staticUrl_info['static_paths']}\n")
        f9.writelines(f"js_and_staticUrl_info['static_url'] = {js_and_staticUrl_info['static_url']}\n")
        f9.writelines(f"all_alive_staticUrl = {all_alive_staticUrl}\n")
        f9.writelines(f"all_alive_js_and_staticUrl = {all_alive_js_and_staticUrl}\n")
        f9.writelines(f"all_js_urls = {all_js_urls}\n")
        f9.writelines(f"-"*100 + '\n')

        for js_path in js_and_staticUrl_info['js_paths']:
            js_paths.append(js_path)
            f.writelines(f"{js_path}\n")

        for js_url in all_js_urls:
            f2.writelines(f"{js_url}\n")

        for _ in all_alive_staticUrl:
            f3.writelines(f"{_}\n")

        for _ in all_alive_js_and_staticUrl:
            f4.writelines(f"{_}\n")

        # for staticUrl_path in js_and_staticUrl_info['static_paths']:
        #     if staticUrl_path.startswith('http'):
        #         static_paths.append(staticUrl_path)
        #         f3.writelines(f"{staticUrl_path}\n")

    if noApiScan == 0:

        # 第三步：访问所有js url，从网页源码中匹配出api接口
        logger_print_content(f"第三步：访问所有js url，从网页源码中匹配出api接口")
        all_api_paths = apiPathFind_api(all_js_urls, cookies, folder_path)
        logger_print_content(f"[*] 所有api接口\n[*] all_api_paths = {all_api_paths}")

        save_dict_to_excel(excelSavePath, excel, '从所有js里获取到的API_PATH列表', all_api_paths)
        with open(f'{folder_path}/3-从所有js里获取到的API_PATH列表.txt', 'at', encoding='utf-8') as f, open(f'{folder_path}/所有变量列表.txt', 'at', encoding='utf-8') as f9:
            for api_path in all_api_paths:
                f.writelines(f"{api_path}\n")
            f9.writelines(f"all_api_paths = {all_api_paths}\n")


        # 第四步梳理: API接口，整理出所有的API URL
        api_info = filter_data(base_domain, all_load_url, all_api_paths)


        save_list_to_excel(excelSavePath, excel, '从自动加载的URL里提取出来的根路径', api_info['tree_urls'])
        save_list_to_excel(excelSavePath, excel, '从自动加载的URL里提取出来的BASE_URL', api_info['base_urls'])
        save_list_to_excel(excelSavePath, excel, '带有API字符串接口的url', api_info['all_path_with_api_urls'])
        save_list_to_excel(excelSavePath, excel, '带有API字符串的接口', api_info['path_with_api_paths'])
        save_list_to_excel(excelSavePath, excel, '没有API字符串的接口', api_info['path_with_no_api_paths'])
        save_list_to_excel(excelSavePath, excel, '组合出来的最终的所有API_URL', api_info['api_urls'])

        with open(f'{folder_path}/4-1-从自动加载的URL里提取出来的根路径.txt', 'at', encoding='utf-8') as f, open(f'{folder_path}/4-2-从自动加载的URL里提取出来的BASE_URL.txt', 'at', encoding='utf-8') as f2, open(f'{folder_path}/4-3-带有API字符串接口的url.txt', 'at', encoding='utf-8') as f3, open(f'{folder_path}/4-4-带有API字符串的接口.txt', 'at', encoding='utf-8') as f4, open(f'{folder_path}/4-5-没有API字符串的接口.txt', 'at', encoding='utf-8') as f5, open(f'{folder_path}/4-6-组合出来的最终的所有API_URL.txt', 'at', encoding='utf-8') as f6, open(f'{folder_path}/所有变量列表.txt', 'at', encoding='utf-8') as f9:
            f9.writelines(f"api_info = {api_info}\n")
            f9.writelines(f"tree_urls = {api_info['tree_urls']}\n")
            f9.writelines(f"base_urls = {api_info['base_urls']}\n")
            f9.writelines(f"path_with_api_paths = {api_info['path_with_api_paths']}\n")
            f9.writelines(f"path_with_no_api_paths = {api_info['path_with_no_api_paths']}\n")
            f9.writelines(f"all_path_with_api_urls = {api_info['all_path_with_api_urls']}\n")
            f9.writelines(f"api_urls = {api_info['api_urls']}\n")
            f9.writelines(f"-"*100 + '\n')

            for tree_url in api_info['tree_urls']:
                f.writelines(f"{tree_url}\n")

            for base_url in api_info['base_urls']:
                f2.writelines(f"{base_url}\n")

            for path_with_api_url in api_info['all_path_with_api_urls']:
                f3.writelines(f"{path_with_api_url}\n")

            for path_with_api_path in api_info['path_with_api_paths']:
                f4.writelines(f"{path_with_api_path}\n")

            for path_with_no_api_path in api_info['path_with_no_api_paths']:
                f5.writelines(f"{path_with_no_api_path}\n")

            for api_url in api_info['api_urls']:
                f6.writelines(f"{api_url}\n")



        if attackType == 0:
            api_urls = api_info['api_urls']

            if len(api_urls) > 200000:
                return
            # 所有api请求的响应包
            all_api_url_xml_json_res = []
            # 第五步：梳理所有API接口并访问
            logger_print_content(f"第五步：无参三种形式请求所有API接口")
            api_url_res = apiUrlReqNoParameter_api(url, api_urls, cookies, folder_path, filePath_url_info)


            # 非404，xml和json的api接口
            xml_json_api_url = []
            with open(f'{folder_path}/5-1-无参三种形式请求API接口响应结果.txt', 'at', encoding='utf-8') as f1, open(f'{folder_path}/5-2-XML_JSON的API_URL列表.txt', 'at', encoding='utf-8') as f2, open(f'{folder_path}/5-3-XML_JSON的API_URL无参的RESPONSE结果.txt', 'at', encoding='utf-8') as f3, open(f'{folder_path}/所有变量列表.txt', 'at', encoding='utf-8') as f9:
                f9.writelines(f"无参 api_url_res = {api_url_res}\n")
                f9.writelines(f"-"*100)
                for _ in api_url_res:
                    f1.writelines(f"{_}\n")
                    if _['res_code'] == 200 and ('xml' in _['res_type'] or 'json' in _['res_type']):
                        f2.writelines(f"{_['url']}\n")
                        f3.writelines(f"{_}\n")
                        xml_json_api_url.append(_['url'])
                        all_api_url_xml_json_res.append(_)
            xml_json_api_url = list(set(xml_json_api_url))

            save_dict_to_excel(excelSavePath, excel, '无参三种形式请求API接口响应结果', api_url_res)
            save_list_to_excel(excelSavePath, excel, 'XML_JSON的API_URL列表', xml_json_api_url)
            save_dict_to_excel(excelSavePath, excel, 'XML_JSON的API_URL无参的RESPONSE结果', all_api_url_xml_json_res)

            # 第六步：提取参数
            logger_print_content(f"第六步：提取参数")
            parameters = getParameter_api(folder_path)
            save_list_to_excel(excelSavePath, excel, '提取的所有参数', parameters)
            with open(f'{folder_path}/6-提取的所有参数.txt', 'at', encoding='utf-8') as f, open(f'{folder_path}/所有变量列表.txt', 'at', encoding='utf-8') as f9:
                f9.writelines(f"parameters = {parameters}\n")
                f9.writelines(f"-"*100 + '\n')
                for parameter in parameters:
                    f.writelines(f"{parameter}\n")

            # 第七步：携带参数请求
            if parameters:
                logger_print_content(f"第七步：有参三种形式请求所有API接口")
                api_url_res = apiUrlReqWithParameter_api(url, xml_json_api_url, cookies, folder_path, parameters, filePath_url_info)
                save_dict_to_excel(excelSavePath, excel, '有参三种形式请求XML_JSON的API接口响应结果', api_url_res)

                with open(f'{folder_path}/7-1-有参三种形式请求XML_JSON的API接口响应结果.txt', 'at', encoding='utf-8') as f1, open(f'{folder_path}/7-2-XML_JSON的API_URL有参的RESPONSE结果.txt', 'at', encoding='utf-8') as f3, open(f'{folder_path}/所有变量列表.txt', 'at', encoding='utf-8') as f9:
                    f9.writelines(f"xml_json_api_url = {xml_json_api_url}\n")
                    f9.writelines(f"有参 api_url_res = {api_url_res}\n")
                    f9.writelines(f"-"*100 + '\n')
                    for _ in api_url_res:
                        f1.writelines(f"{_}\n")
                        f3.writelines(f"{_}\n")
                        all_api_url_xml_json_res.append(_)

    disposeResults_info = deal_results(excelSavePath, excel, folder_path, filePath_url_info)


    getJsUrl_info = {
        "all_load_urls": all_load_url,                                   # 1-1首页自动加载的所有URL列表.txt
        # "js_load_urls": js_load_urls,                                    # 1-2首页自动加载的JS_URL列表.txt
        # "no_js_load_urls": no_js_load_urls,                              # 1-3首页自动加载的属于目标的非JS_URL列表.txt
        #
        # "all_js_urls": all_js_urls,                                      # 2-1-所有存活的js路径-自动加载的js和拼接的js.txt
        # "js_paths": js_and_staticUrl_info['js_paths'],                   # 2-2-提取出的js路径.txt
        # "static_paths": js_and_staticUrl_info['static_paths'],           # 2-3-提取出的静态url路径.txt
        "js_and_staticUrl_alive_info": js_and_staticUrl_alive_info,      # 2-4-存活的js和静态URL.txt

        "all_api_paths": all_api_paths,                                  # 3-从所有js里获取到的API_PATH列表.txt

        "tree_urls" : api_info['tree_urls'],                             # 4-1-从自动加载的URL里提取出来的根路径.txt
        "base_urls": api_info['base_urls'],                              # 4-2-从自动加载的URL里提取出来的BASE_URL.txt
        "all_path_with_api_urls": api_info['all_path_with_api_urls'],    # 4-3-从自动加载的URL里提取出来的路径带有api字符串的URL.txt
        "path_with_api_paths": api_info['path_with_api_paths'],          # 4-4-从所有js里获取到的路径里有API字符串的接口列表.txt
        "path_with_no_api_paths": api_info['path_with_no_api_paths'],    # 4-5-从所有js里获取到的路径里没有API字符串的接口列表.txt
        # "api_urls": [],                                                # 4-6-组合出来的最终的所有API_URL.txt

        "parameters": parameters,                                        # 6-提取的所有参数.txt

        "all_api_url_xml_json_res": all_api_url_xml_json_res,            # 5-3-XML_JSON的API_URL无参的RESPONSE结果.txt 和 7-2-XML_JSON的API_URL有参的RESPONSE结果.txt

        "disposeResults_info": disposeResults_info,
    }
    with open(f'{folder_path}/所有变量列表.txt', 'at', encoding='utf-8') as f9:
        f9.writelines(f"getJsUrl_info = {getJsUrl_info}\n")

    logger_print_content('------------------------------------------------------------------------------------------------------------------------------------')

    return getJsUrl_info

def main():
    usage = '\n\t' \
            'python3 %prog -u http://www.xxx.com\n\t' \
            'python3 %prog -u http://www.xxx.com -c xxxxxxxxxxx\n\t' \
            'python3 %prog -f urls.txt\n\t' \
            'python3 %prog -u http://www.xxx.com --chrome off\n\t' \
            'python3 %prog -u http://www.xxx.com --at 1\n\t' \
            'python3 %prog -u http://www.xxx.com --na 1\n\t'
    parse = OptionParser(usage=usage)
    parse.add_option('-u', '--url', dest='url', type='str', help='要跑的目标url')
    parse.add_option('-c', '--cookies', dest='cookies', type='str', help='cookies')
    parse.add_option('-f', '--file', dest='file', type='str', help='file to scan')
    parse.add_option('--chrome', dest='chrome', type='str', default='on', help='off关闭chromedriver，默认是on') #
    parse.add_option('--at', dest='attackType', type='int', default=0, help='0 收集+探测\t1 收集\t默认是0')  # 0为收集api接口和请求API接口，1为收集API接口不请求API接口
    parse.add_option('--na', dest='noApiScan', type='int', default=0, help='不扫描API接口漏洞，1不扫描，0扫描，默认是0') # 0为js扫描，1为js+api扫描

    options, args = parse.parse_args()
    url, cookies, file, chrome, attackType, noApiScan = options.url, options.cookies, options.file, options.chrome, options.attackType, options.noApiScan

    if url:
        run_url(url, cookies, chrome, attackType, noApiScan)
    elif file:
        with open(file, 'rt') as f:
            for url in f.readlines():
                run_url(url.strip(), cookies, chrome, attackType, noApiScan)

if __name__ == '__main__':
    main()