import urllib.request
import json
from bs4 import BeautifulSoup
import os
import html2text

primitive_url = input('请输入知乎专栏文章的网址（如：https://zhuanlan.zhihu.com/p/12345678）: ')
article_number_str = primitive_url.split('/')[-1]
url = r'https://api.zhihu.com/article/' + article_number_str

res = urllib.request.urlopen(url)
html = res.read().decode('utf-8')
jsonText = json.loads(html)
html_doc = jsonText['content']
soup = BeautifulSoup(html_doc, features='html.parser')
imgs = soup.find_all('img')

targetUrl = input('请输入本地保存地址: ')
if targetUrl[-1] != os.sep:
    targetUrl = targetUrl + os.sep
targetHTMLUrl = targetUrl + article_number_str + '.html'
targetMdUrl = targetUrl + article_number_str + '.md'
targetDirUrl = targetUrl + article_number_str + '_assets' + os.sep
os.mkdir(targetDirUrl)

counter = 0

for img in imgs:
    res = urllib.request.urlopen(img['src']).read()
    image_title = img['src'].split('/')[-1]
    if 'equation' not in image_title:
        path = targetDirUrl + image_title
        with open(path, 'wb') as f:
            f.write(res)
        img.attrs.clear()
        img['src'] = path

targetHTML = soup.prettify()

with open(targetHTMLUrl, 'w') as file_object:
    file_object.write(targetHTML)

for img in imgs:
    res = urllib.request.urlopen(img['src']).read()
    image_title = img['src'].split('/')[-1]
    if 'equation' in image_title:
        tex_doc = img['alt']
        img.name = 'span'
        img.attrs.clear()
        img.string = '$' + tex_doc + '$'

targetMarkdown = soup.prettify()

h = html2text.HTML2Text()
with open(targetMdUrl, 'w') as markdown_file:
    markdown_file.write(h.handle(targetMarkdown))
