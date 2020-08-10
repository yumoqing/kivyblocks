import os
import sys
import codecs
import json
from traceback import print_exc

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
from .qrcodereader import QRCodeReader

def showError(e):
	print('error',e)

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
		body="""def %s(widget,obj=None, v=None):
	jsonstr='''%s'''
	desc = json.loads(jsonstr)
	app = App.get_running_app()
	app.blocks.uniaction(widget, desc)
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
		for  k,v in g.items():
			if isinstance(k,str):
				print('k=',k)
				if k=='get_playerid':
					print('s=',s)
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
		else:
			h = HTTPDataHandler(url,method=method,params=params,
					files=files)
			h.bind(on_success=callback)
			h.bind(on_error=errback)
			h.handle()

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

	def __build(self,desc:dict,ancestor=None):
		def checkReady(w,o):
			w.children_ready[o] = True
			if all(w.children_ready.values()):
				w.ready = True
		widgetClass = desc.get('widgettype',None)
		if not widgetClass:
			print("__build(), desc invalid", desc)
			raise Exception(desc)

		widgetClass = desc['widgettype']
		opts = desc.get('options',{})
		widget = None
		try:
			klass = Factory.get(widgetClass)
			widget = klass(**opts)
			if desc.get('parenturl'):
				widget.parenturl = desc.get('parenturl')
				ancestor = widget
		except Exception as e:
			print('Error:',widgetClass,'not registered')
			print_exc()
			raise NotExistsObject(widgetClass)

		if desc.get('id'):
			myid = desc.get('id')
			holder = ancestor
			if myid[0] == '/':
				myid = myid[1:]
				app = App.get_running_app()
				holder = app.root

			if ancestor == widget:
				app = App.get_running_app()
				holder = app.root

			if not hasattr(holder,'widget_ids'):
				setattr(holder,'widget_ids',{})

			holder.widget_ids[myid] = widget
		
		widget.build_desc = desc
		self.build_rest(widget,desc,ancestor)
		return widget
		
	def build_rest(self, widget,desc,ancestor,t=None):
		bcnt = 0
		btotal = len(desc.get('subwidgets',[]))
		def doit(self,widget,bcnt,btotal,desc,o,w):
			bcnt += 1
			if hasattr(widget,'parenturl'):
				w.parenturl = widget.parenturl
			widget.add_widget(w)
			if hasattr(widget,'addChild'):
				widget.addChild(w)
			if bcnt >= btotal:
				for b in desc.get('binds',[]):
					self.buildBind(widget,b)

		def doerr(o,e):
			raise e

		f = partial(doit,self,widget,bcnt,btotal,desc)
		for sw in desc.get('subwidgets',[]):
			b = Blocks()
			b.bind(on_built=f)
			b.bind(on_failed=doerr)
			b.widgetBuild(sw, ancestor=ancestor)

		if btotal == 0:
			for b in desc.get('binds',[]):
				self.buildBind(widget,b)

	def buildBind(self,widget,desc):
		wid = desc.get('wid','self')
		w = self.getWidgetByIdPath(widget,wid)
		event = desc.get('event')
		if event is None:
			return
		f = self.buildAction(widget,desc)
		w.bind(**{event:f})
	
	def uniaction(self,widget,desc):
		acttype = desc.get('actiontype')
		if acttype=='blocks':
			return self.blocksAction(widget,desc)
		if acttype=='urlwidget':
			return self.urlwidgetAction(widget,desc)
		if acttype == 'registedfunction':
			return self.registedfunctionAction(widget,desc)
		if acttype == 'script':
			return self.scriptAction(widget, desc)
		if acttype == 'method':
			return self.methodAction(widget, desc)
		alert("actiontype(%s) invalid" % acttype,title='error')

	def blocksAction(self,widget,desc):
		target = self.getWidgetByIdPath(widget, desc.get('target','self'))
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
		b.widgetBuild(opts,ancestor=widget)
		
	def urlwidgetAction(self,widget,desc):
		target = self.getWidgetByIdPath(widget, desc.get('target','self'))
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
		b.widgetBuild(d,ancestor=widget)
			
	def getActionData(self,widget,desc):
		data = {}
		if desc.get('datawidget',False):
			dwidget = self.getWidgetByIdPath(widget,
							desc.get('datawidget'))
			data = dwidget.getData()
			if desc.get('keymapping'):
				data = keyMapping(data, desc.get('keymapping'))
		return data

	def registedfunctionAction(self, widget, desc):
		rf = RegisterFunction()
		name = desc.get('rfname')
		func = rf.get(name)
		if func is None:
			print('rfname(%s) not found' % name,rf.registKW)
			raise Exception('rfname(%s) not found' % name)

		params = desc.get('params',{})
		d = self.getActionData(widget,desc)
		params.update(d)
		func(**params)

	def scriptAction(self, widget, desc):
		script = desc.get('script')
		if not script:
			return 
		target = self.getWidgetByIdPath(widget, desc.get('target','self'))
		d = self.getActionData(widget,desc)
		ns = {
			"self":target
		}
		ns.update(d)	
		self.eval(script, ns)
	
	def methodAction(self, widget, desc):
		method = desc.get('method')
		target = self.getWidgetByIdPath(widget, desc.get('target','self'))
		if hasattr(target,method):
			f = getattr(target, method)
			kwargs = desc.get('options',{})
			d = self.getActionData(widget,desc)
			kwargs.update(d)
			f(**kwargs)
		else:
			alert('%s method not found' % method)

	def widgetBuild(self,desc,ancestor=None):
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
				widget = self.__build(desc,ancestor=ancestor)
				self.dispatch('on_built',widget)
			except Exception as e:
				print_exc()
				doerr(None,e)
				return

		def doerr(o,e):
			self.dispatch('on_failed',e)

		name = desc['widgettype']
		if name == 'urlwidget':
			opts = desc.get('options')
			parenturl = None
			url=''
			if ancestor:
				parenturl = ancestor.parenturl
			try:
				url = absurl(opts.get('url'),parenturl)
			except Exception as e:
				self.dispatch('on_failed',e)
			
			def cb(o,d):
				try:
					d['parenturl'] = url
					doit(d)
				except Exception as e:
					doerr(None,e)

			del opts['url']
			self.getUrlData(url,callback=cb,errback=doerr,**opts)
			return
		doit(desc)
	
	def getWidgetByIdPath(self,widget,path):
		ids = path.split('/')
		if ids[0] == '':
			app = App.get_running_app()
			widget = app.root
			ids = ids[1:]
		for id in ids:
			if id == 'self':
				return widget
			if not hasattr(widget, 'widget_ids'):
				print('widget not found,path=',path,'id=',id,'ids=',ids)
				raise WidgetNotFoundById(id)
				
			widget = widget.widget_ids.get(id,None)
			if widget is None:
				print('widget not found,path=',path,'id=',id,'ids=',ids)
				raise WidgetNotFoundById(id)
		return widget
	
	def on_built(self,v=None):
		return

	def on_failed(self,e=None):
		return

Factory.register('Blocks',Blocks)
Factory.register('Video',Video)
