import re
import os

try:
    import requests
except:
    os.system('pip install requests')
    import requests

try:
    from markdownify import markdownify
except:
    os.system('pip install markdownify')
    from markdownify import markdownify

try:
    import pangu
except:
    os.system('pip install pangu')
    import pangu

try:
    import lxml
except:
    os.system('pip install lxml')
    import lxml

try:
    from bs4 import BeautifulSoup
except:
    os.system('pip install BeautifulSoup4')
    from bs4 import BeautifulSoup

headers = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.56 Safari/537.36',
}

soup = None


class Blog:
    def __init__(self):
        self.title = ''
        self.author = ''
        self.url = ''
        self.html = ''
        self.content = ''
        self.markdown_content = ''
        self.zip = ''


class MarkdownFormatter:
    def format(self, markdown_content):
        # 中英文加空格
        markdown_content = pangu.spacing_text(markdown_content)
        markdown_content = markdown_content.replace('\r', '')

        # 修复 pangu 带来的md格式错误
        markdown_content = self.fix_markdown_file_bold_format(markdown_content)

        # 修复断行
        markdown_content = self.fix_markdown_file_wrong_line_break(markdown_content)

        # 修复代码方法 () 前的多余空格
        markdown_content = self.fix_markdown_file_wrong_spacing(markdown_content)

        # 移除空白行
        markdown_content = self.remove_blank_line(markdown_content)

        # 修复 {} 及 ```中文``` 问题
        markdown_content = self.fix_code_format(markdown_content)

        # 移除 >
        markdown_content = self.remove_invalid_ref(markdown_content)

        # 移除图片描述
        markdown_content = self.remove_image_desc(markdown_content)

        # 移除空白行
        markdown_content = self.remove_blank_line(markdown_content)

        return markdown_content

    @staticmethod
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

    @staticmethod
    def get_code_language(code_content):
        return 'java'

    @staticmethod
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
            code_language = MarkdownFormatter.get_code_language(code_content_new)
            code_content_new = '```' + code_language + code_content_new[3::]
            markdown_content = markdown_content.replace(code_content, code_content_new)
        return markdown_content

    @staticmethod
    def fix_markdown_file_wrong_spacing(markdown_content):
        words = re.findall('(\w+) \(', markdown_content)
        for word in words:
            markdown_content = markdown_content.replace('{} ('.format(word), '{}('.format(word))
        else:
            return markdown_content

    @staticmethod
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

    @staticmethod
    def fix_markdown_file_bold_format(text):
        question_regex = ['\*\* (.*?) \*\*', '\* (.*?) \*']
        fixed_template = ['**{}**', '*{}*']
        assert (len(question_regex) == len(fixed_template))
        for index in range(len(fixed_template)):
            match_list = re.finditer(question_regex[index], text)
            for m in match_list:
                text = text.replace(m.group(), fixed_template[index].format(m.group(1)))
        return text

    @staticmethod
    def remove_invalid_ref(text):
        result = text[::]
        while '\n\n>\n' in result:
            result = result.replace('\n\n>\n', '\n\n')
        while '\n>\n' in result:
            result = result.replace('\n>\n', '\n')
        return result

    @staticmethod
    def remove_image_desc(text):
        result = text[::]
        desc_list = re.findall('!\[(.*?)\]\(.*?\)', result)
        for desc in desc_list:
            result = result.replace('![{}]('.format(desc), '![](')

        link_list = re.findall('!\[\]\((.*?)\)', result)
        for link in link_list:
            result = result.replace('![]({})'.format(link), '\n![]({})\n'.format(link))
        return result


