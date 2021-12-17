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

"""
toolbar options
{
	radius:
	"mode":"icon", "icontext","text"
	img_size=1.5,	
	text_size=0.5,
	tools:[
		{
			"name":"myid",
			"img_src":"gggggg",
			"label":"gggggg"
		},
		...
	]
}
"""
class Toolbar(Box):
	def __init__(self, 
				radius=[],
				img_size=1.5,
				text_size=0.5,
				tools=[], 
				normal_css="default",
				actived_css="default",
				**opts):
		self.radius = radius
		self.img_size = img_size
		self.text_size = text_size
		self.tools = tools
		self.tool_widgets={}
		Box.__init__(self, **opts)
		self.register_event_type('on_press')
		first = True
		subs_desc = []
		for opt in self.tools:
			subwidgets = []
			img_src = opt.get('img_src',None)
			if img_src:
				subwidgets.append({
					"widgettype":"AsyncImage",
					"options":{
						"size_hint_y":None,
						"height":CSize(self.img_size),
						"source":img_src
					}
				})
			text = opt.get('label', None)
			if text:
				subwidgets.append({
					"widgettype":"Text",
					"options":{
						"size_hint_y":None,
						"i18n":True,
						"height":CSize(self.text_size),
						"fontsize":CSize(self.text_size),
						"otext":text
					}
				})
			desc = {
				"widgettype":"VBox",
				"options":{
				},
				"subwidgets":subwidgets,
				"data":opt.get('name')
			}
			subs_desc.append(desc)

		self.toggle_items = ToggleItems(
				radius=self.radius,
				unit_size=self.img_size + self.text_size,
				items_desc=subs_desc,
				normal_css=normal_css,
				actived_css=actived_css,
				**opts
				)
		for ti in self.toggle_items.item_widgets:
			ti.widget_id = ti.user_data
		self.toggle_items.bind(on_press=self.tool_press)
		self.add_widget(self.toggle_items)

	def on_press(self, o):
		print('on_press(),', o)

	def tool_press(self,o,v=None):
		self.dispatch('on_press',self.toggle_items.getValue())

"""
Toolpage options
{
	img_size:1.5,	
	text_size:0.7,
	tool_at:"left","right","top","bottom",
	radius:
	"show_name":"default open tool's name"
	tools:[
		{
			"name":"myid",
			"img_src":"gggggg",
			"label":"gggggg"
			"fresh":true
			"url":"ggggggggg"
			"rfname":"register_function_name"
		},
		...
	]
	
"""

class ScrollToolbar(ScrollPanel):
	"""
	tool has the follow attributes
	{
		"name",
		"source_on,
		"source_off,
		"label",
	}
	toolbar has follow attributes
	{
		"padding_c":x spacing
		"img_size_c":image height in charecter size
		"text_size_c":
		"orient":"H" or "V"
		"tool_orient":"horizontal" or "vertical"
		"css_on",
		"css_off",
		"tools":
	}
				css_on='default',
				css_off='default',
				tools=[],
				tool_orient = 'horizontal',
				orient='H',
				padding_c=1,
				img_size_c=2,
				text_size_c=1,
		self.css_on = css_on
		self.css_off = css_off
		self.tools=tools
		self.tool_orient = tool_orient
		self.orient = orient
		self.padding_c = padding_c
		self.img_size_c = img_size_c
		self.text_size_c = text_size_c
	"""

	css_on = StringProperty('default')
	css_off = StringProperty('default')
	tools = ListProperty([])
	tool_orient = StringProperty('horizontal')
	orient = StringProperty('H')
	padding_c = NumericProperty(1)
	img_size_c = NumericProperty(2)
	text_size_c = NumericProperty(1)
	def __init__(self, **kw):
		kwarg_pop(self, kw)
		super(ScrollToolbar, self).__init__(**kw)
		self.register_event_type('on_press')
		if self.orient == 'H':
			self._inner.orientation = 'horizontal'
		else:
			self._inner.orientation = 'vertical'
		self.clear_widgets()
		self.w_dic = {}
		for t in self.tools:
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
								fontsize=CSize(self.text_size_c),
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
								orientation=self.tool_orient,
								fontsize=CSize(self.text_size_c),
								text=label)
			elif source_on:
				w = ToggleImage( source_on=source_on,
								source_off=source_off,
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
				w.bind(on_press=self.tool_press)
		
		if self.orient == 'horizontal':
			self.do_scroll_y = False
			self.size_hint_y = None
			if len(self.w_dic.keys()) > 0:
				self.height = max([w.height for w in self.w_dic.keys()])
			self._inner.spacing = CSize(self.padding_c,0)
		else:
			self.do_scroll_x = False
			self.size_hint_x = None
			if len(self.w_dic.keys()) > 0:
				self.width = max([w.width for w in self.w_dic.keys() ])
			self._inner.spacing = CSize(0, self.padding_c)

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

class ToolPage(BoxLayout):
	toolbar_size = NumericProperty(2)
	tool_at = StringProperty('top')
	toolbar = DictProperty({})
	def __init__(self, **kw):
		print('ToolPage:kw=',kw)
		super(ToolPage, self).__init__(**kw)
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
	
	def on_size(self,obj,size):
		if self.content_w is None:
			return
		if self.tool_at in ['top','bottom']:
			self.toolbar_w.width = self.width
			self.content_w.width = self.width
			self.content_w.height = self.height - self.toolbar_w.height
		else:
			self.toolbar_w.height = self.height
			self.content_w.height = self.height
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

	def on_press_handle(self, o, v):
		name = v.get('name')
		fress = v.get('fress')
		w = self.content_widgets.get(name)
		self.content_w.clear_widgets()
		if w is None or fresh:
			url = v.get('url')
			if url:
				w = self.build_widget(url)
				if w:
					self.content_widgets[name] = w
					self.content_w.add_widget(w)
				return
			rfname = v.get('rfname')
			if rfname:
				rf = RegisterFunction()
				f = rf.get(rfname)
				if f:
					r = f()
					if isinstance(r,Widget):
						self.content_w.add_widget(r)
			return
		if w:
			self.content_w.add_widget(w)

Factory.register('ScrollToolbar', ScrollToolbar)
