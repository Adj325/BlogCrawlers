import os
import signal
import sys

from crawler.blog import BlogCrawler

CURRENT_PATH = os.getcwd()

BLOG_DIR_PATH = os.path.join(CURRENT_PATH, 'blogs')
TEMP_DIR_PATH = os.path.join(CURRENT_PATH, '.temp')

CONFIG_DIR_PATH = os.path.join(CURRENT_PATH, 'config')
WEBSITE_CONFIG_DIR_PATH = os.path.join(CONFIG_DIR_PATH, 'website')
MAIN_CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, 'main.json')
REPLACE_DICT_FILE_PATH = os.path.join(CONFIG_DIR_PATH, 'replace_dict.json')

for dir_name in [TEMP_DIR_PATH, BLOG_DIR_PATH, CONFIG_DIR_PATH, WEBSITE_CONFIG_DIR_PATH]:
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

blogCrawler = BlogCrawler(BLOG_DIR_PATH, TEMP_DIR_PATH, WEBSITE_CONFIG_DIR_PATH, MAIN_CONFIG_FILE_PATH, REPLACE_DICT_FILE_PATH)

exit_handler = lambda signum, frame : (blogCrawler.cleanup(), sys.exit(0))
signal.signal(signal.SIGINT, exit_handler)
signal.signal(signal.SIGTERM, exit_handler)

if __name__ == '__main__':
    while True:
        try:
            blog_url = input('博客网址: ').strip()
            blogCrawler.run(blog_url)
        except KeyboardInterrupt:
            blogCrawler.cleanup()
