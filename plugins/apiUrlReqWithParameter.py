import json

try:
    from plugins.nodeCommon import *
except Exception as e:
    from nodeCommon import *

import os

proxies = None

def get_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, parameters, filePath_url_info):
    try:
        # 构建查询字符串
        query_params = {param: '' for param in parameters}  # 假设所有参数的值为'value'
        query_string = "&".join([f"{key}={value}" for key, value in query_params.items()])
        api_parameters_url = f"{api_url}?{query_string}"

        res = requests.get(url=api_parameters_url, headers=headers, timeout=TIMEOUT, verify=False, allow_redirects=False, proxies=proxies)
        res_code = res.status_code
        res_type = res.headers.get('Content-Type', "")
        text = res.text

        logger_print_content(f"[线程{i}] 剩下:{api_urls_queue.qsize()} [GET] {api_parameters_url}\t状态码:{res_code}\t类型:{res_type}\t响应包大小:{len(text)}")

        if res_code != 200 or ('xml' not in res_type and 'json' not in res_type):
            api_url_res.append({"url": api_parameters_url, 'Method': 'GET', "res_type": res_type, "res_code": res_code, 'res_size': len(text), 'referer_url': referer_url, 'file_path': '', 'parameter': query_string})
            return

        file_name = re.sub(r'[^a-zA-Z0-9\.]', '_', api_url)
        file_path = f'{folder_path}/response/GET_PARAMETERS_{file_name}.txt'
        filePath_url_info[file_path] = api_url
        save_response_to_file(file_path, text)
        api_url_res.append({"url": api_parameters_url, 'Method': 'GET', "res_type": res_type, "res_code": res_code, 'res_size': len(text), 'referer_url': referer_url, 'file_path': file_path, 'parameter': query_string})

    except Exception as e:
        return

def post_data_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, parameters, filePath_url_info):
    try:
        # 构建查询字符串
        query_params = {param: '' for param in parameters}  # 假设所有参数的值为'value'
        query_string = "&".join([f"{key}={value}" for key, value in query_params.items()])

        headers_post_data = headers.copy()
        headers_post_data["Content-Type"] = "application/x-www-form-urlencoded"
        res = requests.post(url=api_url, data=query_string, headers=headers_post_data, timeout=TIMEOUT, verify=False, allow_redirects=False, proxies=proxies)
        res_code = res.status_code
        res_type = res.headers.get('Content-Type', "")
        text = res.text

        logger_print_content(f"[线程{i}] 剩下:{api_urls_queue.qsize()} [POST_DATA] {api_url}\t[DATA] {query_string}\t状态码:{res_code}\t类型:{res_type}\t响应包大小:{len(text)}")

        if res_code != 200 or ('xml' not in res_type and 'json' not in res_type):
            api_url_res.append({"url": api_url, 'Method': 'POST_DATA', "res_type": res_type, "res_code": res_code, 'res_size': len(text), 'referer_url': referer_url, 'file_path': '', 'parameter': query_string})
            return

        file_name = re.sub(r'[^a-zA-Z0-9\.]', '_', api_url)
        file_path = f'{folder_path}/response/POST_DATA_PARAMETERS_{file_name}.txt'
        filePath_url_info[file_path] = api_url
        save_response_to_file(file_path, text)
        api_url_res.append({"url": api_url, 'Method': 'POST_DATA', "res_type": res_type, "res_code": res_code, 'res_size': len(text), 'referer_url': referer_url, 'file_path': file_path, 'parameter': query_string})

    except Exception as e:
        return

def post_json_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, parameters, filePath_url_info):
    try:
        # 构建查询字符串
        query_params = {param: '' for param in parameters}  # 假设所有参数的值为'value'
        query_string = json.dumps(query_params)

        headers_json_data = headers.copy()
        headers_json_data["Content-Type"] = "application/json"
        res = requests.post(url=api_url, json=query_params, headers=headers, timeout=TIMEOUT, verify=False, allow_redirects=False, proxies=proxies)
        res_code = res.status_code
        res_type = res.headers.get('Content-Type', "")
        text = res.text

        logger_print_content(f"[线程{i}] 剩下:{api_urls_queue.qsize()} [POST_JSON] {api_url}\t[JSON] {query_params}\t状态码:{res_code}\t类型:{res_type}\t响应包大小:{len(text)}")

        if res_code != 200 or ('xml' not in res_type and 'json' not in res_type):
            api_url_res.append({"url": api_url, 'Method': 'POST_JSON', "res_type": res_type, "res_code": res_code, 'res_size': len(text), 'referer_url': referer_url, 'file_path': '', 'parameter': query_string})
            return

        file_name = re.sub(r'[^a-zA-Z0-9\.]', '_', api_url)
        file_path = f'{folder_path}/response/POST_JSON_PARAMETERS_{file_name}.txt'
        filePath_url_info[file_path] = api_url
        save_response_to_file(file_path, text)
        api_url_res.append({"url": api_url, 'Method': 'POST_JSON', "res_type": res_type, "res_code": res_code, 'res_size': len(text), 'referer_url': referer_url, 'file_path': file_path, 'parameter': query_string})

    except Exception as e:
        return

# 三种请求方式
def req_api_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, parameters, filePath_url_info):
    get_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, parameters, filePath_url_info)
    post_data_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, parameters, filePath_url_info)
    post_json_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, parameters, filePath_url_info)


def apiUrlReqWithParameter(i, referer_url, api_urls_queue, headers, folder_path, api_url_res, parameters, filePath_url_info):
    while not api_urls_queue.empty():
        api_url = api_urls_queue.get()
        req_api_url(i, referer_url, api_urls_queue, api_url, headers, folder_path, api_url_res, parameters, filePath_url_info)

def apiUrlReqWithParameter_api(referer_url, xml_json_api_url, cookies, folder_path, parameters, filePath_url_info):
    api_url_res = []

    if cookies:
        headers['Cookie'] = cookies
    # 新的js url队列，用来做消息队列，把所有新的js url都跑完
    api_urls_queue = Queue(-1)
    for api_url in xml_json_api_url:
        api_urls_queue.put(api_url)

    threads = []
    for i in range(300):
        t = threading.Thread(target=apiUrlReqWithParameter, args=(i, referer_url, api_urls_queue, headers, folder_path, api_url_res, parameters, filePath_url_info))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


    return api_url_res
