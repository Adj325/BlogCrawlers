import re
import pangu


def format_markdown(markdown_content):
    # 移除 \r
    markdown_content = markdown_content.replace('\r', '')

    # 去除带来的 markdownify 下划线转义
    markdown_content = remove_underline_from_markdownify(markdown_content)

    # 中英文加空格
    markdown_content = pangu.spacing_text(markdown_content)

    # 修复 pangu 带来的md格式错误
    markdown_content = fix_markdown_file_bold_format(markdown_content)

    # 删除行末空格
    markdown_content = remove_space_of_line_end(markdown_content)

    # 修复断行
    markdown_content = fix_markdown_file_wrong_line_break(markdown_content)

    # 修复代码方法 () 前的多余空格
    markdown_content = fix_markdown_file_wrong_spacing(markdown_content)

    # 移除空白行
    markdown_content = remove_blank_line(markdown_content)

    # 修复 {} 及 ```中文``` 问题
    markdown_content = fix_code_format(markdown_content)

    # 优化引用文本
    markdown_content = perf_reference(markdown_content)

    # 图片内容优化
    markdown_content = perf_image_content(markdown_content)

    # 移除空白行
    markdown_content = remove_blank_line(markdown_content)

    return markdown_content


def remove_underline_from_markdownify(markdown_content):
    """
    1. 去除带来的 markdownify 下划线转义
    """
    return markdown_content.replace("\_", "_")


def remove_blank_line(markdown_content):
    """
     input: \n\n\n
    output: \n\n
    """
    markdown_content = re.sub('\n[  ]+\n', '\n\n', markdown_content)
    markdown_content = re.sub('[ ]+\n', '\n', markdown_content)
    markdown_content = re.sub('[\t]+\n', '\n', markdown_content)
    while '\n\n\n' in markdown_content:
        markdown_content = markdown_content.replace('\n\n\n', '\n\n')
    return markdown_content


def remove_space_of_line_end(text):
    text = text.replace(' ', ' ')
    return re.sub('[ ]+$', '', text)


def get_code_language(code_content):
    return 'java'


def fix_code_format(markdown_content):
    """
     input: {System.out\n}
    output: {\nSystem.out\n}

     input: ```中文```
    output: \n```\n中文\n```\n
    """
    markdown_content = markdown_content.replace('{', '{\n')
    markdown_content = markdown_content.replace('}', '\n}')
    markdown_content = re.sub('{[ \n\t]+}', '{}', markdown_content)
    markdown_content = re.sub('\n[  \t]+\n', '\n\n', markdown_content)

    while '{\n\n' in markdown_content:
        markdown_content = markdown_content.replace('{\n\n', '{\n')
    while '\n\n}' in markdown_content:
        markdown_content = markdown_content.replace('\n\n}', '\n}')

    markdown_content = markdown_content.replace('```', '\n\n```\n\n')
    code_content_list = re.findall("(```.*?```)", markdown_content, re.DOTALL)
    for code_content in code_content_list:
        code_content_new = code_content[::]
        while '```\n\n' in code_content_new:
            code_content_new = code_content_new.replace('```\n\n', '```\n')
        while '\n\n```' in code_content_new:
            code_content_new = code_content_new.replace('\n\n```', '\n```')
        code_language = get_code_language(code_content_new)
        code_content_new = '```' + code_language + code_content_new[3::]
        markdown_content = markdown_content.replace(code_content, code_content_new)
    return markdown_content


def fix_markdown_file_wrong_spacing(markdown_content):
    words = re.findall('(\w+) \(', markdown_content)
    for word in words:
        markdown_content = markdown_content.replace('{} ('.format(word), '{}('.format(word))
    else:
        return markdown_content


def fix_markdown_file_wrong_line_break(markdown_content):
    links = re.findall('\[.*?\n.*?\]\(.*?://.*?\)', markdown_content)
    for link in links:
        lin = link.split('\n')
        for li in lin:
            if 'http' in li:
                continue
            else:
                markdown_content = markdown_content.replace(link.strip(), link.strip().replace('\n', ''))

    # 连接含有 - 会断行
    urls = re.findall('://(.*?)-', markdown_content)
    for url in urls:
        markdown_content = markdown_content.replace(url + '-\n', url + '-')
    else:
        return markdown_content


def fix_markdown_file_bold_format(text):
    """
    去除 ** 或 * 的空格
    """
    question_regex = ['\*\*(.*?)\*\*', '\*(.*?)\*']
    fixed_template = ['**{}**', '*{}*']
    assert (len(question_regex) == len(fixed_template))
    for index in range(len(fixed_template)):
        match_list = re.finditer(question_regex[index], text)
        for m in match_list:
            print(m.group())
            src_text = m.group()
            dst_text = fixed_template[index].format(m.group(1).strip())
            text = text.replace(src_text, dst_text)
    return text


def perf_reference(text):
    result = text[::]
    # 去除前方多余换行
    while '\n\n>\n' in result:
        result = result.replace('\n\n>\n', '\n\n', result)
    # 去除中间无效引用
    result = re.sub('\n>\n>\n', '>\n', result)
    while '\n>\n' in result:
        result = result.replace('\n>\n', '\n')
    return result


def perf_image_content(text):
    """
    1. 去除图片描述
    2. 图片前后强制换行
    """
    result = text[::]
    desc_list = re.findall('!\[(.*?)\]\(.*?\)', result)
    for desc in desc_list:
        result = result.replace('![{}]('.format(desc), '![](')

    link_list = re.findall('!\[\]\((.*?)\)', result)
    for link in link_list:
        result = result.replace('![]({})'.format(link), '\n\n![]({})\n\n'.format(link))
    result = re.sub("[\n]+\n\n", "\n\n", result)
    # 解决 "![]() 段落内容" 强制换行后出现的行前有空格问题
    blank_lines = re.findall("\n (\S+)", result)
    for blank_line in blank_lines:
        result = result.replace(' ' + blank_line, blank_line)
    return result
