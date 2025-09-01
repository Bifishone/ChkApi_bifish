
try:
    from plugins.nodeCommon import *
except Exception as e:
    from nodeCommon import *

# 增加content-type tag库
contentTypeList=[#使用 in 逻辑
    {'key': 'text/html', 'tag': 'html'},
    {'key': 'application/json', 'tag': 'json'},
    {'key': 'text/plain', 'tag': 'txt'},
    {'key': 'text/xml', 'tag': 'xml'},
    {'key': 'text/javascript', 'tag': 'js'},
    {'key': 'image/gif', 'tag': 'gif'},
    {'key': 'image/jpeg', 'tag': 'jpg'},
    {'key': 'image/jpg', 'tag': 'jpg'},
    {'key': 'image/png', 'tag': 'png'},
    {'key': 'image/*', 'tag': 'img'},
    {'key': 'image/x-icon', 'tag': 'ico'},
    # {'key': 'ico', 'tag': 'ico'},
    {'key': 'application/xhtml+xml', 'tag': 'xhtml'},
    {'key': 'application/xml', 'tag': 'xml'},
    {'key': 'application/atom+xml', 'tag': 'atom+xml'},
    {'key': 'application/octet-stream', 'tag': 'bin'},
    {'key': 'binary/octet-stream', 'tag': 'bin'},
    {'key': 'audio/x-wav', 'tag': 'wav'},
    {'key': 'audio/x-ms-wma', 'tag': 'w文件'},
    {'key': 'audio/mp3', 'tag': 'mp3'},
    {'key': 'video/x-ms-wmv', 'tag': 'wmv'},
    {'key': 'video/mpeg4', 'tag': 'mp4'},
    {'key': 'video/avi', 'tag': 'avi'},
    {'key': 'application/pdf', 'tag': 'pdf'},
    {'key': 'application/msword', 'tag': 'msword'},
    {'key': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'tag': 'docx'},
    {'key': 'application/vnd.ms-excel', 'tag': 'excel'},
    {'key': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'tag': 'xlsx'},
    {'key': 'application/vnd.ms-powerpoint', 'tag': 'ppt'},
    {'key': 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'tag': 'pptx'},
    {'key': 'application/zip', 'tag': 'zip'},
    {'key': 'application/x-zip-compressed', 'tag': 'zip'},
    {'key': 'application/x-tar', 'tag': 'tar'},
    {'key': 'multipart/form-data', 'tag': 'file'},
    {'key': 'application/vnd.tcpdump.pcap', 'tag': 'pcap'},
    {'key': 'application/x-www-form-urlencoded', 'tag': 'post'},
    {'key': 'application/vnd.spring-boot.actuator.v2+json', 'tag': 'spring-json'},
    {'key': 'text/x-cobol', 'tag': 'x-cobol'},
    {'key': 'application/mbox', 'tag': 'mbox'},
    {'key': 'application/n-triples', 'tag': 'n-triples'},
    {'key': 'text/x-gpsql', 'tag': 'x-gpsql'},
    {'key': 'text/x-chdr', 'tag': 'x-chdr'},
    {'key': 'text/x-modelica', 'tag': 'x-modelica'},
    {'key': 'text/babel$', 'tag': 'babel$'},
    {'key': 'text/x-groovy', 'tag': 'x-groovy'},
    {'key': 'text/x-sparksql', 'tag': 'x-sparksql'},
    {'key': 'text/x-octave', 'tag': 'x-octave'},
    {'key': 'x-shader/x-fragment', 'tag': 'x-fragment'},
    {'key': 'text/x-haml', 'tag': 'x-haml'},
    {'key': 'text/x-c++hdr', 'tag': 'x-c++hdr'},
    {'key': 'text/x-gfm', 'tag': 'x-gfm'},
    {'key': 'text/x-esper', 'tag': 'x-esper'},
    {'key': 'stylesheet/less', 'tag': 'less'},
    {'key': 'application/x-erb', 'tag': 'x-erb'},
    {'key': 'text/markdown', 'tag': 'markdown'},
    {'key': 'application/pgp-encrypted', 'tag': 'pgp-encrypted'},
    {'key': 'text/x-latex', 'tag': 'x-latex'},
    {'key': 'text/x-python', 'tag': 'x-python'},
    {'key': 'text/x-tiddlywiki', 'tag': 'x-tiddlywiki'},
    {'key': 'text/x-squirrel', 'tag': 'x-squirrel'},
    {'key': 'text/mirc', 'tag': 'mirc'},
    {'key': 'application/x-javascript', 'tag': 'x-javascript'},
    {'key': 'text/troff', 'tag': 'troff'},
    {'key': 'text/x-nginx-conf', 'tag': 'x-nginx-conf'},
    {'key': 'text/typescript-jsx', 'tag': 'typescript-jsx'},
    {'key': 'message/http', 'tag': 'http'},
    {'key': 'text/x-hive', 'tag': 'x-hive'},
    {'key': 'text/x-xu', 'tag': 'x-xu'},
    {'key': 'text/x-clojure', 'tag': 'x-clojure'},
    {'key': 'text/x-idl', 'tag': 'x-idl'},
    {'key': 'text/x-gql', 'tag': 'x-gql'},
    {'key': 'text/x-pug', 'tag': 'x-pug'},
    {'key': 'text/apl', 'tag': 'apl'},
    {'key': 'application/xquery', 'tag': 'xquery'},
    {'key': 'audio/wav', 'tag': 'wav'},
    {'key': 'text/x-php', 'tag': 'x-php'},
    {'key': 'video/mp4', 'tag': 'mp4'},
    {'key': 'text/x-csharp', 'tag': 'x-csharp'},
    {'key': 'text/x-go', 'tag': 'x-go'},
    {'key': 'text/x-twig', 'tag': 'x-twig'},
    {'key': 'text/x-vue', 'tag': 'x-vue'},
    {'key': 'text/x-protobuf', 'tag': 'x-protobuf'},
    {'key': 'text/x-literate-haskell', 'tag': 'x-literate-haskell'},
    {'key': 'text/x-django', 'tag': 'x-django'},
    {'key': 'text/x-smarty', 'tag': 'x-smarty'},
    {'key': 'text/sass/i', 'tag': 'i'},
    {'key': 'text/vbscript', 'tag': 'vbscript'},
    {'key': 'text/jsx', 'tag': 'jsx'},
    {'key': 'text/x-rpm-spec', 'tag': 'x-rpm-spec'},
    {'key': 'application/ld+json', 'tag': 'ld+json'},
    {'key': 'application/x-powershell', 'tag': 'x-powershell'},
    {'key': 'text/x-elm', 'tag': 'x-elm'},
    {'key': 'text/x-cmake', 'tag': 'x-cmake'},
    {'key': 'text/x-erlang', 'tag': 'x-erlang'},
    {'key': 'text/x-fsharp', 'tag': 'x-fsharp'},
    {'key': 'text/x-livescript', 'tag': 'x-livescript'},
    {'key': 'text/x-pig', 'tag': 'x-pig'},
    {'key': 'text/x-sql', 'tag': 'x-sql'},
    {'key': 'text/coffeescript', 'tag': 'coffeescript'},
    {'key': 'text/x-z80', 'tag': 'x-z80'},
    {'key': 'application/dart', 'tag': 'dart'},
    {'key': 'application/x-aspx', 'tag': 'x-aspx'},
    {'key': 'text/x-gas', 'tag': 'x-gas'},
    {'key': 'text/typescript', 'tag': 'typescript'},
    {'key': 'application/x-httpd-php', 'tag': 'x-httpd-php'},
    {'key': 'text/x-csrc', 'tag': 'x-csrc'},
    {'key': 'application/x-jsp', 'tag': 'x-jsp'},
    {'key': 'text/x-perl', 'tag': 'x-perl'},
    {'key': 'application/x-json', 'tag': 'x-json'},
    {'key': 'text/x-objectivec', 'tag': 'x-objectivec'},
    {'key': 'video/ogg', 'tag': 'ogg'},
    {'key': 'text/x-webidl', 'tag': 'x-webidl'},
    {'key': 'application/x-cypher-query', 'tag': 'x-cypher-query'},
    {'key': 'text/x-puppet', 'tag': 'x-puppet'},
    {'key': 'application/edn', 'tag': 'edn'},
    {'key': 'text/x-sas', 'tag': 'x-sas'},
    {'key': 'text/x-rst', 'tag': 'x-rst'},
    {'key': 'text/x-properties', 'tag': 'x-properties'},
    {'key': 'text/x-fortran', 'tag': 'x-fortran'},
    {'key': 'auth/forge-password', 'tag': 'forge-password'},
    {'key': 'text/x-verilog', 'tag': 'x-verilog'},
    {'key': 'text/x-ttcn-cfg', 'tag': 'x-ttcn-cfg'},
    {'key': 'text/x-lua', 'tag': 'x-lua'},
    {'key': 'text/x-cassandra', 'tag': 'x-cassandra'},
    {'key': 'text/x-sml', 'tag': 'x-sml'},
    {'key': 'text/x-brainfuck', 'tag': 'x-brainfuck'},
    {'key': 'application/pgp', 'tag': 'pgp'},
    {'key': 'text/x-d', 'tag': 'x-d'},
    {'key': 'text/x-gss', 'tag': 'x-gss'},
    {'key': 'text/x-oz', 'tag': 'x-oz'},
    {'key': 'text/x-diff', 'tag': 'x-diff'},
    {'key': 'application/javascript', 'tag': 'javascript'},
    {'key': 'text/x-fcl', 'tag': 'x-fcl'},
    {'key': 'text/x-sqlite', 'tag': 'x-sqlite'},
    {'key': 'text/x-ecl', 'tag': 'x-ecl'},
    {'key': 'text/x-scss', 'tag': 'x-scss'},
    {'key': 'text/jinja2', 'tag': 'jinja2'},
    {'key': 'application/sparql-query', 'tag': 'sparql-query'},
    {'key': 'text/x-julia', 'tag': 'x-julia'},
    {'key': 'text/x-dockerfile', 'tag': 'x-dockerfile'},
    {'key': 'text/x-mariadb', 'tag': 'x-mariadb'},
    {'key': 'text/yaml', 'tag': 'yaml'},
    {'key': 'text/x-forth', 'tag': 'x-forth'},
    {'key': 'text/x-stex', 'tag': 'x-stex'},
    {'key': 'text/x-coffeescript', 'tag': 'x-coffeescript'},
    {'key': 'text/x-vhdl', 'tag': 'x-vhdl'},
    {'key': 'text/x-kotlin', 'tag': 'x-kotlin'},
    {'key': 'text/x-java', 'tag': 'x-java'},
    {'key': 'text/x-haxe', 'tag': 'x-haxe'},
    {'key': 'text/x-rustsrc', 'tag': 'x-rustsrc'},
    {'key': 'application/x-slim', 'tag': 'x-slim'},
    {'key': 'text/x-spreadsheet', 'tag': 'x-spreadsheet'},
    {'key': 'text/x-jade', 'tag': 'x-jade'},
    {'key': 'text/x-pgsql', 'tag': 'x-pgsql'},
    {'key': 'text/x-rpm-changes', 'tag': 'x-rpm-changes'},
    {'key': 'text/x-feature', 'tag': 'x-feature'},
    {'key': 'audio/x-m4a', 'tag': 'x-m4a'},
    {'key': 'text/x-markdown', 'tag': 'x-markdown'},
    {'key': 'text/x-eiffel', 'tag': 'x-eiffel'},
    {'key': 'text/x-yacas', 'tag': 'x-yacas'},
    {'key': 'text/x-dylan', 'tag': 'x-dylan'},
    {'key': 'text/x-dart', 'tag': 'x-dart'},
    {'key': 'text/x-sh', 'tag': 'x-sh'},
    {'key': 'text/x-asterisk', 'tag': 'x-asterisk'},
    {'key': 'text/x-systemverilog', 'tag': 'x-systemverilog'},
    {'key': 'text/x-mumps', 'tag': 'x-mumps'},
    {'key': 'script/x-vue', 'tag': 'x-vue'},
    {'key': 'text/velocity', 'tag': 'velocity'},
    {'key': 'text/turtle', 'tag': 'turtle'},
    {'key': 'text/x-ruby', 'tag': 'x-ruby'},
    {'key': 'text/x-ttcn-asn', 'tag': 'x-ttcn-asn'},
    {'key': 'application/x-shockwave-flash', 'tag': 'x-shockwave-flash'},
    {'key': 'text/x-solr', 'tag': 'x-solr'},
    {'key': 'text/css', 'tag': 'css'},
    {'key': 'text/x-pascal', 'tag': 'x-pascal'},
    {'key': 'application/x-ejs', 'tag': 'x-ejs'},
    {'key': 'text/x-nesc', 'tag': 'x-nesc'},
    {'key': 'text/x-ocaml', 'tag': 'x-ocaml'},
    {'key': 'text/x-hxml', 'tag': 'x-hxml'},
    {'key': 'text/x-swift', 'tag': 'x-swift'},
    {'key': 'application/xml-dtd', 'tag': 'xml-dtd'},
    {'key': 'text/tiki', 'tag': 'tiki'},
    {'key': 'text/uri-list', 'tag': 'uri-list'},
    {'key': 'text/x-vb', 'tag': 'x-vb'},
    {'key': 'text/x-slim', 'tag': 'x-slim'},
    {'key': 'application/ecmascript', 'tag': 'ecmascript'},
    {'key': 'text/x-ceylon', 'tag': 'x-ceylon'},
    {'key': 'text/x-nsis', 'tag': 'x-nsis'},
    {'key': 'text/x-objectivec++', 'tag': 'x-objectivec++'},
    {'key': 'text/x-cython', 'tag': 'x-cython'},
    {'key': 'application/sieve', 'tag': 'sieve'},
    {'key': 'x-shader/x-vertex', 'tag': 'x-vertex'},
    {'key': 'text/x-c', 'tag': 'x-c'},
    {'key': 'text/x-crystal', 'tag': 'x-crystal'},
    {'key': 'text/x-ebnf', 'tag': 'x-ebnf'},
    {'key': 'text/x-q', 'tag': 'x-q'},
    {'key': 'application/n-quads', 'tag': 'n-quads'},
    {'key': 'text/x-msgenny', 'tag': 'x-msgenny'},
    {'key': 'application/pgp-signature', 'tag': 'pgp-signature'},
    {'key': 'text/x-scala', 'tag': 'x-scala'},
    {'key': 'application/vnd.coffeescript', 'tag': 'vnd.coffeescript'},
    {'key': 'video/webm', 'tag': 'webm'},
    {'key': 'text/ecmascript-d+$', 'tag': 'ecmascript-d+$'},
    {'key': 'text/x-sass', 'tag': 'x-sass'},
    {'key': 'text/x-handlebars-template', 'tag': 'x-handlebars-template'},
    {'key': 'text/x-scheme', 'tag': 'x-scheme'},
    {'key': 'text/x-yaml', 'tag': 'x-yaml'},
    {'key': 'text/x-mssql', 'tag': 'x-mssql'},
    {'key': 'text/x-tcl', 'tag': 'x-tcl'},
    {'key': 'application/pgp-keys', 'tag': 'pgp-keys'},
    {'key': 'application/x-sh', 'tag': 'x-sh'},
    {'key': 'application/typescript', 'tag': 'typescript'},
    {'key': 'text/x-rsrc', 'tag': 'x-rsrc'},
    {'key': 'text/x-ttcn', 'tag': 'x-ttcn'},
    {'key': 'text/x-mathematica', 'tag': 'x-mathematica'},
    {'key': 'text/rtf', 'tag': 'rtf'},
    {'key': 'text/x-mysql', 'tag': 'x-mysql'},
    {'key': 'text/x-clojurescript', 'tag': 'x-clojurescript'},
    {'key': 'text/x-stsrc', 'tag': 'x-stsrc'},
    {'key': 'text/n-triples', 'tag': 'n-triples'},
    {'key': 'text/x-haskell', 'tag': 'x-haskell'},
    {'key': 'text/x-less', 'tag': 'x-less'},
    {'key': 'text/ecmascript', 'tag': 'ecmascript'},
    {'key': 'text/x-mscgen', 'tag': 'x-mscgen'},
    {'key': 'auth/register', 'tag': 'register'},
    {'key': 'text/x-toml', 'tag': 'x-toml'},
    {'key': 'text/x-styl', 'tag': 'x-styl'},
    {'key': 'application/x-httpd-php-open', 'tag': 'x-httpd-php-open'},
    {'key': 'text/x-tornado', 'tag': 'x-tornado'},
    {'key': 'audio/mpeg', 'tag': 'mpeg'},
    {'key': 'text/x-soy', 'tag': 'x-soy'},
    {'key': 'text/x-factor', 'tag': 'x-factor'},
    {'key': 'text/x-common-lisp', 'tag': 'x-common-lisp'},
    {'key': 'text/x-c++src', 'tag': 'x-c++src'},
    {'key': 'text/x-plsql', 'tag': 'x-plsql'},
    # {"key":"html","tag":"html"},
]
contentTypeListPure=[x['key'] for x in contentTypeList]#用于过滤url