class BlogCrawler:
    def __init__(self):
        self.rule_dict = {}
        self.tag_names = []
        self.link_names = []
        self.formatter = MarkdownFormatter()
        dirs = ['config', 'blogs']
        for dir_name in dirs:
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)

        self.load_config()

    def run(self):
        blog_url = input('博客网址: ').strip()

        blog_url_host = self.get_host_from_url(blog_url)
        blog = Blog()
        blog.url = blog_url
        blog.host = blog_url_host
        if blog.host not in self.rule_dict.keys():
            print("未支持网站: " + blog.host)
            return
        self.download_blog(blog, self.rule_dict[blog.host])
        print()

    def load_config(self):
        config_path = 'config'
        config_filenames = os.listdir(config_path)
        for config_filename in config_filenames:
            config_name = config_filename[:-5:]
            self.rule_dict[config_name] = eval(
                open(config_path + os.sep + config_filename, 'r', encoding='utf-8').read())

        config_dict = eval(open("config.json", 'r', encoding='utf-8').read())
        self.tag_names = config_dict["tag_names"]
        self.link_names = config_dict["link_names"]

    def download_blog(self, blog, rule_dict):
        s = requests.session()
        r = s.get(blog.url, headers=headers)
        r.encoding = self.get_html_encoding(r.text)
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        # with open('temp.html', 'w', encoding='utf-8') as f:
        #     f.write(html)

        # 获取标题
        blog_title = self.get_title_of_blog(soup, blog, rule_dict)

        # 获取正文内容
        blog_content = self.get_content_of_blog(soup, blog, rule_dict)

        with open('blog_content.html', 'w', encoding='utf-8') as f:
            f.write(blog_content)

        # 转换前，替换文本
        blog_content = self.replace_words_before_markdownify(blog, blog_content, rule_dict)

        # 转换为 markdown
        markdown_content = markdownify(blog_content, heading_style="ATX")

        with open('markdown_content.md', 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        # 转换前，替换文本
        markdown_content = self.replace_words_after_markdownify(markdown_content, rule_dict)

        # 格式化
        markdown_content = self.formatter.format(markdown_content)

        # 添加头部信息
        markdown_content = self.add_headers(blog_title, blog.url, markdown_content)

        blog_name = self.get_blog_name(blog_title)
        with open("blogs/{}.md".format(blog_name), 'w', encoding='utf-8') as f:
            f.write(markdown_content)

    def get_title_of_blog(self, soup, blog, rule_dict):
        title_bs_args = rule_dict['title_bs_args']
        titles = self.get_content_by_bs_args(soup, title_bs_args, 'title')

        if len(titles) == 0:
            blog_title = 'default'
        else:
            blog_title = pangu.spacing_text(titles)
        blog.title = blog_title
        print('博客标题:', blog_title)
        return blog_title

    def get_content_of_blog(self, soup, blog, rule_dict):
        content_bs_args = rule_dict['content_bs_args']
        blog_content = self.get_content_by_bs_args(soup, content_bs_args)
        return blog_content

    def add_headers(self, blog_title, blog_url, markdown_content):
        header_format = '# [{}]({})\n\n> 标签： {}\n> 双链： {}\n\n{}'
        tag_content = ' '.join(['#{}'.format(name) for name in self.tag_names if name in markdown_content])
        link_content = ' '.join(['[[{}]]'.format(name) for name in self.link_names if name in markdown_content])
        markdown_content = header_format.format(blog_title, blog_url, tag_content, link_content, markdown_content)
        return markdown_content

    @staticmethod
    def get_blog_name(blog_title):
        blog_name = blog_title[::]
        replace_words = (
            ('\n', ''),
            ('*', '_'),
            ('/', '_'),
            (':', '：'),
        )
        for src, dst in replace_words:
            blog_name = blog_name.replace(src, dst)
        return blog_name

    @staticmethod
    def replace_words_before_markdownify(blog, blog_content, rule_dict):
        for src, dst in rule_dict['content_replaces']:
            blog_content = re.sub(src, dst, blog_content)
        blog.content = blog_content
        return blog_content

    @staticmethod
    def replace_words_after_markdownify(markdown_content, rule_dict):
        for src, dst in rule_dict['md_replaces']:
            markdown_content = re.sub(src, dst, markdown_content)
        return markdown_content

    @staticmethod
    def get_host_from_url(url):
        hosts = re.findall("://(.*?)/", url)
        if len(hosts) == 0:
            return None
        else:
            return hosts[0]

    @staticmethod
    def get_content_by_bs_args(soup, bs_args_list, type="content"):
        for bs_args in bs_args_list:
            soup = soup.find(bs_args['name'], attrs=bs_args['attrs'])
        if not type == "content":
            return soup.get_text()
        else:
            return str(soup)

    @staticmethod
    def get_html_encoding(html):
        charset = re.findall('''<meta.*?char[sS]et=["']?(.*?)[";' ]''', html)[0]
        return charset


is_test = False

if not is_test:
    while True:
        blogCrawler = BlogCrawler()
        blogCrawler.run()
else:
    formatter = MarkdownFormatter()
    markdown_content = open('markdown_content.md', encoding='utf-8').read()
    markdown_content_formatted = formatter.format(markdown_content)
    print(markdown_content_formatted)
    with open('markdown_content_formatted.md', encoding='utf-8', mode='w') as f:
        f.write(markdown_content_formatted)
