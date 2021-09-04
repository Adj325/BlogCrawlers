import re
import pangu


def format(markdown_content):
    # 中英文加空格
    markdown_content = pangu.spacing_text(markdown_content)
    markdown_content = markdown_content.replace('\r', '')

    # 修复 pangu 带来的md格式错误
    markdown_content = fix_markdown_file_bold_format(markdown_content)

    # 修复断行
    markdown_content = fix_markdown_file_wrong_line_break(markdown_content)

    # 修复代码方法 () 前的多余空格
    markdown_content = fix_markdown_file_wrong_spacing(markdown_content)

    # 移除空白行
    markdown_content = remove_blank_line(markdown_content)

    # 修复 {} 及 ```中文``` 问题
    markdown_content = fix_code_format(markdown_content)

    # 移除 >
    markdown_content = remove_invalid_ref(markdown_content)

    # 移除图片描述
    markdown_content = remove_image_desc(markdown_content)

    # 移除空白行
    markdown_content = remove_blank_line(markdown_content)

    return markdown_content


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
    question_regex = ['\*\* (.*?) \*\*', '\* (.*?) \*']
    fixed_template = ['**{}**', '*{}*']
    assert (len(question_regex) == len(fixed_template))
    for index in range(len(fixed_template)):
        match_list = re.finditer(question_regex[index], text)
        for m in match_list:
            text = text.replace(m.group(), fixed_template[index].format(m.group(1)))
    return text


def remove_invalid_ref(text):
    result = text[::]
    while '\n\n>\n' in result:
        result = result.replace('\n\n>\n', '\n\n')
    while '\n>\n' in result:
        result = result.replace('\n>\n', '\n')
    return result


def remove_image_desc(text):
    result = text[::]
    desc_list = re.findall('!\[(.*?)\]\(.*?\)', result)
    for desc in desc_list:
        result = result.replace('![{}]('.format(desc), '![](')

    link_list = re.findall('!\[\]\((.*?)\)', result)
    for link in link_list:
        result = result.replace('![]({})'.format(link), '\n![]({})\n'.format(link))
    return result
