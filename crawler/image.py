import os
import re
import sys
import time
import requests
import traceback
from PIL import Image
from shutil import copyfile

headers = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                  (KHTML, like Gecko) Chrome/67.0.3396.56 Safari/537.36'
}


def webp_to_png(image_file_path):
    im = Image.open(image_file_path)
    if im.mode == "RGBA":
        im.load()
        background = Image.new("RGB", im.size, (255, 255, 255))
        background.paste(im, mask=im.split()[3])
        im = background
        im.save(image_file_path, 'PNG')


def get_image_suffix_from_content_type(content_type):
    image_suffix = 'unknown'
    resource_type = content_type.split("/")[1]
    if resource_type == 'webp':
        image_suffix = 'webp'
    else:
        for candidate_suffix in ['jpg', 'jpeg', 'png', 'gif']:
            if resource_type.lower() == candidate_suffix:
                image_suffix = candidate_suffix
                break
    return image_suffix


def construct_image_name(image_idx, image_suffix):
    return '{0:02d}_{1}.{2}'.format(image_idx, int(time.time()), image_suffix)


def save_image_resource(rep, image_idx, image_dirname, image_suffix):
    is_webp_resource = image_suffix == 'webp'
    if is_webp_resource: image_suffix = 'png'
    image_name = construct_image_name(image_idx, image_suffix)

    image_file_path = '{}/{}'.format(image_dirname, image_name)
    with open(image_file_path, 'wb') as f:
        f.write(rep.content)

    if is_webp_resource:
        webp_to_png(image_file_path)
    return image_name


def get_content_and_encoding(file_path):
    for file_encoding in ['utf-8', 'gb18030']:
        try:
            with open(file_path, 'r', encoding=file_encoding) as f:
                content = f.read()
            return content, file_encoding
        except:
            continue


def download_images_for_markdown_file(markdown_file_path, is_backup_old_file=True):
    markdown_file_basename = os.path.basename(markdown_file_path)
    markdown_file_dirname = os.path.dirname(markdown_file_path)

    print('处理: ' + markdown_file_path)
    markdown_file_content, markdown_file_encoding = get_content_and_encoding(markdown_file_path)

    # 找出所有图片链接
    image_urls = re.findall('\!\[.*?\]\((.*?)\)', markdown_file_content)
    if len(image_urls) == 0:
        print("\t{} 没有图片资源".format(markdown_file_basename))
        return

    # 文件名去除空格，以解决图片链接无法被正确读取的问题
    markdown_file_basename = markdown_file_basename[:-3:].replace(' ', '_')

    # 创建图片资源目录
    image_relative_dirname = 'Resources_{}'.format(markdown_file_basename)
    markdown_image_dirname = '{}/{}'.format(markdown_file_dirname, image_relative_dirname)
    if not os.path.exists(markdown_image_dirname):
        os.mkdir(markdown_image_dirname)

    is_modified = False
    for image_idx, image_url in enumerate(image_urls):
        image_idx += 1
        # 链接去除无用字符
        image_download_url = image_url.split('?')[0]

        print('\t{}  url: {}'.format(image_idx, image_download_url))

        # 本地资源处理，用于文件改名时，同时也改资源名称
        host = re.findall("://(.*?)/", image_url)
        if len(host) == 0:
            src_relative_path = image_url[::].replace('\\', '\/')
            part_length = len(src_relative_path.split('/'))
            if part_length != 2:
                print('\t{}  wrong path {}'.format(image_idx, src_relative_path))
                continue
            src_dirname, image_name = src_relative_path.split('/')
            # 目录一致，不移动
            if src_dirname == image_relative_dirname:
                continue
            if image_name is None:
                continue
            src_path = '{}/{}'.format(markdown_file_dirname, src_relative_path)

            image_suffix = src_relative_path.split('.')[-1]
            dst_file_name = construct_image_name(image_idx, image_suffix)
            dst_relative_path = '{}/{}'.format(image_relative_dirname, dst_file_name)
            dst_path = '{}/{}'.format(markdown_file_dirname, dst_relative_path)
            copyfile(src_path, dst_path)
            print('\t{}  dst: {}'.format(image_idx, dst_relative_path))
            print()
            markdown_file_content = markdown_file_content.replace(src_relative_path, dst_relative_path)
            is_modified = True
            continue

        # print('\t{} host: {}'.format(image_idx, ', '.join(host)))

        # 反爬处理
        headers.pop('referer', '')
        if host[0] in ['segmentfault.com', 'user-images.githubusercontent.com']:
            headers.pop('host', '')
        elif host[0] == 'ask.qcloudimg.com':
            headers['referer'] = 'https://cloud.tencent.com/developer/article/1691945'
        elif 'pdai.tech' in image_download_url:
            headers['referer'] = 'https://pdai.tech/'
        else:
            headers['host'] = host[0]

        # 下载文件
        try:
            rep = requests.get(image_download_url, headers=headers)
        except:
            traceback.print_exc()
            print('    下载失败！')
            continue

        # 下载不成功，跳过
        if rep.status_code != 200: continue

        rep_content_type = rep.headers["Content-Type"]
        print('\t{} type: {}'.format(image_idx, rep_content_type))

        # 过滤非图片
        if 'application/octet-stream' != rep_content_type and 'image' not in rep_content_type: continue

        # 获取图片资源后缀
        image_suffix = get_image_suffix_from_content_type(rep_content_type)

        # 将图片资源保存到本地
        image_name = save_image_resource(rep, image_idx, markdown_image_dirname, image_suffix)

        # 更新图片资源链接
        image_relative_url = '{}/{}'.format(image_relative_dirname, image_name)
        markdown_file_content = markdown_file_content.replace(image_url, image_relative_url)
        is_modified = True

        print()

    if not is_modified:
        return

    # 备份源文件
    if is_backup_old_file:
        os.rename(markdown_file_path, markdown_file_path + '.old')

    # 更新文件
    with open(markdown_file_path, 'w', encoding=markdown_file_encoding) as f:
        f.write(markdown_file_content)


def get_markdown_files(target_dir_path):
    if target_dir_path[-1] == "/":
        target_dir_path = target_dir_path[:-1:]
    markdown_file_paths = []
    dir_paths = []
    for filename in os.listdir(target_dir_path):
        if '_res' in filename or 'Resources_' in filename:
            continue
        name = os.path.join(target_dir_path, filename)
        if os.path.isdir(name):
            dir_paths.append(name)
        elif '.md' in filename and '.old' not in filename:
            markdown_file_paths.append(name)
            print(name)
    for dir_path in dir_paths:
        result = get_markdown_files(dir_path)
        if len(result) != 0:
            markdown_file_paths += result
    return markdown_file_paths
