from crawler.image import *

if __name__ == '__main__':
    is_backup_old_file = True
    print('当前目录: ' + os.getcwd() + '\n')
    print('    1: 处理当前目录下的所有 markdown 文件')
    print('    2: 处理当前目录及其子目录下的所有 markdown 文件')
    choice = input('输入：')
    print()
    markdown_file_paths = []
    if choice == "1":
        markdown_file_paths = [os.path.join(os.getcwd(), file_path)
                               for file_path in os.listdir(os.getcwd())
                               if '.md' in file_path and '.old' not in file_path]
    elif choice == "2":
        markdown_file_paths = get_markdown_files(os.getcwd())
    else:
        blogs_dir_path = os.path.join(os.getcwd(), "blogs")
        if os.path.exists(blogs_dir_path):
            markdown_file_paths = get_markdown_files(blogs_dir_path)
        else:
            markdown_file_paths = [os.path.join(os.getcwd(), file_path)
                               for file_path in os.listdir(os.getcwd())
                               if '.md' in file_path and '.old' not in file_path]
    input('\n--回车后，开始处理--')
    for markdown_file_path in markdown_file_paths:
        download_images_for_markdown_file(markdown_file_path, is_backup_old_file)
        print()

    print('提示: 1s后关闭窗口!')
    time.sleep(1)
