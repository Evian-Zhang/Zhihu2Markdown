# Zhihu2Markdown: 将知乎专栏的文章转成 HTML 及 Markdown 格式

本 python 脚本可以将知乎专栏的文章转成 HTML 及 Markdown 格式并将文章中的图片一起储存在本地。

提供的功能有：

* 将知乎专栏的文章转成 Markdown 格式，并且将文章中的图片全部存储到本地
* 可以选择将文章中的 TeX 公式以 TeX 代码的形式加载到 Markdown 文档中
* 目前暂未支持文章中插入视频

## 安装

将本仓库下载或克隆至本地，并且本地需安装Python 3.8及以上版本，包依赖在`requirements.txt`中有描述。

## 使用方法

在终端下进入该脚本文件所在文件夹，运行

```shell
python zhihu2markdown.py --help
```

即可获得使用方法：

```
usage: zhihu2markdown.py [-h] [-o OUTPUT] [-i IMAGE_DIR] [-a USER_AGENT] article_url

Transform zhihu article to Markdown format

positional arguments:
  article_url           URL of zhihu article

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        path of output markdown file
  -i IMAGE_DIR, --image_dir IMAGE_DIR
                        If present, download image to the image dir path
  -a USER_AGENT, --user_agent USER_AGENT
                        User agent
```

最简单的可以直接

```shell
python zhihu2markdown https://zhuanlan.zhihu.com/p/56694990
```

那么就可以将相应URL的文章转为Markdown文本。

其它可选选项详见`--help`指令。

### 作为库使用

也支持将作为库使用：

```python
from lib.transformer import *

config = Config(
	user_agent="", # user agent
	download_image=True, # whether download image
	asset_path="" # path of downloaded image
)
article = Article(article_id, config)

print(article.markdown)
```