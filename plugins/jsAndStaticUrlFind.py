import json
import time

try:
    from plugins.nodeCommon import *
except Exception as e:
    from nodeCommon import *


domainblacklist=[
    "www.w3.org", "example.com", "github.com", "example.org", "www.google", "googleapis.com"
]

def jsFilter(lst):
    tmp = []
    for line in lst:
        line = line.replace("\\/", "/")
        line = line.replace(" ", "")
        line = line.replace("\"", "")
        line = line.replace("'", "")
        line = line.replace("./", "/")
        line = line.replace("%3A", ":")
        line = line.replace("%2F", "/")
        # 新增排除\\
        line = line.replace("\\\\", "")
        if line.endswith("\\"):
            line = line.rstrip("\\")
        if line.startswith("="):
            line = line.lstrip("=")
        for x in domainblacklist:
            if x in line:
                line = ""
                break
        tmp.append(line)
    return tmp


def staticUrlFilter(domain, base_paths):
    tmp = []
    for base_path in base_paths:
        if len(base_path) < 3 or base_path.endswith('.js') or any(ext in base_path.lower() for ext in staticUrlExtBlackList):
            continue
        elif 'http' in base_path:
            if domain not in base_path :
                pass
            else:
                tmp.append(base_path)
        else:
            tmp.append(base_path)
    return list(set(tmp))

def webpack_js_find(js_content):
    try:
        # 使用正则表达式提取基路径和JSON映射表
        re_result = re.search(r'return [a-zA-Z]\.p\+"([^"]+).*\{(.*)\}\[[a-zA-Z]\]\+\"\.js\"\}', js_content)
        base_path = re_result.group(1)
        json_string = re_result.group(2)

        # 通过分割处理每个键值对
        pairs = json_string.split(',')
        formatted_pairs = []
        for pair in pairs:
            key, value = pair.split(':')
            # 确保键被引号包裹
            if not key.startswith('"'):
                continue
            # 确保值被引号包裹
            if not value.startswith('"'):
                continue
            formatted_pairs.append(key + ':' + value)

        chunk_mapping = json.loads('{' + ','.join(formatted_pairs) + '}')
        # 构造完整路径
        js_paths = ['/' + base_path + key + '.' + value + '.js' for key, value in chunk_mapping.items()]
        return js_paths
    except Exception as e:
        # print(e.args)
        return []

def get_new_url(scheme, base, root_path, path):
    if path == "" or path == '//' or path == '/':
        return ''
    path_parts = path.split('/')
    if path.startswith("https:") or path.startswith("http:"):
        new_url = path
    elif path.startswith("//"):
        new_url = scheme + ":" + path
    elif path.startswith("/"):
        new_url = base + path
    elif path.startswith("js/"):
        new_url = base + '/' + path
    elif len(path_parts) > 1:
        new_url = base + '/' + path
    else:
        new_url = base + root_path + path

    return new_url



def js_and_staticUrl_find(i, headers, js_and_staticUrl_info, urls, domain, js_and_staticUrl_alive_info_tmp, folder_path, filePath_url_info):
    while not queue.empty():
        url = queue.get()
        get_js_and_staticUrl(i, headers, js_and_staticUrl_info, url, urls, domain, js_and_staticUrl_alive_info_tmp, folder_path, filePath_url_info)

