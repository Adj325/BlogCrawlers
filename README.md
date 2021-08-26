# BlogCrawlers
各大博客爬虫，爬取并保存为 markdown 文件

## 当前支持

根据网址，匹配配置，爬取博客，保存至本地。

支持网站：CSDN、博客园、简书、掘金、微信文章、cnblog、脚本之家、segmentfault、知乎专栏

## 预想功能

- 本地版：爬取博客，并保存到本地指定目录（图片资源本地化）
- 网站版：解析博客，存储到数据库，供所有用户查看下载（源文件，md 文件，md+图片.zip）

### 更新历史

- 2020-06-27

  解决 SegmentFault 爬取 404 的问题。解决方案：使用会话进行请求。

  现存问题：SF 图片防盗链，图片真实链接暂未研究出怎么获取。
  
- 2020-06-29

  - 解决问题
    - 采用bs匹配解决嵌套匹配时re出现的问题
    - 增加了一些网站支持
    - 修复网络编码问题
    - 修复转换后md文件中的部分格式问题

  - 现存问题
    - html2text库转换后md文件中容易出现断行现象