def urlFilter(lst):
    tmp = []
    for line in lst:
        # 匹配到的api接口如果有contentTypeListPure里的内容，则认为这个api接口是错误的
        if [x for x in contentTypeListPure if x in line]:
            continue
        # 匹配到的api接口如果以['\\', '$', '@', '*', '+', '-', '|', '!', '%', '^', '~', '[', ']']为开头，则认为这个api接口是错误的
        if any(line.strip("\"").strip("'").strip("/").startswith(x) for x in apiRootBlackListDuringSpider):
            continue
        line = line.replace(" ", "")
        line = line.replace("\\/", "/")
        line = line.replace("\"", "")
        line = line.replace("'", "")
        line = line.replace("href=\"", "", 1)
        line = line.replace("href='", "", 1)
        line = line.replace("%3A", ":")
        line = line.replace("%2F", "/")
        # 新增排除\\
        line = line.replace("\\\\", "")
        if line.endswith("\\"):
            line = line.rstrip("\\")
        if line.startswith("="):
            line = line.lstrip("=")
        if line.startswith("href="):
            line = line.lstrip("href=")
        if line == 'href':
            line = ""
        for x in urlblacklist:  #
            if x in line:  # 排除 aa.vue?a=1&b=3的情况
                line = ""
                break
        for x in urlextblacklist:
            # if line.endswith(x):
            if line.split("?")[0].endswith(x):  # 排除 aa.vue?a=1&b=3的情况
                line = ""
                break
        tmp.append(line)
    return tmp

