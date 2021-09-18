import requests
import re
import html2text
import os

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15'

class Config:
	def __init__(self, user_agent=DEFAULT_USER_AGENT, download_image=False, asset_path='.'):
		self.user_agent = user_agent
		self.download_image = download_image
		self.asset_path = os.path.expanduser(asset_path)

class Article:
	def __init__(self, article_id, config):
		article_json = request_json(article_id, config.user_agent)

		self.id = article_json['id']
		self.title = article_json['title']
		self.created = article_json['created']
		self.updated = article_json['updated']
		content = article_json['content']
		self.content = preprocess_content(content, config.download_image, config.asset_path)
		self.raw_markdown = html2text.html2text(self.content)
		self.markdown = final_process(self.raw_markdown)   # 后处理，删除代码块前后多余的空行和图片的无效后缀

def request_json(article_id, user_agent):
	article_api_url = f'https://api.zhihu.com/articles/{article_id}'
	headers = { 'user-agent': user_agent }
	return requests.get(article_api_url, headers=headers).json()

def preprocess_content(content, download_image, asset_path):
	latex_pattern = r'<img src="https://www.zhihu.com/equation?tex=.+?" alt="(.+?)".+?/>'
	def latex_repl(matchobj):
		return f'${matchobj.group(1)}$'
	content = re.sub(latex_pattern, latex_repl, content)
	if download_image:
		image_pattern = r'<img src="(https?.+?)".+?/>'
		def image_repl(matchobj):
			image_url = matchobj.group(1)
			image_title = image_url.split('/')[-1]
			image_download_path = os.path.join(asset_path, image_title)
			image = requests.get(image_url).content
			with open(image_download_path, 'wb') as image_file:
				image_file.write(image)
			return f'<img src="{image_download_path}">'
		content = re.sub(image_pattern, image_repl, content)

	## 以下部分尝试增加代码块的转译
	soup = BeautifulSoup(content,'lxml')
	code_blocks = soup.find_all(name='code')

	for code_block in code_blocks:
		code_type = code_block['class'][0]
		prehead = soup.new_string('```' + code_type[9:])
		afterhead = soup.new_string('```')

		code_block.name = 'pre'
		code_block.attrs = {}
		
		code_block.insert_before(prehead)
		code_block.parent.append(afterhead)

		code_block.parent.parent.unwrap()
		code_block.parent.unwrap()

	content = str(soup)
	#print(content[0:1500])
	return content

def final_process(raw_markdown):
	# 后处理，用于删除代码块前后的多余空行（但仅针对以下的编程语言，其余需要手动添加），并删除图片的无效后缀
	raw_markdown = re.sub(r"\s*```python\s*", '\n```python\n    ', raw_markdown)
	raw_markdown = re.sub(r"\s*```text\s*", '\n```text\n    ', raw_markdown)
	raw_markdown = re.sub(r"\s*```powershell\s*", '\n```powershell\n    ', raw_markdown)
	raw_markdown = re.sub(r"\s*```html\s*", '\n```html\n    ', raw_markdown)
	raw_markdown = re.sub(r"\s*```matlab\s*", '\n```matlab\n    ', raw_markdown)
	raw_markdown = re.sub(r"\s*```java\s*", '\n```java\n    ', raw_markdown)
	raw_markdown = re.sub(r"\s*```javascript\s*", '\n```javascript\n    ', raw_markdown)
	  
	raw_markdown = re.sub(r"\s*```\s", '\n```\n', raw_markdown)
	  
	raw_markdown = re.sub(r'!\[\]\(data:image\S*\n[^\n]*\n','\n', raw_markdown)
	return raw_markdown
