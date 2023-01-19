from bs4 import BeautifulSoup
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
		self.raw_content = article_json['content']
		self.content = preprocess_content(self.raw_content, config.download_image, config.asset_path)
  
		h = html2text.HTML2Text()
		h.body_width = 0 # 让 html2text.HTML2Text 不要自动换行
		self.raw_markdown = h.handle(self.content)
		self.markdown = final_process(self.raw_markdown)   

def request_json(article_id, user_agent):
	article_api_url = f'https://api.zhihu.com/articles/{article_id}'
	headers = { 'user-agent': user_agent }
	return requests.get(article_api_url, headers=headers).json()

def preprocess_content(content, download_image, asset_path):
	# tex 行内公示形如：'<img src="https://www.zhihu.com/equation?tex=%5Clog+p_%7B%5Ctheta%7D%28X%29" alt="\\log p_{\\theta}(X)" eeimg="1"/>'
	latex_pattern = r'<img src="https://www.zhihu.com/equation\?tex=.+?" alt="(.+?)".+?/>'
	def latex_repl(matchobj):
		return f'${matchobj.group(1)}$'
	content = re.sub(latex_pattern, latex_repl, content)
 
	# 把行间公式识别出来并用双 $$ 围起来
	latex_Interline_pattern = r'</p><p\s{1}data-pid="\w+">\$(.+?)\$</p><p\s{1}data-pid="\w+">'
	def latex_Interline_repl(matchobj):
		return f'</p><p\sdata-pid="tex">$$</p><p\sdata-pid="tex">{matchobj.group(1)}</p><p\sdata-pid="tex">$$</p><p\sdata-pid="tex">'
	content = re.sub(latex_Interline_pattern, latex_Interline_repl, content)
 
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

	# 增加代码块的转译
	soup = BeautifulSoup(content,'lxml')
	code_blocks = soup.find_all(name='code')

	try:
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
	except: pass

	content = str(soup)
	#print(content[0:1500])
	return content

def final_process(raw_markdown):
    # 后处理，用于删除代码块前后的多余空行，删除图片的无效后缀，修改行间公式中错误的 latex 换行符
    #        并为 中文、英文、tex行内公式 之间加上空格
	pattern = r"\s*```(python|cpp|matlab|text|c|powershell|html|go|java|c#|fortran|css|verilog|javascript|R|lua)\s*"
	raw_markdown = re.sub(pattern, r"\n```\1\n", raw_markdown)
	raw_markdown = re.sub(r"\s*```\s", '\n```\n', raw_markdown)
	  
	# 把 ![](data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'1050\' height=\'597\'></svg>) 删掉
	raw_markdown = re.sub(r'!\[\]\(data:image.+</svg>\)','', raw_markdown)
 
	# 处理 latex 行间公式转换出来后莫名其妙的反斜杠数量增生的问题
	raw_markdown = re.sub(r'\\\\\\', r'\\\\', raw_markdown)
	raw_markdown = re.sub(r'\\\\ \\\\', r'\\\\', raw_markdown)   
 
	# 中英文空格，latex 公式与周边字符的空格
	raw_markdown = re.sub('([A-Za-z]+)([\u4e00-\u9fa5]+)', r'\1 \2', raw_markdown)
	raw_markdown = re.sub('([\u4e00-\u9fa5]+)([A-Za-z]+)', r'\1 \2', raw_markdown)
 
	raw_markdown = re.sub('([$])([\u4e00-\u9fa5]+)', r'\1 \2', raw_markdown)
	raw_markdown = re.sub('([\u4e00-\u9fa5]+)([$])', r'\1 \2', raw_markdown)
 
	raw_markdown = re.sub('([$])([A-Za-z]+)', r'\1 \2', raw_markdown)
	raw_markdown = re.sub('([A-Za-z]+)([$])', r'\1 \2', raw_markdown)

	return raw_markdown