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
    os.system('pip install BeautifulSoup4')
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
        # blog_url = 'https://segmentfault.com/a/1190000011105644'
        # blog_url = 'https://blog.51cto.com/yht1990/2503819'
        
        blog_url = 'https://zhuanlan.zhihu.com/p/28375308'
        # blog_url = 'https://mp.weixin.qq.com/s/-zKO0TZPqhCB6nyuUyADUw'
        # blog_url = 'https://www.jb51.net/article/174387.htm'
        # blog_url = 'https://juejin.im/post/5ef7328cf265da22a8513da2'
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
        encoding_type = self.get_html_chatset(r.text)
        # 设置编码格式
        r.encoding = encoding_type
        print('编码格式:', r.encoding)
        # 获取文本内容
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        if False:
            # 增加代码标签
            html = re.sub('<code.*?>', '<code>```\n', html)
            html = re.sub('</code>', '\n```</code>', html)
        with open('temp.html', 'w', encoding='utf-8') as f:
            f.write(html)
            
        # 正则获取标题
        title_bs_args = rule['title_bs_args']
        titles = self.get_content_by_bs_args(soup, title_bs_args, 'title')

        if len(titles) == 0:
            title = 'default'
        else:
            title = pangu.spacing_text(titles)
        blog.title = title
        print('标题:', title)

        # 提取正文内容
        content_bs_args = rule['content_bs_args']
        content = self.get_content_by_bs_args(soup, content_bs_args)
        
        content = '<h1><a href="{}">{}</a></h1><br><br>'.format(blog.url, blog.title) + content
        for src, dst in rule['content_replaces']:
            content = re.sub(src, dst, content)
        blog.content = content
        # print('正文:', content)

        # 转换为 MD
        # md_content = Tomd(content).markdown
        # content = re.sub('<a id=".*?"></a>', '', content)
        # code_tag_replace_text = 'magic&%sd我他喵真帅sf*codestart*-sdfa*'
        # content = content.replace('<code>', code_tag_replace_text).replace('</code>', code_tag_replace_text)
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
        # 修复pangu带来的md格式错误
        md_content = self.fix_mdfile_bold_format(md_content)
        # 修复不严格的代码片段
        md_content = self.fix_mdfile_code_format(md_content)
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

    @staticmethod
    def get_content_by_bs_args(soup, bs_args_list, type="content"):
        for bs_args in bs_args_list:
            soup = soup.find(bs_args['name'], attrs = bs_args['attrs'])
        if not type == "content":
            return soup.get_text()
        else:
            return str(soup)
            
    @staticmethod
    def get_html_chatset(html):
        charset = 'utf-8'
        charset = re.findall('''<meta.*?char[sS]et=["']?(.*?)[";' ]''', html)[0]
        return charset

    @staticmethod
    def fix_mdfile_bold_format(text):
        question_regex = ['\*\* (.*?) \*\*', '\* (.*?) \*']
        fixed_template = ['**{}**', '*{}*']
        assert(len(question_regex) == len(fixed_template))
        for index in range(len(fixed_template)):
            match_list = re.finditer(question_regex[index], text)
            for m in match_list:
                text = text.replace(m.group(), fixed_template[index].format(m.group(1)))
        return text
    @staticmethod
    def fix_mdfile_code_format(text):
        lines = text.split('\n')
        code_start_line_count = -1
        code_end_line_count = -1
        cur_lines_count = 0
        while cur_lines_count < len(lines):
            if code_start_line_count == -1:
                if lines[cur_lines_count] == '' and cur_lines_count < len(lines) - 1 and lines[cur_lines_count + 1][0:4] == '    ':
                    # 代码开始
                    code_start_line_count = cur_lines_count
                cur_lines_count += 1
            else:
                # 代码已经开始了
                if lines[cur_lines_count][0:4] == '    ':
                    if cur_lines_count < len(lines) - 2 and lines[cur_lines_count + 1] == '' and not lines[cur_lines_count + 2][0:4] == '    ':
                        # 代码结束的标志1
                        code_end_line_count = cur_lines_count + 1
                        # 这里+1 与 下边的+1不冲突
                        cur_lines_count += 1
                        
                        lines[code_start_line_count] = '```'
                        lines[code_end_line_count] = '```'
                        for i in range(code_start_line_count + 1, code_end_line_count):
                            lines[i] = lines[i][4::]
                        code_start_line_count = -1
                        code_end_line_count = -1
                    elif cur_lines_count == len(lines) - 1 and lines[cur_lines_count + 1] == '':
                        # 代码结束的标志1
                        code_end_line_count = cur_lines_count + 1
                        lines[code_start_line_count] = '```'
                        lines[code_end_line_count] = '```'
                        code_start_line_count = -1
                        code_end_line_count = -1
                    cur_lines_count += 1
                else:
                    cur_lines_count += 1
        lines_concat = ''
        for line in lines:
            lines_concat += '{}\n'.format(line)
        return lines_concat
        
blogCrawler = BlogCrawler()
blogCrawler.run()