import os
import sys
import codecs
# import ujson as json
try:
    import ujson as json
except:
    import json
from traceback import print_exc

from functools import partial

from appPublic.dictExt import dictExtend
from appPublic.folderUtils import ProgramPath
from appPublic.dictObject import DictObject
from appPublic.Singleton import SingletonDecorator, GlobalEnv
from appPublic.datamapping import keyMapping
from appPublic.registerfunction import RegisterFunction

from kivy.logger import Logger
from kivy.config import Config
from kivy.metrics import sp,dp,mm
from kivy.core.window import WindowBase, Window
from kivy.properties import BooleanProperty
from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView
from kivy.app import App
from kivy.factory import Factory
from kivy.uix.video import Video
from .utils import *
from .newvideo import Video
from .orientationlayout import OrientationLayout
from .threadcall import HttpClient
from .register import *
from .script import Script, set_script_env

class WidgetNotFoundById(Exception):
	def __init__(self, id):
		super().__init__()
		self.idstr = id
	
	def __str__(self):
		return "Widget not found by id:" + self.idstr + ':'

	def __expr__(self):
		return str(self)

class ClassMethodNotFound(Exception):
	def __init__(self,k,m):
		super().__init__()
		self.kname = k
		self.mname = m

	def __str__(self):
		s = 'Method(%s) not found in class(%s)' % (self.mname,
					str(self.kname.__classname__))
		return s
	
	def __expr__(self):
		return self.__str__()

	
class NotExistsObject(Exception):
	def __init__(self,name):
		super().__init__()
		self.name = name

	def __str__(self):
		s = 'not exists widget(%s)' % self.name
		return s
	
	def __expr__(self):
		return self.__str__()

class ArgumentError(Exception):
	def __init__(self,argument,desc):
		super().__init__()
		self.argument = argument
		self.desc = desc
	
	def __str__(self):
		s = 'argument(%s) missed:%s' % (self.argument,self.desc)
		return s
	
	def __expr__(self):
		return self.__str__()


class NotRegistedWidget(Exception):
	def __init__(self, name:str):
		super().__init__()
		self.widget_name = name

	def __str__(self):
		s = 'not reigsted widget(%s)' % self.name
		return s
	
	def __expr__(self):
		return self.__str__()

def registerWidget(name:str,widget):
	globals()[name] = widget


