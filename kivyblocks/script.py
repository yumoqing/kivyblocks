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

@SingletonDecorator
class ScriptEnv(DictObject):
	pass

def set_script_env(n,v):
	env = ScriptEnv()
	env.update({n:v})

class Script:
	def __init__(self, root):
		print('root=', root)
		self.root = root
		self.env = {}
		self.handlers = {}
		self.register('.tmpl', TemplateHandler)
		self.register('.dspy', DspyHandler)

	def url2filepath(self, url):
		if url.startswith('file://'):
			url = url[7:]
		return join(self.root, *url.split('/'))

	def dispatch(self, url, **kw):
		filepath = self.url2filepath(url)
		for suffix, handler in self.handlers.items():
			if filepath.endswith(suffix):
				env = self.env.copy()
				env.update(ScriptEnv())
				env.update(kw)
				env['root_path'] = self.root
				env['url'] = url
				env['filepath'] = filepath
				h = handler(env, **kw)
				d = h.render()
				try:
					return json.loads(d)
				except:
					return d

	def register(self, suffix, handler):
		self.handlers[suffix] = handler

	def set_env(self, n, v):
		self.env.update({n:v})

class BaseHandler:
	def entire_url(self, url):
		if url.startswith('file://') or \
				url.startswith('http://') or \
				url.startswith('hppts://'):
			return url
		p1 = self.env['url'].split('/')[:-1]
		p2 = url.split('/')
		return '/'.join(p1+p2)
	def __init__(self, env):
		self.env = env
		self.env['entire_url'] = self.entire_url

class TemplateHandler(BaseHandler):
	def __init__(self, env):
		super().__init__(env)
		root = env['root_path']
		paths = [root]
		fp = env['filepath'][len(root):]
		plst = fp.split(sep)[:-1]
		self.templ_file = basename(env['filepath'])
		cpath = root
		for p in plst:
			cpath = join(cpath, p)
			paths.append(cpath)

		self.engine = MyTemplateEngine(paths)

	def render(self):
		return self.engine.render(self.templ_file, self.env)

class DspyHandler(BaseHandler):
	def __init__(self, env):
		super().__init__(env)

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
		lenv = self.env.copy()
		lenv.update(params)
		txt = self.loadScript(self.env['filepath'])
		exec(txt,lenv,lenv)
		func = lenv['myfunc']
		return func(self.env, **lenv)