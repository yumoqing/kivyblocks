import os
import sys
import codecs
import json
from traceback import print_exc

from functools import partial

from appPublic.dictExt import dictExtend
from appPublic.jsonConfig import getConfig
from appPublic.folderUtils import ProgramPath
from appPublic.dictObject import DictObject
from appPublic.Singleton import SingletonDecorator

from kivy.config import Config
from kivy.metrics import sp,dp,mm
from kivy.core.window import WindowBase
from kivy.properties import BooleanProperty
from kivy.uix.widget import Widget
from kivy.app import App
from .baseWidget import *
from .widgetExt import Messager
from .externalwidgetmanager import ExternalWidgetManager
from .threadcall import HttpClient
from .toolbar import *
from .dg import DataGrid
from .utils import *
from .ready import WidgetReady
from .serverImageViewer import ServerImageViewer
from .vplayer import VPlayer
from .form import InputBox, Form, StrSearchForm
from .boxViewer import BoxViewer
from .tree import Tree, TextTree

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

@SingletonDecorator
class RegistedFunction:
	def __init__(self):
		self.rf_list = {}
	
	def register(self,name,func):
		self.rf_list[name] = func

	def get(self,name):
		return self.rf_list.get(name)

def registerWidget(name,widget):
	globals()[name] = widget


class Blocks:
	registedWidgets = {}
	def __init__(self):
		self.action_id = 0
	
	def register_widget(self,name,widget):
		globals()[name] = widget

	def buildAction(self,widget,desc):
		self.action_id += 1
		fname = 'action%d' % self.action_id
		l = {
		}
		body="""def %s(widget,obj=None, v=None):
	jsonstr='''%s'''
	print(type(widget), type(obj),v,'action():desc=',jsonstr)
	desc = json.loads(jsonstr)
	app = App.get_running_app()
	app.blocks.uniaction(widget, desc)
	print('finished')
""" % (fname, json.dumps(desc))
		exec(body,globals(),l)
		f = l.get(fname,None)
		if f is None:
			raise Exception('None Function')
		func =partial(f,widget)
		return func
		setattr(widget,fname,f)
		return getattr(widget,fname)
		
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

		return eval(s,g,l)

	def getUrlData(self,kw,parenturl=None):
		url = kw.get('url')
		method = kw.get('method','GET')
		params = kw.get('params',{})
		if url is None:
			print('kw=',kw)
			raise ArgumentError('url','getUrlData() miss a url argument')
		url = absurl(url,parenturl)
		if url.startswith('file://'):
			filename = url[7:]
			print(filename)
			with codecs.open(filename,'r','utf-8') as f:
				b = f.read()
				dic = json.loads(b)
		else:
			dic = App.get_running_app().hc(url,method=method,params=params)
		return dic, url

	def strValueExpr(self,s:str,localnamespace:dict={}):
		if not s.startswith('py::'):
			return s
		try:
			v = self.eval(s[4:],localnamespace)
			return v
		except Exception as e:
			if s.startswith('CSize'):
				print('Exception .... ',e,s)
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
		if type(obj) in [ type({}), type(DictObject) ]:
			return self.dictValueExpr(obj,localnamespace)
		return obj

	def __build(self,desc:dict,ancestor=None):
		def checkReady(w,o):
			print('checkReady():w=',w,'o=',o)
			w.children_ready[o] = True
			if all(w.children_ready.values()):
				w.ready = True
		widgetClass = desc.get('widgettype',None)
		if not widgetClass:
			print("__build(), desc invalid", desc)
			raise Exception(desc)

		widgetClass = desc['widgettype']
		opts = desc.get('options',{})
		klass = globals().get(widgetClass)
		if not klass:
			raise NotExistsObject(widgetClass)
		widget = klass(**opts)
		if desc.get('parenturl'):
			widget.parenturl = desc.get('parenturl')
			ancestor = widget

		if desc.get('id'):
			myid = desc.get('id')
			holder = ancestor
			if ancestor == widget:
				app = App.get_running_app()
				holder = app.root
			if not hasattr(holder,'widget_ids'):
				setattr(holder,'widget_ids',{})
			holder.widget_ids[myid] = widget
		
		widget.build_desc = desc
		self.build_rest(widget,desc,ancestor)
		# f = partial(self.build_rest,widget,desc,ancestor)
		# event = Clock.schedule_once(f,0)
		return widget
		
	def build_rest(self, widget,desc,ancestor,t=None):
		for sw in desc.get('subwidgets',[]):
			w = self.widgetBuild(sw, ancestor=ancestor)
			if w is None:
				continue
			w.parenturl = widget.parenturl
			widget.add_widget(w)
			if hasattr(widget,'addChild'):
				widget.addChild(w)
		for b in desc.get('binds',[]):
			self.buildBind(widget,b)
		if hasattr(widget, 'built'):
			widget.built()

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
		alert(msg="actiontype invalid",title=acttype)

	def blocksAction(widget,desc):
		target = self.getWidgetByIdPath(widget, desc.get('target','self'))
		add_mode = desc.get('mode','replace')
		opts = desc.get('options')
		d = self.getActionData(widget,desc)
		p = opts.get('options',{})
		p.update(d)
		opts['options'] = p
		x = self.widgetBuild(opts,ancestor=widget)
		if x is None:
			alert(str(opts), title='widugetBuild error')
			return 
		if add_mode == 'replace':
			target.clear_widgets()
		target.add_widget(x)
		
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
		x = self.widgetBuild(d,ancestor=widget)
		if x is None:
			return 
		if add_mode == 'replace':
			target.clear_widgets()
		target.add_widget(x)
			
	def getActionData(self,widget,desc):
		data = {}
		if desc.get('datawidget',False):
			dwidget = self.getWidgetByIdPath(widget,
							desc.get('datawidget'))
			data = dwidget.getData()
		return data

	def registedfunctionAction(self, widget, desc):
		rf = RegistedFunction()
		name = desc.get('rfname')
		func = rf.get(name)
		params = desc.get(params,{})
		d = self.getActionData(widget,desc)
		params.update(d)
		func(params)

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
		name = desc['widgettype']
		if name == 'urlwidget':
			opts = desc.get('options')
			parenturl = None
			if ancestor:
				parenturl = ancestor.parenturl
			desc, parenturl = self.getUrlData(opts,parenturl)
			if not isinstance(desc,dict):
				print("getUrlData() return error data",opts,parenturl)
				# alert(str(desc) + 'format error',title='widgetBuild()')
				return None
			desc = self.valueExpr(desc)
			desc['parenturl'] = parenturl
			
		try:
			widget = self.__build(desc,ancestor=ancestor)
			return widget
		except:
			print('widgetBuild() Error',desc)
			print_exc()
			alert(str(desc))
			return None
	
	def getWidgetByIdPath(self,widget,path):
		ids = path.split('/')
		if ids[0] == '':
			app = App.get_running_app()
			widget = app.root
			ids = ids[1:]
		for id in ids:
			if id == 'self':
				return widget
			widget = widget.widget_ids.get(id,None)
			if widget is None:
				print('widget not found,path=',path,'id=',id,'ids=',ids)
				raise WidgetNotFoundById(id)
		return widget
	
