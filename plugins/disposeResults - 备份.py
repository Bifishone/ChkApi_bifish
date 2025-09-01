import os
from collections import defaultdict
from hashlib import sha256
import shutil

import yaml

try:
    from plugins.nodeCommon import *
except Exception as e:
    from nodeCommon import *

try:
    with open('./plugins/rule.yaml', 'r') as file:
        hae_rule = yaml.safe_load(file)
except Exception as e:
    with open('./rule.yaml', 'r') as file:
        hae_rule = yaml.safe_load(file)

try:
    with open('./plugins/sensitive_data_rule.yaml', 'r') as file:
        sensitive_data_rule = yaml.safe_load(file)
except Exception as e:
    with open('./sensitive_data_rule.yaml', 'r') as file:
        sensitive_data_rule = yaml.safe_load(file)

# 差异化response
def diff_response_api(folder_path, filePath_url_info):
    diff_response_info = []
    all_files = []
    content_count = defaultdict(list)  # 存储内容哈希值和相应文件路径的列表
    file_sizes = {}  # 存储每个哈希值对应的文件大小

    # 确保差异化response目录存在
    diff_response_dir = f"{folder_path}/差异化response"
    os.makedirs(diff_response_dir, exist_ok=True)

    # 文件用于存储哈希值、文件大小和文件名
    hash_file_path = os.path.join(f"{folder_path}/8-1-响应包diff_hash.txt")
    with open(hash_file_path, 'wt', encoding='utf-8') as hash_file, open(f"./result.txt", 'at', encoding='utf-8') as result_file:
        for root, _, files in os.walk(f"{folder_path}/response"):
            for file in files:
                # if file.startswith('GET'):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'rb') as f:
                        content = f.read()
                        content_hash = sha256(content).hexdigest()
                        content_count[content_hash].append(full_path)
                        file_size = os.path.getsize(full_path)
                        # 只记录第一次计算的文件大小，假设相同哈希的文件大小相同
                        if content_hash not in file_sizes:
                            file_sizes[content_hash] = file_size
                except IOError as e:
                    pass
                    # print(f"读取文件 {full_path} 时出错：{e}")

                # print(full_path)
                # all_files.append(full_path)

        # 根据每个哈希值对应的文件数量从小到大排序，并在出现次数相同的情况下按文件大小从大到小排序
        sorted_hashes = sorted(content_count.items(), key=lambda item: (len(item[1]), -file_sizes[item[0]]))
        for content_hash, paths in sorted_hashes:
            size = file_sizes[content_hash]
            hash_file.write(f"{content_hash} ({len(paths)} 次, 大小: {size} 字节):\n")
            for path in paths:
                hash_file.write(f"{path}\n")

            if len(paths) < 10:
                result_file.writelines(f"{content_hash} ({len(paths)} 次, 大小: {size} 字节):\n")
                for path in paths:
                    url = filePath_url_info.get(path, "")
                    result_file.write(f"{path}\n")
                    diff_response_info.append([content_hash, len(paths), size, url, path])

        # 处理每个哈希值，将出现次数小于10次的文件复制到差异化response目录
        for paths in content_count.values():
            if len(paths) < 10:
                for path in paths:
                    dest_path = os.path.join(diff_response_dir, os.path.basename(path))
                    shutil.copy2(path, dest_path)  # 使用copy2以保留元数据
                    logger_print_content(f"文件 {path} 已复制到 {dest_path}")


    return diff_response_info

# 过滤脏数据，结果归整
def filter_dirty_pack_response_api(folder_path):
    def get_all_files():
        all_files = []
        prefixes = ('GET', 'POST')
        # 读取所有文件
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.startswith(prefixes):
                    full_path = os.path.join(root, file)
                    # print(full_path)
                    all_files.append(full_path)
        return all_files

    all_files = get_all_files()
    if all_files:
        pack_file = os.path.join(f"{folder_path}/8-2-响应包结果归整.txt")
        with open(pack_file, 'wt', encoding='utf-8') as f2:
            for file in all_files:
                try:
                    with open(file, 'rt', encoding='utf-8') as f3:
                        text = f3.read().strip()
                        if not text:
                           continue
                        flag = False
                        for balcktext in BLACK_TEXT:
                            if balcktext in text:
                                flag = True
                                break
                        if not flag:
                            f2.writelines(f"[file] {file}\n{text}\n\n\n----------------------------------------------------------------------------------------------------\n")
                except Exception as e:
                    logger_print_content(f'filter_dirty_pack_response_api Error: {e.args}')
        return pack_file

