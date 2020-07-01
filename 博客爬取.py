import re
import os
try:
    import requests
except:
    os.system('pip install requests')
    import requests
    
try:
    import html2text as ht
except:
    os.system('pip install html2text')
    import html2text as ht

try:
    import pangu
except:
    os.system('pip install pangu')
    import pangu

try:
    from bs4 import BeautifulSoup
except:
    os.system('pip install beautifulsoup4')
    os.system('pip install lxml')
    from bs4 import BeautifulSoup

    
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
        blog_url = input('输入博客URL: ').strip()
        # blog_url = 'https://www.jianshu.com/p/215600b11413'
        # blog_url = 'https://blog.csdn.net/hellozpc/article/details/106861972'
        # blog_url = 'https://www.cnblogs.com/wanlei/p/10650325.html'
        #blog_url = 'https://segmentfault.com/a/1190000011105644'
        #blog_url = 'https://blog.51cto.com/yht1990/2503819'
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
        if rule['encoding'] is not None:
            r.encoding = 'utf-8'
        # 获取文本内容
        html = r.text

        soup = BeautifulSoup(html, 'lxml')
        if False:
        
            # 增加代码标签
            html = re.sub('<code.*?>', '<code>```\n', html)
            html = re.sub('</code>', '```\n</code>', html)
        with open('temp.html', 'w', encoding='utf-8') as f:
            f.write(html)

        
        # 正则获取标题
        title_pattern = rule['title_pattern']
        titles = re.findall(title_pattern, html, re.DOTALL)
        if len(titles) == 0:
            title = 'default'
        else:
            title = pangu.spacing_text(titles[0])
        blog.title = title
        print('标题:', title)

        if rule['content_type'] == 'bs':
            content = soup.select(rule['content_pattern']).pop()
            content = str(content)

        else:
            # 提取正文内容
            content_pattern = rule['content_pattern']
            contents = re.findall(content_pattern, html, re.DOTALL)
            if len(contents) == 0:
                content = ''
            else:
                content = contents[0]

        content = '<h1><a href="{}">{}</a></h1><br><br>'.format(blog.url, blog.title) + content
        for src, dst in rule['content_replaces']:
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
        #md_content = md_content.replace('\n', '\n\n')
        while '\n\n\n' in md_content:
            md_content = md_content.replace('\n\n\n', '\n\n')
        # print(' MD:', md_content)

        # 正则替换
        for src, dst in rule['md_replaces']:
            md_content = re.sub(src, dst, md_content)
        # 加空格
        md_content = pangu.spacing_text(md_content)

        # ** *
        for star_line in re.findall('\*(.*?)\*', md_content):
            md_content = md_content.replace('{}'.format(star_line), '{}'.format(star_line.strip()))
        # 异常断行
        md_content = re.sub('-\n', '-', md_content)

        # 规范代码标签
        #md_content = re.sub('[ ]```', '```', md_content)
        

        # 过滤非法字符
        title = re.sub('[\/:*?"<>|]', '-', title)
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
while True:
    blogCrawler.run()

