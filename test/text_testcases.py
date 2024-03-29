import os
import unittest

from crawler.blog import BlogCrawler

CURRENT_PATH = 'D:\@BlogCrawlers'

BLOG_DIR_PATH = os.path.join(CURRENT_PATH, '.temp')
TEMP_DIR_PATH = os.path.join(CURRENT_PATH, '.temp')

CONFIG_DIR_PATH = os.path.join(CURRENT_PATH, 'config')
WEBSITE_CONFIG_DIR_PATH = os.path.join(CONFIG_DIR_PATH, 'website')
MAIN_CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, 'main.json')

for dir_name in [TEMP_DIR_PATH, BLOG_DIR_PATH, CONFIG_DIR_PATH, WEBSITE_CONFIG_DIR_PATH]:
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

blogCrawler = BlogCrawler(BLOG_DIR_PATH, TEMP_DIR_PATH, WEBSITE_CONFIG_DIR_PATH, MAIN_CONFIG_FILE_PATH)


class MyTestCase(unittest.TestCase):
    def test_crawl_weixin(self):
        blogCrawler.run("https://mp.weixin.qq.com/s?__biz=Mzg3NjU3NTkwMQ==&mid=2247521569&idx=1&sn=99ad369c36f6ef0ad5b95a90ea492171&scene=21#wechat_redirect")


if __name__ == '__main__':
    unittest.main()