def get_js_and_staticUrl(i, headers, js_and_staticUrl_info, url, urls, domain, js_and_staticUrl_alive_info_tmp, folder_path, filePath_url_info):
    try:
        # logger_print_content(f"[线程{i}] 剩下:{queue.qsize()} {url} 获取页面里的js url")
        # response = requests.head(url=url, headers=headers, timeout=TIMEOUT, verify=False, allow_redirects=False)
        # print(response.headers)
        res = requests.get(url=url, headers=headers, timeout=TIMEOUT, verify=False, allow_redirects=False, stream=True)
        code = res.status_code
        if code != 200:
            logger_print_content(f"[状态码非200，过滤掉] [{code}] {url}")
            return

        Content_Disposition = res.headers.get('Content-Disposition')# 获取网页源代码
        logger_print_content(f"[Content-Disposition] {url} {Content_Disposition}")
        if Content_Disposition:
            if 'attachment' in Content_Disposition:
                logger_print_content(f"[下载文件，过滤掉] {url} {Content_Disposition}")
                return

        # logger_print_content(f"[线程{i}] 剩下:{queue.qsize()} {url} 获取页面里的js url")
        # res = requests.get(url=url, headers=headers, timeout=TIMEOUT, verify=False, allow_redirects=False)
        # logger_print_content(f"[线程{i}] 剩下:{queue.qsize()} {url} 获取页面里的js url\t状态码:{res.status_code}\t长度:{len(res.text)}")

        text = res.text
        logger_print_content(f"[线程{i}] 剩下:{queue.qsize()} {url} 获取页面里的js url\t状态码:{code}\t长度:{len(text)}")

        file_name = re.sub(r'[^a-zA-Z0-9\.]', '_', url)
        file_path = f'{folder_path}/js_response/JS_{file_name}.txt'
        filePath_url_info[file_path] = url
        save_response_to_file(file_path, text)

        js_and_staticUrl_alive_info_tmp.append({"url": url, "code": code, "length": len(text)})


    except Exception as e:
        # logger_print_content(print_exc())
        # logger_print_content(e.args)
        # js_and_staticUrl_alive_info_tmp.append({"url": url, "code": 0, "length": 0})
        return

    # 获取url的相关元素
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    path = parsed_url.path
    host = parsed_url.hostname
    port = parsed_url.port

    base = f"{scheme}://{host}"
    if port:
        base += f":{port}"

    # 从基础URL中提取路径部分，并去掉文件名
    # base_path_sections = parsed_url.path.rsplit('/', 1)[0].split('/')

    # 正则匹配 删除掉最后的js路径名 例如：/static/js/elicons.626b260a.js 得到 /static/js/
    pattern = re.compile(r'/.*/{1}|/')
    root_result = pattern.findall(path)
    if root_result:
        root_path = root_result[0]
    else:
        root_path = "/"

    # print(scheme, host, base, root_path)
    # 从基础URL中提取路径部分，并删除最后一个路径部分（通常是文件名）
    # root_path = parsed_url.path.rsplit('/', 1)[0]

    # \.js\b：确保路径以 .js 结束，并且后面是一个单词边界，以避免像 .json 这样的后缀被错误匹配。
    js_patterns = [
        r'http[^\s\'’"\>\<\:\(\)\[\,]+?\.js\b',
        r'["\']/[^\s\'’"\>\<\:\(\)\[\,]+?\.js\b',
        r'=[^\s\'’"\>\<\:\(\)\[\,]+?\.js\b',
        r'=["\'][^\s\'’"\>\<\:\(\)\[\,]+?\.js\b',
    ]

    staticUrl_patterns = [
        # r'(?:"|\')(https?://[^"\'\s\,\>]*|/[^"\'\s\,\>]*?)(?<!\.js)(?="|\')'
        r'["\']http[^\s\'’"\>\<\)\(]+?[\"\']',
        r'=http[^\s\'’"\>\<\)\(]+',
        r'[\"\']/[^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]+?["\']',
    ]

    # 正则匹配获取所有的js路径
    for js_pattern in js_patterns:
        js_paths = re.findall(js_pattern, text)
        js_paths = ["".join(x.strip("\"'")) for x in js_paths]
        js_paths = list(set(js_paths))
        if not js_paths:
            continue

        logger_print_content(f"{url}匹配出如下的js url:{js_paths}")
        js_paths = jsFilter(js_paths)
        # js_paths = [x.rstrip("\\") if x.endswith("\\") else x for x in js_paths]
        logger_print_content(f"{url}调整后得到如下的js url:{js_paths}")
        # js_paths = ['="static/js/elicons.626b260a.js', '="static/js/modules.d59689f1.js', '="static/js/app.397cfa65.js']
        js_and_staticUrl_info['js_paths'].extend(js_paths)

        # 组合成新的js url
        for js_path in js_paths:
            new_js_url = get_new_url(scheme, base, root_path, js_path)
            # 判断新的js url是否已经在js_urls列表里
            if not new_js_url:
                continue
            elif new_js_url in urls:
                logger_print_content(f"[-] {new_js_url}已经在urls列表里")
                # pass
            else:
                logger_print_content(f"[+] {new_js_url} 新增js url并加入到队列里")
                urls.append(new_js_url)
                queue.put(new_js_url)

            js_and_staticUrl_info['js_url'].append({'url': new_js_url, 'referer': url, 'url_type': "js_url"})

    # 静态URL
    for staticUrl_pattern in staticUrl_patterns:
        static_paths = re.findall(staticUrl_pattern, text)
        static_paths = [x.strip('\'" ').rstrip('/') for x in static_paths]
        static_paths = list(set(static_paths))
        if not static_paths:
            continue
        logger_print_content(f"{url}匹配出如下的static_paths:{static_paths}")
        static_paths = staticUrlFilter(domain, static_paths)
        if len(static_paths) > 20:
            continue
        logger_print_content(f"{url}调整后得到如下的static_paths:{static_paths}")
        js_and_staticUrl_info['static_paths'].extend(static_paths)

        for static_path in static_paths:
            static_url = get_new_url(scheme, base, root_path, static_path)
            logger_print_content(f"{url}调整后得到如下的static_url:{static_url}")
            logger_print_content(f"static_url: {static_url}")
            if not static_url:
                continue
            elif static_url in urls:
                logger_print_content(f"[-] {static_url} 已经在urls列表里")
                # pass
            else:
                logger_print_content(f"[+] {static_url} 新增static url并加入到队列里")
                urls.append(static_url)
                queue.put(static_url)

            js_and_staticUrl_info['static_url'].append({'url': static_url, 'referer': url, 'url_type': "static_url"})

    # webpack获取js
    js_paths = webpack_js_find(text)
    if js_paths:
        logger_print_content(f"【WEBPACK】{url} 匹配出如下的js url:{js_paths}")
        js_and_staticUrl_info['js_paths'].extend(js_paths)
        # 组合成新的js url
        for js_path in js_paths:
            new_js_url = get_new_url(scheme, base, root_path, js_path)
            # 判断新的js url是否已经在js_urls列表里
            if not new_js_url:
                continue
            elif new_js_url in urls:
                logger_print_content(f"[-] {new_js_url}已经在urls列表里")
                # pass
            else:
                logger_print_content(f"[+] {new_js_url} 新增js url并加入到队列里")
                urls.append(new_js_url)
                queue.put(new_js_url)

            js_and_staticUrl_info['js_url'].append({'url': new_js_url, 'referer': url, 'url_type': "js_url"})

    # print("\n")





