import os
import re
import pangu
import requests
import shutil

from bs4 import BeautifulSoup
from markdownify import markdownify

from formatter import markdown

HEADERS = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
                  Chrome/67.0.3396.56 Safari/537.36',
}


class Blog:
    def __init__(self):
        self.title = ''
        self.url = ''
        self.html = ''
        self.content = ''
        self.markdown_content = ''


class BlogCrawler:
    def __init__(self, blog_dir_path, temp_dir_path, website_cfg_dir_path, main_cfg_file_path, replace_dict_file_path):
        self.blog_dir_path = blog_dir_path
        self.temp_dir_path = temp_dir_path
        self.website_cfg_dir_path = website_cfg_dir_path
        self.main_cfg_file_path = main_cfg_file_path
        self.replace_dict_file_path = replace_dict_file_path

        self.website_rules_dict = {}
        self.tag_names = []
        self.link_names = []
        self.load_config()
        self.replace_dict = eval(open(replace_dict_file_path, encoding='utf-8').read())

    def run(self, blog_url):
        blog_url_host = self.get_host_from_url(blog_url)
        blog = Blog()
        blog.url = blog_url
        blog.host = blog_url_host

        website_rule_dict = self.get_website_rule_dict_by_host(blog_url_host)
        if website_rule_dict is not None:
            self.download_blog(blog, website_rule_dict)
        else:
            print("未支持网站: " + blog.host)
        print()

    def get_website_rule_dict_by_host(self, blog_url_host):
        """
        获取网站爬取规则
        """
        if blog_url_host in self.website_rules_dict.keys():
            return self.website_rules_dict[blog_url_host]

        for host in self.website_rules_dict.keys():
            if host in blog_url_host:
                return self.website_rules_dict[host]
        return None

    def load_config(self):
        config_names = os.listdir(self.website_cfg_dir_path)
        for config_name in config_names:
            config_file_path = os.path.join(self.website_cfg_dir_path, config_name)
            config_dict = eval(open(config_file_path, 'r', encoding='utf-8').read())
            self.website_rules_dict[config_dict['host']] = config_dict

        config_dict = eval(open(self.main_cfg_file_path, 'r', encoding='utf-8').read())
        self.tag_names = config_dict["tag_names"]
        self.link_names = config_dict["link_names"]

    def download_blog(self, blog, website_rule_dict):
        session = requests.session()
        rep = session.get(blog.url, headers=HEADERS)
        rep.encoding = self.get_html_encoding(rep.text)
        html = rep.text
        soup = BeautifulSoup(html, 'lxml')

        temp_html_file_path = os.path.join(self.temp_dir_path, "blog.html")
        with open(temp_html_file_path, 'w', encoding='utf-8') as f:
            f.write(html)

        # 获取标题
        blog_title = self.get_title_of_blog(soup, blog, website_rule_dict)

        # 获取正文内容
        blog_content = self.get_content_of_blog(soup, website_rule_dict)

        with open(os.path.join(self.temp_dir_path, 'blog_content.html'), 'w', encoding='utf-8') as f:
            f.write(blog_content)

        # 转换前，替换文本
        blog_content = self.replace_words_before_markdownify(blog, blog_content, website_rule_dict)

        # 转换为 markdown
        markdown_content = markdownify(blog_content, heading_style="ATX")
        with open(os.path.join(self.temp_dir_path, 'blog_markdown.md'), 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        # 转换前，替换文本
        markdown_content = self.replace_words_after_markdownify(markdown_content, website_rule_dict)

        # 格式化
        markdown_content = markdown.format_markdown(markdown_content)

        # 替换
        for old_val, new_val in self.replace_dict.items():
            markdown_content = markdown_content.replace(old_val, new_val)

        # 添加头部信息
        markdown_content = self.add_headers(blog_title, blog.url, markdown_content)
        markdown_content = re.sub('[\n]+\n\n', '\n\n', markdown_content)
        blog_file_path = os.path.join(self.blog_dir_path, "{}.md".format(self.get_blog_name(blog_title)))
        with open(blog_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

    def get_title_of_blog(self, soup, blog, website_rule_dict):
        title_bs_args = website_rule_dict['title_bs_args']
        titles = []
        try:
            titles = self.get_content_by_bs_args(soup, title_bs_args, 'title')
        except:
            print('\n错误提示：标题提取失败')
            print('\n标题参数: ' + str(title_bs_args))

        if len(titles) == 0:
            blog_title = 'default'
        else:
            blog_title = pangu.spacing_text(titles)
        blog.title = blog_title
        print('博客标题:', blog_title)
        return blog_title

    def get_content_of_blog(self, soup, website_rule_dict):
        content_bs_args = website_rule_dict['content_bs_args']
        blog_content = self.get_content_by_bs_args(soup, content_bs_args)
        if blog_content == 'None':
            print('\n错误提示：内容提取失败')
            print('内容参数: ' + str(content_bs_args))
            return ''
        return blog_content

    def add_headers(self, blog_title, blog_url, markdown_content):
        header_format = '# [{}]({})\n\n> 标签： {}\n>\n> 双链： {}\n\n{}'
        tag_content = ' '.join(['#{}'.format(name) for name in self.tag_names if name in markdown_content])
        link_content = ' '.join(['[[{}]]'.format(name) for name in self.link_names if name in markdown_content])
        markdown_content = header_format.format(blog_title, blog_url, tag_content, link_content, markdown_content)
        return markdown_content

    def cleanup(self):
        """
        Do some cleanup stuff before exiting the BlogCrawler.
        :return: None
        """
        for root, dirs, files in os.walk(self.temp_dir_path):
            for file in files:
                if file != '.gitkeep':
                    os.unlink(os.path.join(root, file))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

    @staticmethod
    def get_blog_name(blog_title):
        blog_name = blog_title.strip('\n').strip('\n').strip(' ').strip(' ').strip('\t')
        return re.sub(r"[\/\\\:\*\?\"\<\>\|]", '_', blog_name)

    @staticmethod
    def replace_words_before_markdownify(blog, blog_content, website_rule_dict):
        for src, dst in website_rule_dict['html_replaces']:
            blog_content = re.sub(src, dst, blog_content)
        blog.content = blog_content
        return blog_content

    @staticmethod
    def replace_words_after_markdownify(markdown_content, website_rule_dict):
        for src, dst in website_rule_dict['markdown_replaces']:
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
