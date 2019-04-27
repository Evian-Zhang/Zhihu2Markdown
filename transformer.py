import urllib.request
import json
from bs4 import BeautifulSoup
import os
import sys
import html2text

primitive_url = input('请输入知乎专栏文章的网址（如：https://zhuanlan.zhihu.com/p/12345678）: ')
article_number_str = primitive_url.split('/')[-1]
url = r'https://api.zhihu.com/article/' + article_number_str

res = urllib.request.urlopen(url)
html = res.read().decode('utf-8')
jsonText = json.loads(html)
html_doc = jsonText['content']
html_title = jsonText['title']
html_doc = html_doc.replace('<br> <img src="https://www.zhihu.com/equation?', '<br> <img tmp="notinline" src="https://www.zhihu.com/equation?')
html_doc = html_doc.replace('<br><img src="https://www.zhihu.com/equation?', '<br><img tmp="notinline" src="https://www.zhihu.com/equation?')
soup = BeautifulSoup(html_doc, features='html.parser')
imgs = soup.find_all('img')

targetUrl = input('请输入本地保存地址: ')
if targetUrl[-1] != os.sep:
    targetUrl = targetUrl + os.sep
targetHTMLUrl = targetUrl + article_number_str + '.html'
targetMdUrl = targetUrl + article_number_str + '.md'
targetDirUrl = targetUrl + article_number_str + '_assets'
if not os.path.exists(targetDirUrl):
    os.mkdir(targetDirUrl)

print('\n正在下载图片')

texIndexCount = 0
imgCount = 0

sys.stdout.write('已处理图片数: ' + str(imgCount) + '\r')

for img in imgs:
    res = urllib.request.urlopen(img['src']).read()
    image_title = img['src'].split('/')[-1]
    if 'equation' not in image_title:
        path = targetDirUrl + os.sep + image_title
        relativePath = '.' + os.sep + article_number_str + '_assets' + os.sep + image_title
        with open(path, 'wb') as img_file:
            img_file.write(res)
        img.attrs.clear()
        img['src'] = relativePath
    else:
        tex_doc = img['alt']
        img.string = '$\\displaystyle ' + tex_doc + '$'
        img.name = 'span'
        img.attrs.clear()
        img['class'] = 'text/tex'
    imgCount = imgCount + 1
    sys.stdout.write('已处理图片数: ' + str(imgCount) + '\r')
print('图片处理完成')

print('\n正在生成HTML')

targetHTML_content = soup.prettify()
targetHTML_head = '''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>''' + html_title + '''</title>
<script src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML' async></script>
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
    tex2jax: {
        inlineMath: [ ['$','$'] ],
        displayMath: [ ['$$','$$'] ]
    }
});
</script>
</head>'''
targetHTML = targetHTML_head + '<body>' + targetHTML_content + '</body></html>'


with open(targetHTMLUrl, 'w') as file_object:
    file_object.write(targetHTML)

targetMarkdown = soup.prettify()

h = html2text.HTML2Text()

print('\n正在生成Markdown')

with open(targetMdUrl, 'w') as markdown_file:
    markdown_file.write(h.handle(targetMarkdown))
