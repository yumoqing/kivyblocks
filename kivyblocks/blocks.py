import os
import sys
import codecs
import json
from traceback import print_exc

import kivy
from functools import partial

from appPublic.dictExt import dictExtend
from appPublic.folderUtils import ProgramPath
from appPublic.dictObject import DictObject
from appPublic.Singleton import SingletonDecorator, GlobalEnv
from appPublic.datamapping import keyMapping
from appPublic.registerfunction import RegisterFunction

from kivy.config import Config
from kivy.metrics import sp,dp,mm
from kivy.core.window import WindowBase
from kivy.properties import BooleanProperty
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.factory import Factory
from kivy.uix.video import Video
from .baseWidget import *
from .toolbar import *
from .dg import DataGrid
from .utils import *
from .serverImageViewer import ServerImageViewer
from .vplayer import VPlayer
from .form import InputBox, Form, StrSearchForm
from .boxViewer import BoxViewer
from .tree import Tree, TextTree
from .newvideo import Video
# from .qrcodereader import QRCodeReader
from .ready import WidgetReady
from .bgcolorbehavior import BGColorBehavior
from .orientationlayout import OrientationLayout
from kivyblocks import doubleface

def showError(e):
	print('error',e)


def wrap_ready(klass):
	try:
		w = Factory.get(klass)
		if hasattr(w,'ready'):
			return w
		Factory.unregister(klass)
		globals()[klass] = w
	except:
		w = globals().get(klass)
		if w is None:
			return None
		if hasattr(w,'ready'):
			return w
		
	script = f"""class R_{klass}(WidgetReady, {klass}):
	def __init__(self, **kw):
		{klass}.__init__(self, **kw)
		WidgetReady.__init__(self)
""" 
	exec(script,globals(),globals())
	newWidget = globals().get(f'R_{klass}')
	Factory.register(klass,newWidget)
	return newWidget

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
	def __init__(self,name):
		super().__init__()
		self.widget_name = name

	def __str__(self):
		s = 'not reigsted widget(%s)' % self.name
		return s
	
	def __expr__(self):
		return self.__str__()

def registerWidget(name,widget):
	globals()[name] = widget


