try:
    from plugins.nodeCommon import *
except Exception as e:
    from nodeCommon import *


english_parameter_list = [
    r"'([a-zA-Z]+)' parameter",
    r'"([a-zA-Z]+)" parameter',
    r'([a-zA-Z]+) parameter',
    r'\(([a-zA-Z]+)[=]*\) parameter',

    r"parameter '([a-zA-Z]+)'",
    r'parameter "([a-zA-Z]+)"',
    r'parameter ([a-zA-Z]+)',
    r'parameter \(([a-zA-Z]+)[=]*\)',

    r"'([a-zA-Z]+)' param",
    r'"([a-zA-Z]+)" param',
    r'([a-zA-Z]+) param',
    r'\(([a-zA-Z]+)[=]*\) param',

    r"param '([a-zA-Z]+)'",
    r'param "([a-zA-Z]+)"',
    r'param ([a-zA-Z]+)',
    r'param \(([a-zA-Z]+)[=]*\)',

    r'parameter ([a-zA-Z]+) ',
    r'param\[([a-zA-Z]+)\] required',
    r'parameter\[([a-zA-Z]+)\] required',
]
# english_paramete_patterns = '|'.join(english_parameter_list)

chinese_parameter_list = ["不能为空", "非法的", "参数"]
chinese_paramete_patterns = r"(['\"]?)([a-zA-Z]+)\1\s*(?:{})|(?:(?:{})\s*['\"]?([a-zA-Z]+)['\"]?)".format('|'.join(chinese_parameter_list), '|'.join(chinese_parameter_list))

# 定义用于检查是否包含中文字符的正则表达式
chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')

def extract_info_from_nested_data(data, current_depth=1, target_depth=2):
    # 初始化用来存储找到的键和参数的列表
    keys = []
    params = []

    # 判断当前数据点是否为字典类型
    if isinstance(data, dict):
        # 如果当前深度已达到或超过目标深度，则收集当前层的所有键
        if current_depth >= target_depth:
            keys.extend(data.keys())
        # 遍历字典中的每一个键值对
        for key, value in data.items():
            # 如果键是'param'或'parameter'且值为字符串，将该值添加到参数列表中
            if key in ['param', 'parameter'] and isinstance(value, str):
                # print(f"1111111:{value}")
                params.append(value)
            # 如果值是字典或列表，递归调用此函数以深入处理
            if isinstance(value, (dict, list)):
                nested_keys, nested_params = extract_info_from_nested_data(value, current_depth + 1, target_depth)
                keys.extend(nested_keys)
                params.extend(nested_params)
            # 如果值是字符串，检查字符串中是否包含参数
            elif isinstance(value, str):
                # 使用正则表达式检测是否含有中文字符，并提取参数
                if chinese_pattern.search(value):
                    extracted_params = re.findall(chinese_paramete_patterns, value)
                else:
                    # 独立处理每个英文正则表达式以查找匹配项
                    extracted_params = []
                    for pattern in english_parameter_list:
                        matches = re.findall(pattern, value)
                        extracted_params.extend(matches)
                # 处理所有提取的参数，将元组中的参数扁平化添加到params列表中
                for match in extracted_params:
                    if isinstance(match, tuple):
                        params.extend([param for param in match if param])
                    else:
                        params.append(match)
    # 如果当前数据点是列表，遍历列表中的每一个元素
    elif isinstance(data, list):
        for item in data:
            # 为列表中的每一项递归调用此函数
            nested_keys, nested_params = extract_info_from_nested_data(item, current_depth + 1, target_depth)
            # 收集更深层次的键
            keys.extend(nested_keys)
            # 收集更深层次的参数
            params.extend(nested_params)
    # 返回去重后的键和参数，保持顺序不变
    return remove_duplicates(keys), remove_duplicates(params)

def getParameter_api(folder_path):
    parameters = []
    all_files = list_files(folder_path)
    for file in all_files:
        with open(file, 'rt', encoding='utf-8') as f:
            try:
                text = eval(f.read())
                result_keys, result_params = extract_info_from_nested_data(text)
                if not result_params:
                    result_params = result_keys
                if result_params:
                    print(f"{result_params}\t{type(text)}\t{file}")
                    parameters.extend(result_params)
            except Exception as e:
                pass
    return parameters