def filter_dirty_pack_js_response_api(folder_path):
    def get_all_files():
        all_files = []
        prefixes = ('JS_')
        # 读取所有文件
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.startswith(prefixes):
                    full_path = os.path.join(root, file)
                    # print(full_path)
                    all_files.append(full_path)
        return all_files

    all_files = get_all_files()
    if all_files:
        pack_file = os.path.join(f"{folder_path}/8-3-JS_响应包结果归整.txt")
        with open(pack_file, 'wt', encoding='utf-8') as f2:
            for file in all_files:
                try:
                    with open(file, 'rt', encoding='utf-8') as f3:
                        text = f3.read().strip()
                        if not text:
                           continue
                        f2.writelines(f"[file] {file}\n{text}\n\n\n----------------------------------------------------------------------------------------------------\n")
                except Exception as e:
                    logger_print_content(f'Error: {e.args}')
        return pack_file

# hae获取敏感数据
def hae_api(folder_path, filePath_url_info):
    def get_all_files():
        all_files = []
        prefixes = ('GET', 'POST', 'JS_')
        # 读取所有文件
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.startswith(prefixes):
                    full_path = os.path.join(root, file)
                    # print(full_path)
                    all_files.append(full_path)
        return all_files

    all_files = get_all_files()
    hae_api_info = []
    hae_file = os.path.join(f"{folder_path}/8-4-hae检测结果.txt")

    if all_files:
        with open(hae_file, 'at', encoding='utf-8') as f2:
            for file in all_files:
                url = filePath_url_info.get(file, "")
                with open(file, 'rt', encoding='utf-8') as f:
                    text = f.read()
                    # 打印读取的数据
                    for group in hae_rule['rules']:
                        for _ in group['rule']:
                            name, f_regex = _['name'], _['f_regex']
                            matches_result = re.findall(f_regex, text)
                            matches = []
                            for i in matches_result:
                                if isinstance(i, tuple):
                                    for j in i:
                                        if j:
                                            matches.append(j)
                                else:
                                    matches.append(i)
                            # matches = [__ for __ in _ for _ in matches_result]
                            matches = tuple(set(matches))
                            if matches and len(str(matches)) < 99999:
                                if (name, matches, url, file) not in hae_api_info:
                                    hae_api_info.append((name, matches, url, file))
                                f2.writelines(f'{name}\t|\t{matches}\t|\t{url}|\t{file}\n')

    hae_api_info = list(set(hae_api_info))
    for _ in hae_api_info:
        print(_)
    return hae_api_info

def sensitive_data_api(folder_path, filePath_url_info):
    def get_all_files():
        all_files = []
        prefixes = ('GET', 'POST', 'JS_')
        # 读取所有文件
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.startswith(prefixes):
                    full_path = os.path.join(root, file)
                    # print(full_path)
                    all_files.append(full_path)
        return all_files

    all_files = get_all_files()
    sensitive_data_info = []
    sensitive_data_file = os.path.join(f"{folder_path}/8-5-敏感信息检测结果.txt")
    # num = 0

    if all_files:
        with open(sensitive_data_file, 'at', encoding='utf-8') as f2:
            for file in all_files:
                url = filePath_url_info.get(file, "")
                # num += 1
                # print(f"[{len(all_files)}]第{num}个文件:{file}")
                with open(file, 'rt', encoding='utf-8') as f:
                    text = f.read()
                    # 打印读取的数据
                    for _ in sensitive_data_rule['rules']:
                        name, f_regex = _['id'], _['pattern']
                        matches_result = re.findall(f_regex, text)
                        matches = []
                        for i in matches_result:
                            if isinstance(i, tuple):
                                for j in i:
                                    if j:
                                        matches.append(j)
                            else:
                                matches.append(i)
                        # matches = [__ for __ in _ for _ in matches_result]
                        matches = tuple(set(matches))
                        if matches and len(str(matches)) < 99999:
                            if (name, matches, url, file) not in sensitive_data_info:
                                sensitive_data_info.append((name, matches, url, file))
                            f2.writelines(f'{name}\t|\t{matches}\t|\t{url}|\t{file}\n')

    sensitive_data_info = list(set(sensitive_data_info))
    for _ in sensitive_data_info:
        print(_)
    return sensitive_data_info

def disposeResults_api(folder_path, filePath_url_info):
    # filter_dirty_pack_response_api(folder_path)
    # filter_dirty_pack_js_response_api(folder_path)
    hae_api_info = hae_api(folder_path, filePath_url_info)
    sensitive_data_info = sensitive_data_api(folder_path, filePath_url_info)
    diff_response_info = diff_response_api(folder_path, filePath_url_info)

    disposeResults_info = {
        "diff_response_info": diff_response_info,
        "hae_api_info": hae_api_info,
        "sensitive_data_info": sensitive_data_info
    }

    return disposeResults_info
