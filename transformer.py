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

isLocal_str = input('是否将公式储存为本地文件[Y/n]: ')
isLocal = False
if isLocal_str == 'Y':
    isLocal = True

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
    elif isLocal:
        tmp = 'equation' + str(texIndexCount)
        path = targetDirUrl + os.sep + tmp + '.svg'
        relativePath = '.' + os.sep + article_number_str + '_assets' + os.sep + tmp + '.svg'
        with open(path, 'wb') as tex_file:
            tex_file.write(res)
        img['src'] = relativePath
        texIndexCount = texIndexCount + 1
    imgCount = imgCount + 1
    sys.stdout.write('已处理图片数: ' + str(imgCount) + '\r')
print('图片处理完成')

print('\n正在生成HTML')

targetHTML_content = soup.prettify()
targetHTML = '<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><title>' + html_title + '</title></head><body>' + targetHTML_content + '</body></html>'


with open(targetHTMLUrl, 'w') as file_object:
    file_object.write(targetHTML)

if isLocal:
    hasTex_str = input('是否在Markdown中使用TeX公式[Y/n]: ')
    hasTex = False
    if hasTex_str == 'Y':
        hasTex = True
    if hasTex:
        print('\n正在处理公式')
        texCount = 0
        sys.stdout.write('已处理公式数: ' + str(texCount) + '\r')
        for img in imgs:
            image_title = img['src'].split('/')[-1]
            if 'equation' in image_title:
                tex_doc = img['alt']
                img.name = 'span'
                if 'tmp' in img.attrs:
                    img.string = '$$' + tex_doc + '$$'
                else:
                    img.string = '$' + tex_doc + '$'
                img.attrs.clear()
                texCount = texCount + 1
                sys.stdout.write('已处理公式数: ' + str(texCount) + '\r')
        print('公式处理完成')

targetMarkdown = soup.prettify()

h = html2text.HTML2Text()

print('\n正在生成Markdown')

with open(targetMdUrl, 'w') as markdown_file:
    markdown_file.write(h.handle(targetMarkdown))
