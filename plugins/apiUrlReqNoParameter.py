try:
    from plugins.nodeCommon import *
except Exception as e:
    from nodeCommon import *

import os


def get_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, filePath_url_info):
    try:
        res = requests.get(url=api_url, headers=headers, timeout=TIMEOUT, verify=False, allow_redirects=False)
        res_code = res.status_code
        res_type = res.headers.get('Content-Type', "")
        text = res.text

        logger_print_content(f"[线程{i}] 剩下:{api_urls_queue.qsize()} [GET] {api_url}\t状态码:{res_code}\t类型:{res_type}\t响应包大小:{len(text)}")

        if res_code != 200 or ('xml' not in res_type and 'json' not in res_type):
            api_url_res.append({"url": api_url, 'Method': 'GET', "res_type": res_type, "res_code": res_code, 'res_size': len(text), 'referer_url': referer_url, 'file_path': '', 'parameter': ""})
            return

        file_name = re.sub(r'[^a-zA-Z0-9\.]', '_', api_url)
        file_path = f'{folder_path}/response/GET_{file_name}.txt'
        filePath_url_info[file_path] = api_url
        save_response_to_file(file_path, text)
        api_url_res.append({"url": api_url, 'Method': 'GET', "res_type": res_type, "res_code": res_code, 'res_size': len(text), 'referer_url': referer_url, 'file_path': file_path, 'parameter': ""})

    except Exception as e:
        return

def post_data_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, filePath_url_info):
    try:
        headers_post_data = headers.copy()
        headers_post_data["Content-Type"] = "application/x-www-form-urlencoded"
        res = requests.post(url=api_url, data="", headers=headers_post_data, timeout=TIMEOUT, verify=False, allow_redirects=False)
        res_code = res.status_code
        res_type = res.headers.get('Content-Type', "")
        text = res.text

        logger_print_content(f"[线程{i}] 剩下:{api_urls_queue.qsize()} [POST_DATA] {api_url}\t状态码:{res_code}\t类型:{res_type}\t响应包大小:{len(text)}")

        if res_code != 200 or ('xml' not in res_type and 'json' not in res_type):
            api_url_res.append({"url": api_url, 'Method': 'POST_DATA', "res_type": res_type, "res_code": res_code, 'res_size': len(text), 'referer_url': referer_url, 'file_path': '', 'parameter': ""})
            return

        file_name = re.sub(r'[^a-zA-Z0-9\.]', '_', api_url)
        file_path = f'{folder_path}/response/POST_DATA_{file_name}.txt'
        filePath_url_info[file_path] = api_url
        save_response_to_file(file_path, text)
        api_url_res.append({"url": api_url, 'Method': 'POST_DATA', "res_type": res_type, "res_code": res_code, 'res_size': len(text), 'referer_url': referer_url, 'file_path': file_path, 'parameter': ""})

    except Exception as e:
        return

def post_json_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, filePath_url_info):
    try:
        headers_json_data = headers.copy()
        headers_json_data["Content-Type"] = "application/json"
        res = requests.post(url=api_url, json={}, headers=headers_json_data, timeout=TIMEOUT, verify=False, allow_redirects=False)
        res_code = res.status_code
        res_type = res.headers.get('Content-Type', "")
        text = res.text

        logger_print_content(f"[线程{i}] 剩下:{api_urls_queue.qsize()} [POST_JSON] {api_url}\t状态码:{res_code}\t类型:{res_type}\t响应包大小:{len(text)}")

        if res_code != 200 or ('xml' not in res_type and 'json' not in res_type):
            api_url_res.append({"url": api_url, 'Method': 'POST_JSON', "res_type": res_type, "res_code": res_code, 'res_size': len(text), 'referer_url': referer_url, 'file_path': '', 'parameter': ""})
            return

        file_name = re.sub(r'[^a-zA-Z0-9\.]', '_', api_url)
        file_path = f'{folder_path}/response/POST_JSON_{file_name}.txt'
        filePath_url_info[file_path] = api_url
        save_response_to_file(file_path, text)
        api_url_res.append({"url": api_url, 'Method': 'POST_JSON', "res_type": res_type, "res_code": res_code, 'res_size': len(text), 'referer_url': referer_url, 'file_path': file_path, 'parameter': ""})

    except Exception as e:
        return

# 三种请求方式
def req_api_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, filePath_url_info):
    get_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, filePath_url_info)
    post_data_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, filePath_url_info)
    post_json_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, filePath_url_info)


def apiUrlReq(i, referer_url, api_urls_queue, headers, folder_path, api_url_res, filePath_url_info):
    while not api_urls_queue.empty():
        api_url = api_urls_queue.get()
        req_api_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, filePath_url_info)

def apiUrlReqNoParameter_api(referer_url, api_path_urls, cookies, folder_path, filePath_url_info):
    try:
        os.makedirs(f"{folder_path}/response/")
    except Exception as e:
        pass

    api_url_res = []

    if cookies:
        headers['Cookie'] = cookies
    # 新的js url队列，用来做消息队列，把所有新的js url都跑完
    api_urls_queue = Queue(-1)
    with open(f'{folder_path}/危险API接口.txt', 'at', encoding='utf-8') as f1, open(f'{folder_path}/安全API接口.txt', 'at', encoding='utf-8') as f2:
        for api_url in api_path_urls:
            # 过滤掉危险的API接口
            if any(dangerApi in urlparse(api_url).path.lower() for dangerApi in dangerApiList):
                logger_print_content(f"dangerApi : {api_url}")
                f1.writelines(f"{api_url}\n")
            # 安全的API接口进入扫描队列
            else:
                f2.writelines(f"{api_url}\n")
                api_urls_queue.put(api_url)

    threads = []
    for i in range(300):
        t = threading.Thread(target=apiUrlReq, args=(i, referer_url, api_urls_queue, headers, folder_path, api_url_res, filePath_url_info))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


    return api_url_res

