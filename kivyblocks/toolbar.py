from kivy.logger import Logger
from kivy.graphics import Color, Rectangle
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import AsyncImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import StringProperty, DictProperty, \
			ListProperty, NumericProperty

from appPublic.dictObject import DictObject
from appPublic.registerfunction import RegisterFunction

from .widgetExt.scrollwidget import ScrollWidget
from .utils import *
from .ready import WidgetReady
from .color_definitions import getColors
from .baseWidget import Text, Box
from .scrollpanel import ScrollPanel
from .toggleitems import ToggleItems

class ScrollToolbar(ScrollPanel):
	"""
	tool has the follow attributes
	{
		"name",
		"source_on,
		"source_off,
		# source_on, source_off, or "img_src",
		"label",
		"deletable"
		"url",
		"rfname",
	}
	toolbar has follow attributes
	{
		"padding_c":x spacing
		"img_size_c":image height in charecter size
		"text_size_c":
		"toolbar_orient":"H" or "V"
		"tool_orient":"horizontal" or "vertical"
		"css_on",
		"css_off",
		"tools":
	}
	"""

	css_on = StringProperty('default')
	css_off = StringProperty('default')
	tools = ListProperty([])
	tool_orient = StringProperty('horizontal')
	toolbar_orient = StringProperty('H')
	padding_c = NumericProperty(1)
	img_size_c = NumericProperty(2)
	text_size_c = NumericProperty(1)

	def __init__(self, **kw):
		SUPER(ScrollToolbar, self, kw)
		self.register_event_type('on_press')
		if self.toolbar_orient == 'H':
			self._inner.orientation = 'horizontal'
		else:
			self._inner.orientation = 'vertical'
		self.clear_widgets()
		self.w_dic = {}
		for t in self.tools:
			self.add_tool(t)
		
		self.bar_width = 0
		if self.toolbar_orient == 'H':
			self.do_scroll_y = False
			self._inner.spacing = CSize(self.padding_c,0)
		else:
			self.do_scroll_x = False
			self._inner.spacing = CSize(0, self.padding_c)

	def on_children_size(self, o, size):
		self.on_size(None, None)

	def on_size(self, o, size):
		print('on_size=', size)
		if self.toolbar_orient == 'H':
			self.size_hint_x = 1
			self.size_hint_y = None
			if len(self.w_dic.keys()) > 0:
				self.height = max([w.height for w in self.w_dic.keys()])
			self._inner.spacing = CSize(self.padding_c,0)
		else:
			self.size_hint_x = None
			self.size_hint_y = 1
			if len(self.w_dic.keys()) > 0:
				self.width = max([w.width for w in self.w_dic.keys() ])
			self._inner.spacing = CSize(0, self.padding_c)
		print('###size_hint=',
			self.size_hint_x,
			self.size_hint_y,
			self.size_hint, 
			self.size)
		
	def add_tool(self, t):
		label = t.get('label', t.get('name', None))
		source_on = t.get('source_on', t.get('img_src',None))
		source_off = t.get('source_off', t.get('img_src', None))
		ToggleIconText = Factory.ToggleIconText
		ToggleText = Factory.ToggleText
		ToggleImage = Factory.ToggleImage
		if label and source_on:
			w = ToggleIconText(css_on=self.css_on,
							css_off=self.css_off,
							text=label,
							size_hint = (None, None),
							fontsize=self.text_size_c,
							source_on=source_on,
							source_off=source_off,
							orientation=self.tool_orient,
							img_kw={
								"size_hint":(None, None),
								"height":CSize(self.img_size_c),
								"width":CSize(self.img_size_c)
							}
			)
		elif label:
			w = ToggleText(css_on=self.css_on,
							css_off=self.css_off,
							size_hint = (None, None),
							orientation=self.tool_orient,
							fontsize=CSize(self.text_size_c),
							text=label)
		elif source_on:
			w = ToggleImage( source_on=source_on,
							source_off=source_off,
							size_hint = (None, None),
							orientation=self.tool_orient,
							img_kw={
								"size_hint":(None, None),
								"height":CSize(self.img_size_c),
								"width":CSize(self.img_size_c)
							}
			)

		if w:
			self.add_widget(w)
			self.w_dic[w] = t
			w.select(False)
			w.bind(size=self.on_children_size)
			w.bind(on_press=self.tool_press)
			w.bind(minimum_width=w.setter('width'))
			w.bind(minimum_height=w.setter('height'))

	def del_tool(self, name):
		m = [ x for x,y in self.w_dic.items() if y['name'] == name ]
		for w in m:
			self.remove(w)
		self.w_dic = {k:v for k,v in self.w_dic.copy().items() \
						if k not in m }
		
	def on_press(self, o):
		pass

	def select(self,name):
		for w, v in self.w_dic.items():
			if v['name'] == name:
				w.select(True)
				self.tool_press(w)
				break

	def tool_press(self, o):
		for w,v in self.w_dic.items():
			if w == o:
				ret_v = v
				w.select(True)
			else:
				w.select(False)
		self.dispatch('on_press', ret_v)

