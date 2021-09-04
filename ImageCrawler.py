from crawler.image import *

if __name__ == '__main__':
    is_backup_old_file = True
    print('    1: 处理当前目录下的所有 markdown 文件')
    print('    2: 处理当前目录及其子目录下的所有 markdown 文件')
    print('enter: 处理 blogs 目录下的所有 markdown 文件')
    choice = input('输入：')
    print()
    print('当前目录: ' + os.getcwd() + '\n')
    markdown_file_paths = []
    if choice == "1":
        markdown_file_paths = [os.getcwd() + '/' + f for f in os.listdir(os.getcwd()) if
                               '.md' in f and '.old' not in f]
    elif choice == "2":
        markdown_file_paths = get_markdown_files(os.getcwd())
    else:
        if os.path.exists(os.getcwd() + "/blogs"):
            markdown_file_paths = get_markdown_files(os.getcwd() + "/blogs")
    input('\n--回车后，开始处理--')
    for markdown_file_path in markdown_file_paths:
        download_images_for_markdown_file(markdown_file_path, is_backup_old_file)
        print()

    print('提示: 1s后关闭窗口!')
    time.sleep(1)