class Blocks(EventDispatcher):
	def __init__(self):
		EventDispatcher.__init__(self)
		self.action_id = 0
		self.register_event_type('on_built')
		self.register_event_type('on_failed')
		self.env = GlobalEnv()

	def set(self,k,v):
		self.env[k] = v
	
	def register_widget(self,name,widget):
		globals()[name] = widget

	def buildAction(self,widget,desc):
		self.action_id += 1
		fname = 'action%d' % self.action_id
		l = {
		}
		body="""def %s(widget,obj=None, *args):
	jsonstr='''%s'''
	desc = json.loads(jsonstr)
	blocks = Blocks()
	blocks.uniaction(widget, desc,*args)
""" % (fname, json.dumps(desc))
		exec(body,globals(),l)
		f = l.get(fname,None)
		if f is None:
			raise Exception('None Function')
		func =partial(f,widget)
		return func
		
	def eval(self,s,l):
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

		g['__builtins__'] = globals()['__builtins__'].copy()
		g['__builtins__']['__import__'] = None
		g['__builtins__']['__loader__'] = None
		g['__builtins__']['open'] = None
		g.update(self.env)
		return eval(s,g,l)

	def getUrlData(self,url,method='GET',params={}, files={},
					callback=None,
					errback=None,**kw):

		if url.startswith('file://'):
			filename = url[7:]
			with codecs.open(filename,'r','utf-8') as f:
				b = f.read()
				dic = json.loads(b)
				callback(None,dic)
		elif url.startswith('http://') or url.startswith('https://'):
			h = HTTPDataHandler(url,method=method,params=params,
					files=files)
			h.bind(on_success=callback)
			h.bind(on_error=errback)
			h.handle()
		else:
			config = getConfig()
			url = config.uihome + url
			return self.getUrlData(url,method=method,
					params=params,
					files=files,
					callback=callback,
					errback=errback, **kw)

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

	def arrayValueExpr(self,arr:list,localnamespace:dict={}):
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

	def dictValueExpr(self,dic:dict,localnamespace:dict={}):
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
	def valueExpr(self,obj,localnamespace={}):
		if type(obj) == type(''):
			return self.strValueExpr(obj,localnamespace)
		if type(obj) == type([]):
			return self.arrayValueExpr(obj,localnamespace)
		if type(obj) == type({}):
			return self.dictValueExpr(obj,localnamespace)
		if isinstance(obj,DictObject):
			return self.dictValueExpr(obj,localnamespace)
		return obj

	def __build(self,desc:dict):
		# print('__build(),desc=',desc)
		widgetClass = desc.get('widgettype',None)
		if not widgetClass:
			print("__build(), desc invalid", desc)
			raise Exception(desc)

		widgetClass = desc['widgettype']
		opts = desc.get('options',{})
		widget = None
		try:
			klass = wrap_ready(widgetClass)
			widget = klass(**opts)
			if desc.get('parenturl'):
				widget.parenturl = desc.get('parenturl')
		except Exception as e:
			print('Error:',widgetClass,'not registered')
			print_exc()
			raise NotExistsObject(widgetClass)

		if desc.get('id'):
			widget.widget_id = desc.get('id')
		
		widget.build_desc = desc
		self.build_rest(widget,desc)
		return widget
		
	def build_rest(self, widget,desc,t=None):
		bcnt = 0
		btotal = len(desc.get('subwidgets',[]))
		params={
			'blocks':self,
			'bcnt':bcnt,
			'btotal':btotal,
			'desc':desc,
			'widget':widget
		}
		def doit(params,o,w):
			params['bcnt'] += 1
			bcnt = params['bcnt']
			btotal = params['btotal']
			blocks = params['blocks']
			desc = params['desc']
			widget = params['widget']
			if hasattr(widget,'parenturl'):
				w.parenturl = widget.parenturl
			widget.add_widget(w)
			# print('bcnt=',bcnt,'btotal=',btotal,'desc=',desc)
			if bcnt >= btotal:
				for b in desc.get('binds',[]):
					# print('buildBind() called',b)
					blocks.buildBind(widget,b)

		def doerr(o,e):
			raise e

		f = partial(doit,params)
		for sw in desc.get('subwidgets',[]):
			b = Blocks()
			b.bind(on_built=f)
			b.bind(on_failed=doerr)
			b.widgetBuild(sw)

		if btotal == 0:
			for b in desc.get('binds',[]):
				self.buildBind(widget,b)

	def buildBind(self,widget,desc):
		wid = desc.get('wid','self')
		w = Blocks.getWidgetById(desc.get('wid','self'),from_widget=widget)
		event = desc.get('event')
		if event is None:
			return
		f = self.buildAction(widget,desc)
		w.bind(**{event:f})
		# print('w=',w,event,desc)
	
	def uniaction(self,widget,desc, *args):
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
		alert("actiontype(%s) invalid" % acttype,title='error')

	def blocksAction(self,widget,desc, *args):
		target = Blocks.getWidgetById(desc.get('target','self'),widget)
		add_mode = desc.get('mode','replace')
		opts = desc.get('options')
		d = self.getActionData(widget,desc)
		p = opts.get('options',{})
		p.update(d)
		opts['options'] = p
		def doit(target,add_mode,o,w):
			if add_mode == 'replace':
				target.clear_widgets()
			target.add_widget(w)

		def doerr(o,e):
			raise e

		b = Blocks()
		b.bind(on_built=partial(doit,target,add_mode))
		b.bind(on_failed=doerr)
		b.widgetBuild(opts)
		
	def urlwidgetAction(self,widget,desc, *args):
		target = Blocks.getWidgetById(desc.get('target','self'),widget)
		add_mode = desc.get('mode','replace')
		opts = desc.get('options')
		d = self.getActionData(widget,desc)
		p = opts.get('params',{})
		p.update(d)
		opts['params'] = p
		d = {
			'widgettype' : 'urlwidget'
		}
		d['options'] = opts

		def doit(target,add_mode,o,w):
			if add_mode == 'replace':
				target.clear_widgets()
			target.add_widget(w)

		def doerr(o,e):
			raise e

		b = Blocks()
		b.bind(on_built=partial(doit,target,add_mode))
		b.bind(on_failed=doerr)
		b.widgetBuild(d)
			
	def getActionData(self,widget,desc,*args):
		data = {}
		if desc.get('datawidget',False):
			dwidget = Blocks.getWidgetById(desc.get('datawidget','self'),widget)
			if dwidget and hasattr(dwidget,'getData'):
				data = dwidget.getData()
				if desc.get('keymapping'):
					data = keyMapping(data, desc.get('keymapping'))
		return data

	def registedfunctionAction(self, widget, desc, *args):
		target = Blocks.getWidgetById(desc.get('target','self'),widget)
		rf = RegisterFunction()
		name = desc.get('rfname')
		func = rf.get(name)
		if func is None:
			print('rfname(%s) not found' % name,rf.registKW)
			raise Exception('rfname(%s) not found' % name)

		params = desc.get('params',{})
		d = self.getActionData(widget,desc)
		params.update(d)
		# print('registedfunctionAction(),params=',params)
		func(target, *args, **params)

	def scriptAction(self, widget, desc, *args):
		script = desc.get('script')
		if not script:
			return 
		target = Blocks.getWidgetById(desc.get('target','self'),widget)
		d = self.getActionData(widget,desc)
		ns = {
			"self":target,
			"args":args
		}
		ns.update(d)	
		self.eval(script, ns)
	
	def methodAction(self, widget, desc, *args):
		method = desc.get('method')
		target = Blocks.getWidgetById(desc.get('target','self'),widget)
		if hasattr(target,method):
			f = getattr(target, method)
			kwargs = desc.get('options',{})
			d = self.getActionData(widget,desc)
			kwargs.update(d)
			f(*args, **kwargs)
		else:
			alert('%s method not found' % method)

	def widgetBuild(self,desc):
		"""
		desc format:
		{
			widgettype:<registered widget>,
			id:widget id,
			options:
			subwidgets:[
			]
			binds:[
			]
		}
		"""
		def doit(desc):
			# Logger.info("blocks:%s",str(desc))
			desc = self.valueExpr(desc)
			# Logger.info("blocks:%s",str(desc))
			try:
				widget = self.__build(desc)
				self.dispatch('on_built',widget)
				if hasattr(widget,'ready'):
					widget.ready()
			except Exception as e:
				print_exc()
				doerr(None,e)
				return

		def doerr(o,e):
			print('blocks.py:wigetBuild() failed,desc=',desc)
			self.dispatch('on_failed',e)

		name = desc['widgettype']
		if name == 'urlwidget':
			opts = desc.get('options')
			url = opts.get('url')
			if url is None:
				self.dispatch('on_failed',Exception('miss url'))
			
			def cb(o,d):
				try:
					doit(d)
				except Exception as e:
					doerr(None,e)

			if opts.get('url'):
				del opts['url']
			self.getUrlData(url,callback=cb,errback=doerr,**opts)
			return
		doit(desc)
	
	@classmethod
	def getWidgetById(self,id,from_widget=None):
		app = App.get_running_app()
		if id in ['root','/self']:
			return app.root
		if id=='self':
			return from_widget
		if from_widget is None:
			from_widget = app.root
		if hasattr(from_widget,'widget_id'):
			print('Blocks.getWidgetById():widget_id=',
						from_widget.widget_id,'id=',id)
			if from_widget.widget_id == id:
				return from_widget
		for c in from_widget.children:
			ret = Blocks.getWidgetById(id,from_widget=c)
			if ret:
				return ret
		return None

	def on_built(self,v=None):
		return

	def on_failed(self,e=None):
		return

Factory.register('Blocks',Blocks)
Factory.register('Video',Video)
Factory.register('OrientationLayout', OrientationLayout)
