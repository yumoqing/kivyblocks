import os
import codecs
import traceback
try:
	import ujson as json
except:
	import json
from os.path import join, sep, dirname, basename
from appPublic.Singleton import GlobalEnv
from appPublic.jsonConfig import getConfig
from appPublic.myTE import MyTemplateEngine
from appPublic.Singleton import SingletonDecorator
from appPublic.dictObject import DictObject

from kivy.logger import Logger
from kivy.utils import platform

@SingletonDecorator
class ScriptEnv(DictObject):
	pass

def set_script_env(n,v):
	env = ScriptEnv()
	env.update({n:v})

class Script:
	def __init__(self):
		config = getConfig()
		self.root = config.script_root
		if sep != '/':
			self.root = self.root.replace(sep, '/')
		# print('Script.root=', self.root)
		self.env = {}
		self.env['uihome'] = config.uihome
		self.handlers = {}
		self.register('.tmpl', TemplateHandler)
		self.register('.dspy', DspyHandler)
		self.register('.ui', TemplateHandler)

	def url2filepath(self, url):
		if url.startswith('file://'):
			url = url[7:]
		parts = self.root.split('/')
		if url[0] == '/':
			url = url[1:]
		parts += url.split('/')
		ret = '/'.join(parts)
		# ret = join(self.root, *url.split('/'))
		print('url2filepath():root=', self.root, url, parts, ret)
		return ret

	def show_info(self, env):
		workdir = env['workdir']
		sfile = env['filepath']
		url = env['url']
		# print(f'script:workdir={workdir}')
		# print(f'script:script_file={sfile}')
		# print(f'script:url={url}')
		sdir = os.path.join(workdir, 'scripts')
		sf_exists = os.path.isdir(sdir)
		conf_f = os.path.join(workdir, 'conf', 'config.json')
		conf_exists = os.path.isfile(conf_f)
		# print(f'script:script exists {sf_exists}')
		# print(f'script:config.json exists {conf_exists}')

	def dispatch(self, url, **kw):
		filepath = self.url2filepath(url)
		# print('dispatch():url=', url, 'filepath=', filepath)
		for suffix, handler in self.handlers.items():
			if filepath.endswith(suffix):
				env = self.env.copy()
				env.update(ScriptEnv())
				env.update(kw)
				env['root_path'] = self.root
				env['url'] = url
				env['filepath'] = filepath
				h = handler(self, env)
				d = h.render()
				try:
					return json.loads(d)
				except:
					return d
		return filepath

	def register(self, suffix, handler):
		self.handlers[suffix] = handler

	def set_env(self, n, v):
		self.env.update({n:v})

class BaseHandler:
	def real_filepath(self, url):
		myurl = self.entire_url(url)
		return self.script.url2filepath(myurl)

	def entire_url(self, url):
		if url.startswith('file://') or \
				url.startswith('http://') or \
				url.startswith('hppts://'):
			return url
		tokens = url.split('/')
		if tokens[0] == '':
			root = self.env['uihome']
			if root[-1] == '/':
				return root + url[1:]
			else:
				tokens[0] = root
				return '/'.join(tokens)

		p1 = self.env['url'].split('/')[:-1]
		ret = '/'.join(p1+tokens)
		print('entire_url(): org_url=', self.env['url'],
				'url=', url,
				'p1=', p1,
				'tokens=', tokens,
				'ret=', ret)
		return ret

	def __init__(self, script, env):
		self.script = script
		self.env = env
		self.env['entire_url'] = self.entire_url
		self.env['real_filepath'] = self.real_filepath

class TemplateHandler(BaseHandler):
	def __init__(self, script, env):
		super().__init__(script, env)
		root = env['root_path']
		paths = [root]
		fp = env['filepath'][len(root)+1:]
		plst = fp.split('/')[:-1]
		self.templ_file = basename(env['filepath'])
		cpath = root
		for p in plst:
			cpath = f'{cpath}/{p}'
			paths.append(cpath)

		paths.reverse()
		print(f'paths={paths}')
		self.engine = MyTemplateEngine(paths)

	def render(self):
		try:
			return self.engine.render(self.templ_file, self.env)
		except Exception as e:
			print('Exception:', str(e))
			print('filename=', self.env['filepath'])
			traceback.print_exc()

class DspyHandler(BaseHandler):
	def __init__(self, script, env):
		super().__init__(script, env)

	def loadScript(self, path):
		data = ''
		with codecs.open(path,'rb','utf-8') as f:
			data = f.read()
		b= ''.join(data.split('\r'))
		lines = b.split('\n')
		lines = ['\t' + l for l in lines ]
		txt = "def myfunc(request,**ns):\n" + '\n'.join(lines)
		return txt

	def render(self, params={}):
		try:
			lenv = self.env.copy()
			lenv.update(params)
			txt = self.loadScript(self.env['filepath'])
			exec(txt,lenv,lenv)
			func = lenv['myfunc']
			return func(self.env, **lenv)
		except Exception as e:
			print('Exception:', str(e))
			print('filename=', self.env['filepath'])
			traceback.print_exc()

