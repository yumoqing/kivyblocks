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

from appPublic.dictObject import DictObject
from appPublic.registerfunction import RegisterFunction

from .widgetExt.scrollwidget import ScrollWidget
from .utils import *
from .ready import WidgetReady
from .color_definitions import getColors
from .bgcolorbehavior import BGColorBehavior
from .baseWidget import Text
from .toggleitems import PressableBox, ToggleItems

"""
toolbar options
{
	color_level:
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
class Toolbar(BoxLayout):
	def __init__(self, color_level=-1,
				radius=[],
				img_size=1.5,
				text_size=0.5,
				tools=[], **opts):
		self.color_level = color_level
		self.radius = radius
		self.img_size = img_size
		self.text_size = text_size
		self.tools = tools
		self.tool_widgets={}
		BoxLayout.__init__(self, **opts)
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
				color_level=self.color_level,
				radius=self.radius,
				unit_size=self.img_size + self.text_size,
				items_desc=subs_desc,
				orientation=opts.get('orientation','horizontal')
				)
		for ti in self.toggle_items.children:
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
	color_level:0,
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
class ToolPage(BGColorBehavior, BoxLayout):
	def __init__(self,color_level=-1,radius=[],
					toolbar_size=None,
					img_size=1.5,
					text_size=0.7,
					show_name=None, tool_at='top', **opts):
		self.opts = DictObject(**opts)
		if tool_at in [ 'top','bottom']:
			orient = 'vertical'
		else:
			orient = 'horizontal'
		if not toolbar_size:
			toolbar_size = img_size + text_size + 0.3
		self.toolbar_size = toolbar_size
		self.img_size = img_size
		self.text_size = text_size
		names = [i.name for i in self.opts.tools]
		if not show_name or \
			not show_name in names:
			show_name = self.opts.tools[0].name
			
		self.content_widgets = {}
		self.show_name = show_name
		self.color_level=self.opts.color_level or 0
		self.sub_radius = self.opts.radius
		self.tool_at = tool_at
		BoxLayout.__init__(self,orientation=orient)
		BGColorBehavior.__init__(self,
							color_level=color_level,
							radius=[])
		self.content = None
		self.toolbar = None
		self.init()
		print('Toolpage():self.show_name=', self.show_name)
		Clock.schedule_once(self.show_page, 0.5)
	
	def show_page(self, *args):
		print('toolbar=',self.toolbar.width,self.toolbar.height, \
				'toggleitems=',self.toolbar.toggle_items.width, \
					self.toolbar.toggle_items.height)
		toggle_items = self.toolbar.toggle_items
		for c in toggle_items.children:
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

	def init(self):
		self.initFlag = True
		self.mywidgets = {}
		self.content = BoxLayout()
		self.content.widget_id = 'content'
		opts = self.opts.copy()
		if self.tool_at in ['top','bottom']:
			opts['size_hint_x'] = 1 
			opts['size_hint_y'] = None
			opts['height'] = CSize(self.toolbar_size)
			opts['orientation'] = 'horizontal'
		else:
			opts['size_hint_y'] = 1
			opts['size_hint_x'] = None
			opts['width'] = CSize(self.toolbar_size)
			opts['orientation'] = 'vertical'
		self.toolbar = Toolbar(color_level=self.color_level,
						radius=self.sub_radius,
						img_size=self.img_size,
						text_size=self.text_size,
						**opts)
		if self.tool_at in ['top','left']:
			self.add_widget(self.toolbar)
			self.add_widget(self.content)
		else:
			self.add_widget(self.content)
			self.add_widget(self.toolbar)
		toggle_items = self.toolbar.toggle_items
		for t in toggle_items.children:	
			t.bind(on_press=self.on_press_handle)

	def get_tool_by_name(self,name):
		for t in self.opts.tools:
			if t.name == name:
				return t
		return None

	def build_widget(self, url):
		desc = {
			"widgettype":"urlwidget",
			"options":{
				"url":url
			}
		}
		b = Factory.Blocks()
		return b.widgetBuild(desc)

	def on_press_handle(self, o):
		name = o.getValue()
		t = self.get_tool_by_name(name)
		w = self.content_widgets.get(name)
		self.content.clear_widgets()
		if w is None or t.fresh:
			if t.url:
				w = self.build_widget(t.url)
				self.content_widgets[name] = w
				self.content.add_widget(w)
				return
			if t.rfname:
				rf = RegisterFunction()
				f = rf.get(t.rfname)
				if f:
					r = f()
					if isinstance(r,Widget):
						self.content.add_widget(r)
			return
		if w:
			print('toolbar.py: Use old widget')
			self.content.add_widget(w)