def js_find_api(domain, urls, cookies, folder_path, filePath_url_info):
    try:
        os.makedirs(f"{folder_path}/js_response/")
    except Exception as e:
        pass

    global queue
    js_and_staticUrl_info = {
        "js_paths": [],
        "js_url": [],
        "static_paths": [],
        "static_url": [],
    }

    # 记录每个js的来源
    # js_url_refer = []

    js_and_staticUrl_alive_info_tmp = []

    if cookies:
        headers['Cookie'] = cookies
    # 新的js url队列，用来做消息队列，把所有新的js url都跑完
    queue = Queue(-1)
    for url in urls:
        queue.put(url)

    threads = []
    for i in range(300):
        t = threading.Thread(target=js_and_staticUrl_find, args=(i, headers, js_and_staticUrl_info, urls, domain, js_and_staticUrl_alive_info_tmp, folder_path, filePath_url_info))
        threads.append(t)
        t.start()
        time.sleep(0.2)

    for t in threads:
        t.join()

    # logger_print_content(f"从网页源码匹配到的所有js url\njs_find_urls = {js_find_urls}\n\n")

    js_and_staticUrl_info['js_paths'] = list(set(js_and_staticUrl_info['js_paths']))
    js_and_staticUrl_info['static_paths'] = list(set(js_and_staticUrl_info['static_paths']))

    print(js_and_staticUrl_alive_info_tmp)

    js_and_staticUrl_alive_info = []
    for _1 in js_and_staticUrl_alive_info_tmp:
        for _2 in js_and_staticUrl_info['js_url'] + js_and_staticUrl_info['static_url']:
            if _1['url'] == _2['url']:
                url, referer, url_type, code, length = _2['url'], _2['referer'], _2['url_type'], _1['code'], _1['length']
                if code != 404:
                    js_and_staticUrl_alive_info.append({"url": url, "code": code, "length": length, "url_type": url_type, "referer": referer})
                    break


    print(js_and_staticUrl_alive_info)
    return js_and_staticUrl_info, js_and_staticUrl_alive_info
