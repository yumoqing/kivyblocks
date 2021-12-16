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
from kivy.properties import StringProperty, ListProperty, NumericProperty

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
						"font_size":CSize(self.text_size),
						"text":text
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
		"img_height_c":image height in charecter size
		"img_width_c":image width in charecter size
		"css_on",
		"css_off",
		"tools":
		"tool_orient"
	}

	"""
	css_on = StringProperty('default')
	css_off = StringProperty('default')
	tools = ListProperty([])
	tool_orient = StringProperty('horizontal')
	img_height_c = NumericProperty(2)
	img_width_c = NumericProperty(2)
	def __init__(self, **kw):
		print('#############init begin##########')
		super(ScrollToolbar, self).__init__(**kw)
		print('#############super init end##########')
		self.register_event_type('on_press')
		self.w_dic = {}
		for t in self.tools:
			label = t.get('label')
			source_on = t.get('source_on', t.get('img_src',None))
			source_off = t.get('source_off', t.get('img_src', None))
			ToggleIconText = Factory.ToggleIconText
			ToggleText = Factory.ToggleText
			ToggleImage = Factory.ToggleImage
			if label and source_on:
				w = ToggleIconText(css_on=self.css_on,
								css_off=self.css_off,
								text=label,
								source_on=source_on,
								source_off=source_off,
								orientation=self.tool_orient,
								img_kw={
									"size_hint":(None, None),
									"height":CSize(self.img_height_c),
									"width":CSize(self.img_width_c)
								}
				)
			elif label:
				w = ToggleText(css_on=self.css_on,
								css_off=self.css_off,
								orientation=self.tool_orient,
								text=label)
			elif source_on:
				w = ToggleImage( source_on=source_on,
								source_off=source_off,
								orientation=self.tool_orient,
								img_kw={
									"size_hint":(None, None),
									"height":CSize(self.img_height_c),
									"width":CSize(self.img_width_c)
								}
				)

			if w:
				self.add_widget(w)
				self.w_dic[w] = t
				w.bind(on_press=self.tool_press)

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
	normal_css=StringProperty(None)
	actived_css=StringProperty(None)
	toolbar_size = NumericProperty(2)
	img_size = NumericProperty(1.5)
	text_size = NumericProperty(0.7)
	tool_at = StringProperty('top')
	tools = ListProperty([])
	def __init__(self, **kw):
		if self.tool_at in [ 'top','bottom']:
			orient = 'vertical'
		else:
			orient = 'horizontal'
		kw['orientation'] = orient
		super(ToolPage, self).__init__(**kw)
		if not self.toolbar_size:
			self.toolbar_size = self.img_size + self.text_size + 0.3
		self.content_widgets = {}
		self.content = None
		self.toolbar = None
		self.init()
		name = self.tools[0]['name']
		self.toolbar.select(name)
	
	def show_page(self, *args):
		toggle_items = self.toolbar.toggle_items
		for c in toggle_items.item_widgets:
			cvalue = c.getValue()
			if cvalue == self.show_name:
				c.dispatch('on_press')

	def on_size(self,obj,size):
		if self.content is None:
			return
		if self.tool_at in ['top','bottom']:
			self.toolbar.width = self.width
			self.content.width = self.width
			self.content.height = self.height - self.toolbar.height
		else:
			self.toolbar.height = self.height
			self.content.height = self.height
			self.content.width = self.width - self.toolbar.width
		print(f'tb-width={self.toolbar.width}')
		print(f'tb-height={self.toolbar.height}')
		print(f'c-height={self.content.height}')
		print(f'c-width={self.content.width}')
		print(f'height={self.height}')
		print(f'width={self.width}')

	def init(self):
		self.initFlag = True
		self.mywidgets = {}
		self.content = BoxLayout()
		self.content.widget_id = 'content'
		opts = {}
		opts['img_height_c'] = self.img_size
		opts['img_width_c'] = self.img_size
		opts['css_on'] = self.actived_css
		opts['css_off'] = self.normal_css
		opts['orient'] = 'H'
		if self.tool_at in ['top','bottom']:
			opts['size_hint_x'] = 1 
			opts['size_hint_y'] = None
			opts['height'] = CSize(self.toolbar_size)
		else:
			opts['size_hint_y'] = 1
			opts['size_hint_x'] = None
			opts['width'] = CSize(self.toolbar_size)
		opts['tools'] = self.tools
		self.toolbar = ScrollToolbar(**opts)
		if self.tool_at in ['top','left']:
			self.add_widget(self.toolbar)
			self.add_widget(self.content)
		else:
			self.add_widget(self.content)
			self.add_widget(self.toolbar)
		
		self.toolbar.bind(on_press=self.on_press_handle)

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
		self.content.clear_widgets()
		if w is None or fresh:
			url = v.get('url')
			if url:
				w = self.build_widget(url)
				if w:
					self.content_widgets[name] = w
					self.content.add_widget(w)
				return
			rfname = v.get('rfname')
			if rfname:
				rf = RegisterFunction()
				f = rf.get(rfname)
				if f:
					r = f()
					if isinstance(r,Widget):
						self.content.add_widget(r)
			return
		if w:
			self.content.add_widget(w)

