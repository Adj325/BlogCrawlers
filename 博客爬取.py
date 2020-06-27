import re
import os
import requests

import html2text as ht

headers = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.56 Safari/537.36',
}


class Blog:
    def __init__(self):
        self.title = ''
        self.author = ''
        self.url = ''
        self.html = ''
        self.content = ''
        self.md_content = ''
        self.zip = ''


class BlogCrawler:
    def __init__(self):
        self.rules = {}
        dirs = ['config', 'blogs']
        for dir_name in dirs:
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)

        self.load_config()

    def run(self):
        # blog_url = input('输入博客URL: ').trim()
        # blog_url = 'https://www.jianshu.com/p/215600b11413'
        # blog_url = 'https://blog.csdn.net/hellozpc/article/details/106861972'
        # blog_url = 'https://www.cnblogs.com/wanlei/p/10650325.html'
        blog_url = 'https://segmentfault.com/a/1190000011105644'
        blog_url_host = self.get_host_from_url(blog_url)
        print('网站:', blog_url_host)
        blog = Blog()
        blog.url = blog_url
        blog.host = blog_url_host
        if blog.host not in self.rules.keys():
            print("未支持网站: " + blog.host)
            return
        self.get_html_from_blog(blog, self.rules[blog.host])

    def get_html_from_blog(self, blog, rule):
        s = requests.session()
        r = s.get(blog.url, headers=headers)
        # 获取文本内容
        html = r.text
        if False:
            # 增加代码标签
            html = re.sub('<code.*?>', '<code>```\n', html)
            html = re.sub('</code>', '\n```</code>', html)
        with open('temp.html', 'w', encoding='utf-8') as f:
            f.write(html)
            
        # 正则获取标题
        title_pattern = rule['title_pattern']
        titles = re.findall(title_pattern, html, re.DOTALL)
        if len(titles) == 0:
            title = ''
        else:
            title = titles[0]
        blog.title = title
        print('标题:', title)

        # 提取正文内容
        content_pattern = rule['content_pattern']
        contents = re.findall(content_pattern, html, re.DOTALL)
        if len(contents) == 0:
            content = ''
        else:
            content = contents[0]
            content = '<h1><a href="{}">{}</a></h1><br><br>'.format(blog.url, blog.title) + content
            for src, dst in rule['content_replaces']:
                print(src, dst)
                print(src in content)
                content = re.sub(src, dst, content)
        blog.content = content
        # print('正文:', content)

        # 转换为 MD
        # md_content = Tomd(content).markdown
        # content = re.sub('<a id=".*?"></a>', '', content)
        text_maker = ht.HTML2Text()
        md_content = text_maker.handle(content)
        # 去空行
        md_content = md_content.replace('\r', '')
        while ' \n' in md_content:
            md_content = md_content.replace(' \n', '\n')
        while '\n\n\n' in md_content:
            md_content = md_content.replace('\n\n\n', '\n\n')
        # print(' MD:', md_content)

        for src, dst in rule['md_replaces']:
            md_content = re.sub(src, dst, md_content)
        with open("blogs" + os.sep + title + '.md', 'w', encoding='utf-8') as f:
            f.write(md_content)
        pass

    def load_config(self):
        config_path = 'config'
        config_filenames = os.listdir(config_path)
        for config_filename in config_filenames:
            config_name = config_filename[:-5:]
            self.rules[config_name] = eval(
                open(config_path + os.sep + config_filename, 'r', encoding='utf-8').read())

    @staticmethod
    def get_host_from_url(url):
        hosts = re.findall("://(.*?)/", url)
        if len(hosts) == 0:
            return None
        else:
            return hosts[0]


blogCrawler = BlogCrawler()
blogCrawler.run()
# https://blog.csdn.net/hellozpc/article/details/81436980