class ToolPage(Box):
	"""
	ToolPage:
	{
		toolbar_size:
		tool_at
		toolbar
	}
	"""
	toolbar_size = NumericProperty(2)
	tool_at = StringProperty('top')
	toolbar = DictProperty({})
	def __init__(self, **kw):
		print('ToolPage:kw=',kw)
		SUPER(ToolPage, self, kw)
		if self.tool_at in [ 'top','bottom']:
			self.orientation = 'vertical'
		else:
			self.orientation = 'horizontal'
		if not self.toolbar_size:
			self.toolbar_size = self.img_size + self.text_size + 0.3
		self.content_widgets = {}
		self.content_w = None
		self.toolbar_w = None
		self.init()
		name = self.toolbar['tools'][0]['name']
		self.toolbar_w.select(name)
	
	def add_tool(self, tool):
		self.toolbar_w.add_tool(tool)

	def del_tool(self, name):
		self.toolbar_w.del_tool(o)
		g = self.content_widgets.copy()
		self.content_widgets = {k:v for k,v in g.items()}

	def on_size(self,obj,size):
		if self.content_w is None:
			return
		if self.tool_at in ['top','bottom']:
			self.toolbar_w.size_hint_y = None
			self.content_w.height = self.height - self.toolbar_w.height
		else:
			self.toolbar_w.size_hint_x = None
			self.content_w.width = self.width - self.toolbar_w.width

	def init(self):
		self.content_w = BoxLayout()
		self.content_w.widget_id = 'content'
		self.toolbar_w = ScrollToolbar(**self.toolbar)
		if self.tool_at in ['top','left']:
			self.add_widget(self.toolbar_w)
			self.add_widget(self.content_w)
		else:
			self.add_widget(self.content_w)
			self.add_widget(self.toolbar_w)
		
		self.toolbar_w.bind(on_press=self.on_press_handle)

	def build_widget(self, url):
		desc = {
			"widgettype":"urlwidget",
			"options":{
				"url":url
			}
		}
		b = Factory.Blocks()
		return b.widgetBuild(desc)

	def print_all(self):
		self.print_info(self)
		self.print_info(self.toolbar_w)
		for w in self.toolbar_w.w_dic.keys():
			self.print_info(w)
			for c in w.children:
				self.print_info(c)
		self.print_info(self.content_w)
		for c in self.content_w.children:
			self.print_info(c)

	def print_info(self, o):
		print('self.size_hint=', o.__class__, o.size_hint, 
				'self.x,y=', o.width, o.height)
		
	def on_press_handle(self, o, v):
		name = v.get('name')
		refresh = v.get('refresh', False)
		self.print_all()
		w = self.content_widgets.get(name)
		self.content_w.clear_widgets()
		if w and not refresh:
			self.content_w.add_widget(w)
			return
		url = v.get('url')
		if url:
			w = self.build_widget(url)
			if w:
				self.content_widgets[name] = w
				self.content_w.add_widget(w)
				print('w=', w)
			return
		rfname = v.get('rfname')
		if rfname:
			rf = RegisterFunction()
			f = rf.get(rfname)
			if f:
				r = f()
				if isinstance(r,Widget):
						self.content_w.add_widget(r)

Factory.register('ScrollToolbar', ScrollToolbar)
Toolbar = ScrollToolbar
