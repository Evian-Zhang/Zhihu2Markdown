# Zhihu2Markdown: 将知乎专栏的文章转成 HTML 及 Markdown 格式

本 python 脚本可以将知乎专栏的文章转成 HTML 及 Markdown 格式并将文章中的图片一起储存在本地。

提供的功能有：

* 将知乎专栏的文章转成 HTML 格式，并且将文章中的图片全部存储到本地
* 可以选择将文章中的 TeX 公式以 mathjax 的形式加载到 HTML 文档中
* 将知乎专栏的文章转成 Markdown 格式，并且将文章中的图片全部存储到本地
* 可以选择将文章中的 TeX 公式以 TeX 代码的形式加载到 Markdown 文档中
* 目前暂未支持文章中插入视频

## python 包依赖

* bs4
* html2text

## 使用方法

在终端下进入该脚本文件所在文件夹，运行

```bash
python transformer.py
```

即可。