class Blocks(EventDispatcher):
	def __init__(self):
		EventDispatcher.__init__(self)
		self.action_id = 0
		self.register_event_type('on_built')
		self.register_event_type('on_failed')
		self.env = GlobalEnv()
		config = getConfig()
		if config.script_root:
			self.script = Script(config.script_root)
		else:
			self.script = Script(config.workdir)

	def set(self, k:str, v):
		self.env[k] = v
	
	def register_widget(self, name:str, widget:Widget):
		globals()[name] = widget

	def buildAction(self, widget:Widget, desc):
		conform_desc = desc.get('conform')
		blocks = Blocks()
		if not conform_desc:
			return partial(blocks.uniaction, widget, desc)
		func =partial(blocks.conform_action,widget, desc)
		return func
		
	def eval(self, s:str, l:dict):
		g = {}
		forbidens = [
			"os",
			"sys",
			"codecs",
			"json",
		]

		for k,v in globals().copy().items():
			if k not in forbidens:
				g[k] = v

		"""
		g['__builtins__'] = globals()['__builtins__']
		g['__builtins__']['__import__'] = None
		g['__builtins__']['__loader__'] = None
		g['__builtins__']['open'] = None
		"""
		g.update(self.env)
		return eval(s,g,l)

	def getUrlData(self, url:str, method:str='GET',
						params:dict={}, files:dict={},
					callback=None,
					errback=None,**kw):

		if url is None:
			if errback:
				errback(None,Exception('url is None'))
			else:
				return None

		if url.startswith('file://'):
			return self.script.dispatch(url, **params)
		elif url.startswith('http://') or url.startswith('https://'):
			try:
				hc = HttpClient()
				resp=hc(url,method=method,params=params,files=files)
				# print('Blocks.py :resp=',resp)
				return resp
			except Exception as e:
				print_exc()
				if errback:
					return errback(None,e)
				return None
		else:
			config = getConfig()
			url = config.uihome + url
			return self.getUrlData(url,method=method,
					params=params,
					files=files,
					**kw)

	def strValueExpr(self,s:str,localnamespace:dict={}):
		if not s.startswith('py::'):
			return s
		s = s[4:]
		try:
			v = self.eval(s,localnamespace)
			return v
		except Exception as e:
			print('Exception .... ',e,'script=',s)
			print_exc()
			return s

	def arrayValueExpr(self,arr:list,localnamespace:dict={}) -> list:
		d = []
		for v in arr:
			if type(v) == type(''):
				d.append(self.strValueExpr(v,localnamespace))
				continue
			if type(v) == type([]):
				d.append(self.arrayValueExpr(v,localnamespace))
				continue
			if type(v) == type({}):
				d.append(self.dictValueExpr(v,localnamespace))
				continue
			if type(v) == type(DictObject):
				d.append(self.dictValueExpr(v,localnamespace))
				continue
			d.append(v)
		return d

	def dictValueExpr(self,dic:dict,localnamespace:dict={}) -> dict:
		d = {}
		for k,v in dic.items():
			if type(v) == type(''):
				d[k] = self.strValueExpr(v,localnamespace)
				continue
			if type(v) == type([]):
				d[k] = self.arrayValueExpr(v,localnamespace)
				continue
			if type(v) == type({}):
				d[k] = self.dictValueExpr(v,localnamespace)
				continue
			if type(v) == type(DictObject):
				d[k] = self.dictValueExpr(v,localnamespace)
				continue
			d[k] = v
		return d
	def valueExpr(self,obj,localnamespace:dict={}):
		if type(obj) == type(''):
			return self.strValueExpr(obj,localnamespace)
		if type(obj) == type([]):
			return self.arrayValueExpr(obj,localnamespace)
		if type(obj) == type({}):
			return self.dictValueExpr(obj,localnamespace)
		if isinstance(obj,DictObject):
			return self.dictValueExpr(obj,localnamespace)
		return obj

	def w_build(self,desc) -> Widget:
		widgetClass = desc.get('widgettype',None)
		if not widgetClass:
			Logger.info("Block: w_build(), desc invalid", desc)
			raise Exception(desc)

		widgetClass = desc['widgettype']
		opts = self.valueExpr(desc.get('options',{}).copy())
		widget = None
		try:
			klass = Factory.get(widgetClass)
			widget = klass(**opts)
		except Exception as e:
			print('Error:',widgetClass,'contructon error')
			print_exc()
			raise NotExistsObject(widgetClass)

		if desc.get('id'):
			id = desc.get('id')
			if id.startswith('app.'):
				app = App.get_running_app()
				id = id[4:]
				setattr(app, id, widget)
			if id.startswith('root.'):
				app = App.get_running_app()
				id = id[5:]
				setattr(app.root, id, widget)
				
			if '.' in id:
				Logger.info('widget id(%s) can not contain "."', id)
			else:
				widget.widget_id = id
		
		widget.build_desc = desc
		self.build_attributes(widget, desc)
		self.build_rest(widget, desc)
		self.buildBinds(widget, desc)
		return widget
		
	def build_attributes(self, widget:Widget,desc,t=None):
		excludes = ['widgettype','options','subwidgets','binds']
		for k,v in [(k,v) for k,v in desc.items() if k not in excludes]:
			if isinstance(v,dict) and v.get('widgettype'):
				b = Blocks()
				v = self.valueExpr(v, localnamespace={'self':widget})
				w = b.widgetBuild(v)
				if hasattr(widget,k):
					aw = getattr(widget,k)
					if isinstance(aw,Layout):
						aw.add_widget(w)
						continue
				setattr(widget,k,w)
				continue
			setattr(widget,k,self.valueExpr(v,\
						localnamespace={'self':widget}))

	def build_rest(self, widget:Widget,desc,t=None):
		self.subwidget_total = len(desc.get('subwidgets',[]))
		self.subwidgets = [ None for i in range(self.subwidget_total)]
		pos = 0
		for pos,sw in enumerate(desc.get('subwidgets',[])):
			b = Blocks()
			if isinstance(sw, str):
				# w = Blocks.getWidgetById(sw, from_widget=widget)
				w = Blocks.findWidget(sw, from_widget=widget)
				if w:
					widget.add_widget(w)
				continue
				
			kw = self.valueExpr(sw.copy(), 
						localnamespace={'self':widget})
			w = b.widgetBuild(kw)
			if w:
				widget.add_widget(w)


	def buildBinds(self, widget:Widget, desc:dict):
		for b in desc.get('binds',[]):
			kw = self.valueExpr(b.copy(), \
						localnamespace={'self':widget})
			self.buildBind(widget,kw)

	def buildBind(self, widget:Widget, desc:dict):
		wid = desc.get('wid','self')
		# w = Blocks.getWidgetById(desc.get('wid','self'),from_widget=widget)
		w = Blocks.findWidget(desc.get('wid','self'),from_widget=widget)
		if not w:
			Logger.info('Block: id(%s) %s',desc.get('wid','self'),
							'not found via Blocks.getWidgetById()')
			return
		event = desc.get('event')
		if event is None:
			Logger.info('Block: binds desc miss event, desc=%s',str(desc))
			return
		f = self.buildAction(widget,desc)
		if f is None:
			Logger.info('Block: get a null function,%s',str(desc))
			return
		w.bind(**{event:f})
	
	def multipleAction(self, widget:Widget, desc, *args):
		desc1 = {k:v for k, v in desc.items() if k != 'actions'}
		mydesc = desc1.copy()
		for a in desc['actions']:
			new_desc = mydesc.copy()
			new_desc.update(a)
			self.uniaction(widget,new_desc, *args)

	def conform_action(self, widget:Widget, desc, *args):
		conform_desc = desc.get('conform')
		blocks = Blocks()
		if not conform_desc:
			blocks.uniaction(widget, desc,*args, **kw)
			return
		w = blocks.widgetBuild({
			"widgettype":"Conform",
			"options":conform_desc
		})
		w.bind(on_conform=partial(blocks.uniaction, widget, desc))
		w.open()

	def uniaction(self, widget:Widget, desc, *args):
		acttype = desc.get('actiontype')
		if acttype=='blocks':
			return self.blocksAction(widget,desc, *args)
		if acttype=='urlwidget':
			return self.urlwidgetAction(widget,desc, *args)
		if acttype == 'registedfunction':
			return self.registedfunctionAction(widget,desc, *args)
		if acttype == 'script':
			return self.scriptAction(widget, desc, *args)
		if acttype == 'method':
			return self.methodAction(widget, desc, *args)
		if acttype == 'event':
			return self.eventAction(widget, desc, *args)
		if acttype == 'multiple':
			return self.multipleAction(widget, desc, *args)

		alert("actiontype(%s) invalid" % acttype,title='error')

	def eventAction(self, widget:Widget, desc, *args):
		target = self.get_target(widget, desc)
		event = desc.get('dispatch_event')
		if not event:
			Logger.info('Block: eventAction():desc(%s) miss dispatch_event',
							str(desc))
			return
		params = desc.get('params',{})
		d = self.getActionData(widget,desc, *args)
		if d:
			params.update(d)
		try:
			target.dispatch(event, params)
		except Exception as e:
			Logger.info(f'Block: eventAction():dispatch {event} error')
			print_exc()
			return
		
	def get_target(self, widget:Widget, desc):
		if not desc.get('target'):
			return None
		# return Blocks.getWidgetById(desc.get('target'),from_widget=widget)
		return Blocks.findWidget(desc.get('target'),from_widget=widget)

	def blocksAction(self, widget:Widget, desc, *args):
		target = self.get_target(widget, desc)
		add_mode = desc.get('mode','replace')
		opts = desc.get('options').copy()
		d = self.getActionData(widget,desc, *args)
		p = opts.get('options',{}).copy()
		if d:
			p.update(d)
		opts['options'] = p
		def doit(target:Widget, add_mode:str, o, w:Widget):
			if isinstance(w, Modal):
				return

			if target and not w.parent:
				if add_mode == 'replace':
					target.clear_widgets()
				target.add_widget(w)

		def doerr(o,e):
			Logger.info('Block: blocksAction(): desc=%s widgetBuild error'
								,str(desc))
			raise e

		b = Blocks()
		b.bind(on_built=partial(doit,target,add_mode))
		b.bind(on_failed=doerr)
		b.widgetBuild(opts)
		
	def urlwidgetAction(self, widget:Widget, desc, *args):
		target = self.get_target(widget, desc)
		add_mode = desc.get('mode','replace')
		opts = desc.get('options', {}).copy()
		p1 = opts.get('params',{})
		p = {}
		if p1:
			p.update(p1)
		if len(args) >= 1 and isinstance(args[0],dict):
			p.update(args[0])
		d = self.getActionData(widget, desc, *args)
		if d:
			p.update(d)
		opts['params'] = p
		d = {
			'widgettype' : 'urlwidget',
			'options': opts
		}

		def doit(target:Widget, add_mode:str, o, w:Widget):
			if isinstance(w, ModalView):
				return

			if target and not w.parent:
				if add_mode == 'replace':
					target.clear_widgets()
				target.add_widget(w)

		def doerr(o,e):
			Logger.info('Block: urlwidgetAction(): desc=%s widgetBuild error'
								,str(desc))

		b = Blocks()
		b.bind(on_built=partial(doit,target,add_mode))
		b.bind(on_failed=doerr)
		b.widgetBuild(d)
			
	def getActionData(self, widget:Widget, desc, *args):
		data = {}
		rtdesc = self.build_rtdesc(desc)
		if rtdesc:
			rt = self.get_rtdata(widget, rtdesc, *args)
			if rt:
				data.update(rt)
			if desc.get('keymapping'):
				data = keyMapping(data, desc.get('keymapping'))
		Logger.info('getActionData():rtdesc=%s, data=%s', rtdesc, data)
		return data

	def registedfunctionAction(self, widget:Widget, desc, *args):
		target = self.get_target(widget, desc)
		rf = RegisterFunction()
		name = desc.get('rfname')
		func = rf.get(name)
		if func is None:
			Logger.info('Block: desc=%s rfname(%s) not found', 
						str(desc), name)
			raise Exception('rfname(%s) not found' % name)

		params = desc.get('params',{}).copy()
		d = self.getActionData(widget,desc, *args)
		if d:
			params.update(d)
		func(target, *args, **params)

	def scriptAction(self, widget:Widget, desc, *args):
		script = desc.get('script')
		if not script:
			Logger.info('Block: scriptAction():desc(%s) target not found',
							str(desc))
			return 
		target = self.get_target(widget, desc)
		d = self.getActionData(widget,desc, *args)
		ns = {
			"self":target,
			"args":args,
			"kwargs":d
		}
		if d:
			ns.update(d)
		try:
			self.eval(script, ns)
		except Exception as e:
			print_exc()
			print(e)

	def build_rtdesc(self, desc):
		rtdesc = desc.get('rtdata')
		if not rtdesc:
			if desc.get('datawidget'):
				rtdesc = {}
				rtdesc['target'] = desc['datawidget']
				if desc.get('datascript'):
					rtdesc['script'] = desc.get('datacript')
				else:
					rtdesc['method'] = desc.get('datamethod', 'getValue')
				rtdesc['kwargs'] = desc.get('datakwargs', {})
		return rtdesc

	def get_rtdata(self, widget:Widget, desc, *args):
		"""
		desc descript follow attributes
		{
			"target", a target name from widget
			"method", a method name, default is 'getValue',
			"script", script to handle the data
			"kwargs":" a dict arguments, default is {}
		}
		"""
		
		if desc is None or desc == {}:
			print('get_rtdata():desc is None')
			return {}
		kwargs = desc.get('kwargs', {})
		if not isinstance(kwargs, dict):
			kwargs = {}
		w = None
		if len(args) > 0:
			w = args[0]
		target = desc.get('target')
		if target:
			# w = Blocks.getWidgetById(target, from_widget=widget)
			w = Blocks.findWidget(target, from_widget=widget)
		if w is None:
			print('get_rtdata():w is None', desc)
			return {}
		script = desc.get('script')
		if script:
			ns = {
				"self":w,
				"args":args,
				"kwargs":kwargs
			}
			d = self.eval(script, ns)
			return d

		method = desc.get('method', 'getValue')
		if not hasattr(w, method):
			print('get_rtdata():method is None', desc, type(w))
			return {}
		f = getattr(w, method)
		try:
			r = f(**kwargs)
			if isinstance(r, dict):
				return r
			if isinstance(r, DictObject):
				return r.to_dict()
			print('get_rtdata():method return is not dict', desc, 'ret=', r, type(r))
			return {}
		except:
			print_exc()
			return {}

	def methodAction(self, widget:Widget, desc, *args):
		method = desc.get('method')
		target = self.get_target(widget, desc)
		if target is None:
			Logger.info('Block: methodAction():desc(%s) target not found',
							str(desc))
			return
		if method is None:
			Logger.info('Block: methodAction():desc(%s) method not found',
							str(desc))
			return
		if hasattr(target,method):
			f = getattr(target, method)
			kwargs = desc.get('options',{}).copy()
			d = self.getActionData(widget,desc, *args)
			if d:
				kwargs.update(d)
			f(*args, **kwargs)
		else:
			alert('%s method not found' % method)

	def widgetBuild(self, desc):
		"""
		desc format:
		{
			widgettype:<registered widget>,
			id:widget id,
			options:{}
			subwidgets:[
			]
			binds:[
			]
		}
		"""
		def doit(desc):
			if isinstance(desc,DictObject):
				desc = desc.to_dict()
			if not isinstance(desc,dict):
				Logger.info('Block: desc(%s) must be a dict object(%s)',
							desc,type(desc))
				return None

			# desc = self.valueExpr(desc)
			try:
				widget = self.w_build(desc)
				self.dispatch('on_built',widget)
				if hasattr(widget,'ready'):
					widget.ready = True
				return widget
			except Exception as e:
				print_exc()
				self.dispatch('on_failed',e)
				return None

		if isinstance(desc,DictObject):
			desc = desc.to_dict()
		if not isinstance(desc, dict):
			print('widgetBuild1: desc must be a dict object',
						desc,type(desc))
			self.dispatch('on_failed',Exception('miss url'))
			return

		widgettype = desc.get('widgettype')
		while widgettype == "urlwidget":
			opts = desc.get('options',{}).copy()
			extend = desc.get('extend')
			addon = None
			if desc.get('extend'):
				addon = desc.get('extend').copy()
			url = opts.get('url')
			if url is None:
				self.dispatch('on_failed',Exception('miss url'))
				return
			
			if opts.get('url'):
				del opts['url']
			rtdesc = self.build_rtdesc(opts)
			if rtdesc:
				rtdata = self.get_rtdata(None, rtdesc)
				params = opts.get('params', {})
				params.update(rtdata)
				opts['params'] = params

			desc = self.getUrlData(url,**opts)
			if not (isinstance(desc, DictObject) or \
							isinstance(desc, dict)):
				print('Block2: desc must be a dict object',
								desc,type(desc))
				self.dispatch('on_failed',Exception('miss url'))
				return

			if addon:
				desc = dictExtend(desc,addon)
			widgettype = desc.get('widgettype')
		if widgettype is None:
			print('Block3: desc must be a dict object not None')
			return None
		return doit(desc)
	
	@classmethod
	def findWidget(self, id:str, from_widget:Widget=None) -> Widget:
		"""
		-:find up direct, find widget in ancestor
		+ or empty: find down direct, find widget in descendant
		@:find widget by class
		$ or empty:find widget by id
		.:more than one step.

		"""
		def find_widget_by_id(id, from_widget):
			if id=='self':
				return from_widget
			if hasattr(from_widget,'widget_id'):
				if from_widget.widget_id == id:
					return from_widget
			if hasattr(from_widget, id):
				w = getattr(from_widget,id)
				return w
			return None

		def find_widget_by_class(klass, from_widget):
			if from_widget.__class__.__name__ == klass:
				return from_widget
			for k, v in from_widget.__dict__.items():
				if isinstance(v, Widget):
					if v.__class__.__name__ == klass:
						return v
			return None
		
		def _find_widget(name, from_widget, dir='down', 
					find_func=find_widget_by_id):
			w = find_func(name, from_widget)
			if w:
				return w
			if dir == 'down':
				children = [i for i in from_widget.children]
				if hasattr(from_widget, 'get_subwidgets'):
					children = from_widget.get_subwidgets()
				Logger.info('children=%s', str(children))
				for c in children:
					ret = _find_widget(name, from_widget=c, dir=dir)
					if ret:
						return ret
			else:
				if isinstance(from_widget, WindowBase):
					return None
				if from_widget.parent:
					return _find_widget(name, 
								from_widget=from_widget.parent,
								dir=dir)
			Logger.info('Block:_find_widget(), %s, %s %s return None',
						name, from_widget.__class__.__name__, dir)
			return None

		def find_widget(step, from_widget):
			dir = 'down'
			if step[0:1] == '-':
				dir = 'up'
				step = step[1:]
			find_func = find_widget_by_id
			if step[0:1] == '@':
				step = step[1:]
				find_func = find_widget_by_class
			return _find_widget(step, from_widget=from_widget, 
						dir=dir, find_func=find_func)

		steps = id.split('.')
		w = from_widget
		for i, s in enumerate(steps):
			if i==0:
				app = App.get_running_app()
				fid = s
				if fid == '/self' or fid == 'root':
					w = app.root
					if len(steps) == 1:
						return from_widget
					continue
				if fid == 'Window':
					w = Window
					if len(steps) == 1:
						return w
					continue
				if fid == 'app':
					return app

			w = find_widget(s, w)
			if not w:
				return None
		return w
			
	@classmethod
	def getWidgetById(self, id:str, from_widget:Widget=None) -> Widget:
		return Blocks.findWidget(id, from_widget=from_widget)

	def on_built(self,v=None):
		return

	def on_failed(self,e=None):
		return

	def buildKlass(self, desc):
		"""
		desc = {
			"classname":"MyClass",
			"base":["Box", "WidgetReady"],
			"properties":[
				{
					"name":"aaa",
					"type":"str",
					"default":1
				}
			]
			"subwidgets":[
			],
			
		"""
		codes = """
{% for b in bases %}
{{b}} = Factory.{{b}}
{% endfor %}

class {{ classname }}({% for b in bases -%}{{b}}{% endfor %})
{% for p in properties %}
	{{p.name}} {{p.type}}({{p.default}})
{% endfor %}
	def __init__(self, **kw):
		super({{classname}}, self).__init__(**kw)

"""

Factory.register('Blocks',Blocks)
Factory.register('Video',Video)
Factory.register('OrientationLayout', OrientationLayout)
