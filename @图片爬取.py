import os
import re
import sys
import time
import traceback

try:
    import requests
except:
    os.system('pip install requests')
    import requests

try:
    from PIL import Image
except:
    os.system('pip install pillow')
    from PIL import Image
    
headers = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.56 Safari/537.36'
}


def webp2png(src, dst):
    im = Image.open(src)
    if im.mode == "RGBA":
        im.load()
        background = Image.new("RGB", im.size, (255, 255, 255))
        background.paste(im, mask=im.split()[3])
        im = background
        im.save(dst, 'PNG')


def get_suffix(name):
    for suffix in ['jpg', 'png', 'gif']:
        if suffix in name.lower():
            return suffix
    else:
        return 'unknown'


def process(md_file):
    basename = os.path.basename(md_file)
    base_dir = os.path.dirname(md_file)

    print(md_file)
    try:
        encoding = 'utf-8'
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except:
        encoding = 'gb18030'
        with open(md_file, 'r', encoding='gb18030') as f:
            md_content = f.read()

    # 找出所有图片链接
    media_urls = re.findall('\!\[.*?\]\((.*?)\)', md_content)
    if len(media_urls) != 0:
        # 创建res目录
        md_catalog = base_dir + '/Resources_{}'.format(basename[:-3:])
        # 新版本
        if not os.path.exists(md_catalog):
            os.mkdir(md_catalog)
        is_modified = False
        for media_no, media_url in enumerate(media_urls):
            media_no += 1
            print('   ', media_no, media_url)
            if 'data:image' in media_url:
                pass
            elif 'http' in media_url:
                try:
                    host = re.findall("://(.*?)/", media_url)
                    # 过滤本地链接
                    if len(host) == 0:
                        continue
                    print('   ', media_no, ', '.join(host))
                    headers.pop('referer', '')
                    if host[0] in ['segmentfault.com', 'user-images.githubusercontent.com']:
                        headers.pop('host', '')
                    elif host[0] == 'ask.qcloudimg.com':
                        headers['referer'] = 'https://cloud.tencent.com/developer/article/1691945'
                    else:
                        headers['host'] = host[0]
                    

                    r = requests.get(media_url, headers=headers)
                    print('   ', media_no, r.headers["Content-Type"])
                    is_webp = False
                    # 过滤非图片
                    if 'application/octet-stream' != r.headers["Content-Type"] and 'image' not in r.headers["Content-Type"]:
                        continue

                    # suffix = get_suffix(media_url)
                    # if suffix == "unknown":
                    suffix = r.headers["Content-Type"].split("/")[1]
                    # print('   ', suffix)
                    if suffix == 'webp':
                        is_webp = True
                        suffix = 'png'
                    elif suffix == 'octet-stream':
                        suffix = get_suffix(media_url)

                    media_name = '{0:02d}.{1}'.format(media_no, suffix)
                    media_path = '{}/{}'.format(md_catalog, media_name)

                    if r.status_code == 200:
                        with open(media_path, 'wb') as f:
                            f.write(r.content)

                    # webp2png
                    if is_webp:
                        webp2png(media_path, media_path)
                    # print('{}/{}'.format('Resources_{}'.format(basename[:-3:]), media_name))
                    # input('')
                    md_content = md_content.replace(media_url,
                                                    '{}/{}'.format('Resources_{}'.format(basename[:-3:]), media_name))
                    is_modified = True
                except:
                    traceback.print_exc()
                    print('    下载失败！')
            print()
        else:
            if is_modified:
                try:
                    os.rename(md_file, md_file + '.old')
                    with open(md_file, 'w', encoding=encoding) as f:
                        f.write(md_content)
                except:
                    pass


def get_mdfiles(target_path):
    if target_path[-1] == "/":
        target_path = target_path[:-1:]
    li = []
    dir_paths = []
    for f in os.listdir(target_path):
        if '_res' in f or 'Resources_' in f:
            continue
        name = target_path + "/" + f
        if os.path.isdir(name):
            dir_paths.append(name)
        elif '.md' in f and '.old' not in f:
            li.append(name)
            print(name)
    for dir_path in dir_paths:
        result = get_mdfiles(dir_path)
        if len(result) != 0:
            li += result
    return li


if len(sys.argv) == 2:
    print(sys.argv)
    if '.md' in sys.argv[1]:
        process(sys.argv[1])
        print('提示: 处理成功!')
else:
    inp = input('回车: 处理当前目录下的所有md文件\n dir: 处理当前目录及其子目录下的所有md文件\n输入：')
    print()
    print('当前目录: ' + os.getcwd() + '\n')
    if inp == "dir":
        md_files = get_mdfiles(os.getcwd())
    else:
        md_files = [os.getcwd() + '/' + f for f in os.listdir(os.getcwd()) if '.md' in f and '.old' not in f]
    #print('\n'.join(md_files))
    input('\n--回车后，开始处理--')
    for md_file in md_files:
        process(md_file)
        print()

print('提示: 2s后关闭窗口!')
time.sleep(2)