def get_api_path(i, js_urls_queue, js_url, headers, all_api_paths, folder_path, ):
    try:
        # logger_print_content(f"{js_url}获取JS页面里的API接口")
        res = requests.get(url=js_url, headers=headers, timeout=TIMEOUT, verify=False, allow_redirects=False)
        logger_print_content(f"[线程{i}] 剩下:{js_urls_queue.qsize()} {js_url}获取JS页面里的API接口\t状态码:{res.status_code}")
        # 获取网页源代码
        text = res.text

        file_name = re.sub(r'[^a-zA-Z0-9\.]', '_', js_url)
        file_path = f'{folder_path}/js_response/JS_{file_name}.txt'
        save_response_to_file(file_path, text)

        # print(text)
        if res.status_code == 404:
            return
    except Exception as e:
        return

    # 获取url的相关元素
    parsed_url = urlparse(js_url)
    scheme = parsed_url.scheme
    path = parsed_url.path
    host = parsed_url.hostname
    port = parsed_url.port
    if port:
        host = host + ":" + str(port)

    # 正则匹配 删除掉最后的js路径名 例如：/static/js/elicons.626b260a.js 得到 /static/js/
    pattern = re.compile(r'/.*/{1}|/')
    root_result = pattern.findall(path)
    if root_result:
        root_path = root_result[0]
    else:
        root_path = "/"

    api_patterns = [
        r'["\']http[^\s\'’"\>\<\)\(]{2,250}?[\"\']',
        r'=http[^\s\'’"\>\<\)\(]{2,250}',
        r'[\"\']/[^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        # 排除汉字
        r'[\"\'][^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?/[^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?/[^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        # 排除汉字
        r'(?i)(?<=path:)\s?[\"\'][^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        r'(?i)(?<=path\s:)\s?[\"\'][^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        r'(?i)(?<=path=)\s?[\"\'][^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        r'(?i)(?<=path\s=)\s?[\"\'][^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        r'(?i)(?<=url:)\s?[\"\'][^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        r'(?i)(?<=url\s:)\s?[\"\'][^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        r'(?i)(?<=url=)\s?[\"\'][^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        r'(?i)(?<=url\s=)\s?[\"\'][^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        r'(?i)(?<=index:)\s?[\"\'][^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        r'(?i)(?<=index\s:)\s?[\"\'][^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        r'(?i)(?<=index=)\s?[\"\'][^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        r'(?i)(?<=index\s=)\s?[\"\'][^\s\'’"\>\<\:\)\(\u4e00-\u9fa5]{1,250}?["\']',
        r'(href|action).{0,3}=.{0,3}[\"\'][^\s\'’"\>\<\)\(]{2,250}',
        r'(href|action).{0,3}=.{0,3}[^\s\'’"\>\<\)\(]{2,250}',
        r'(?:"|\'|`)(\/[^"\'`<>]+)(?:"|\'|`)',
    ]

    new_api_urls = []
    new_api_paths = []
    all_api_paths_list = []
    for api_pattern in api_patterns:
        pattern = re.compile(api_pattern)
        api_result = pattern.findall(text)
        if not api_result:
            continue
        logger_print_content(f"{js_url}匹配出如下的api接口:{api_result}")
        api_result = [x.strip('\'" ').rstrip('/') for x in api_result]
        api_result = urlFilter(api_result)
        # logger_print_content(f"{js_url}整后得到如下的api接口:{api_result}")



        for _ in api_result:
            new_api_path = urlparse(_).path
            new_api_query = urlparse(_).query
            if new_api_query:
                new_api_path = f"{new_api_path}?{new_api_query}"

            if new_api_path == "" or any(ext in new_api_path.lower() for ext in staticFileExtBlackList):
                continue
            elif new_api_path in all_api_paths_list:
                logger_print_content(f"{new_api_path}已经在api接口列表里")
            else:
                logger_print_content(f"{new_api_path} 新的api接口")
                new_api_paths.append(new_api_path)
                all_api_paths_list.append(new_api_path)
                all_api_paths.append({'referer': js_url, 'api_path': new_api_path, 'url_type': "api_path"})

    if new_api_paths:
        logger_print_content(f"{js_url} 新增[{len(new_api_paths)}]个新的api接口\n")
        # all_api_paths.extend(new_api_paths)
        # all_api_paths_list = list(set(all_api_paths_list))
    else:
        logger_print_content(f"{js_url} 无新增api接口\n")

def apiPathFind(i, js_urls_queue, headers, all_api_paths, folder_path, ):
    while not js_urls_queue.empty():
        js_url = js_urls_queue.get()
        get_api_path(i, js_urls_queue, js_url, headers, all_api_paths, folder_path, )

def apiPathFind_api(js_urls, cookies, folder_path):
    logger_print_content(f"js_urls: {js_urls}")
    all_api_paths = []

    try:
        os.makedirs(f"{folder_path}/js_response/")
    except Exception as e:
        pass

    if cookies:
        headers['Cookie'] = cookies
    # 新的js url队列，用来做消息队列，把所有新的js url都跑完
    js_urls_queue = Queue(-1)
    for js_url in js_urls:
        # logger_print_content(f"js_url: {js_url}")
        js_urls_queue.put(js_url)

    threads = []
    for i in range(100):
        t = threading.Thread(target=apiPathFind, args=(i, js_urls_queue, headers, all_api_paths, folder_path, ))
        threads.append(t)
        t.start()
        time.sleep(0.2)

    for t in threads:
        t.join()

    return all_api_paths
