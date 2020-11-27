from kivy.logger import Logger
from kivy.graphics import Color, Rectangle
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import AsyncImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.app import App
from kivy.clock import Clock

from appPublic.dictObject import DictObject

from .widgetExt.scrollwidget import ScrollWidget
from .utils import *
from .ready import WidgetReady
from .i18n import I18nText 
from .color_definitions import getColors
from .bgcolorbehavior import BGColorBehavior

"""
toobar={
	"mode":"icon", "icontext","text"
	img_size=2,	
	text_size=1,
	"tools":[
	]
}

tool options
{
	name:'',
	label:''
	img=''
}
"""
class Tool(ButtonBehavior, BGColorBehavior, BoxLayout):
	def __init__(self,ancestor=None,**opts):
		if ancestor is None:
			ancestor = App.get_running_app().root
		self.widget_id = opts['name']
		ButtonBehavior.__init__(self)
		BoxLayout.__init__(self,
					size_hint_y=None)
		BGColorBehavior.__init__(self,color_level=ancestor.color_level)
		self.bl = BoxLayout(orientation='vertical',
					size_hint_y=None)
		self.add_widget(self.bl)
		self.opts = DictObject(**opts)
		if not self.opts.img_size:
			self.opts.img_size = 2
		if not self.opts.text_size:
			self.opts.text_size = 1
		app = App.get_running_app()
		size = 0
		if self.opts.img_src:
			size = CSize(self.opts.img_size or 2)
			img = AsyncImage(source=self.opts.img_src,
				size_hint=(None,None),
				size=(size,size))
			self.bl.add_widget(img)

		tsize = CSize(self.opts.text_size)
		label = self.opts.label or self.opts.name
		self.lbl = I18nText( otext=label,
					font_size=int(tsize),
					text_size=(CSize(len(label)), tsize),
					height=tsize,
					width=CSize(len(label)),
					size_hint=(None,None),
					)
		self.bl.add_widget(self.lbl)
		self.height = (size + tsize)*1.1
		
	def on_size(self,obj,size):
		Logger.info('toolbar: Tool() on_size fired') 
		#self.lbl.color, self.bgcolor = getColors(self.ancestor.color_level,
		#					selected=False)
		#self.lbl.bgcolor = self.bgcolor

	def on_press(self):
		print('Tool(). pressed ...............')

	def setActive(self,flag):
		if flag:
			self.selected()
		else:
			self.unselected()


"""
toolbar options
{
	img_size=1.5,	
	text_size=0.7,
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
class Toolbar(BGColorBehavior, GridLayout):
	def __init__(self, ancestor=None,**opts):
		self.opts = DictObject(**opts)
		self.tool_widgets={}
		GridLayout.__init__(self,cols = len(self.opts.tools))
		color_level = 0
		if isinstance(ancestor, BGColorBehavior):
			color_level = ancestor.color_level + 1
		BGColorBehavior.__init__(self,color_level=color_level)
		self.size_hint = (1,None)
		first = True
		for opt in self.opts.tools:
			opt.img_size = self.opts.img_size
			opt.text_size = self.opts.text_size
			if opt.img_src:
				purl = None
				if ancestor and hasattr(ancestor, 'parenturl'):
					purl = ancestor.parenturl
				opt.img_src = absurl(opt.img_src,purl)
			tool = Tool(ancestor=ancestor, **opt)
			if first:
				first = False
				h = ancestor
				if not ancestor:
					h = App.get_runnung_app().root
			self.tool_widgets[opt.name] = tool
			box = BoxLayout()
			box.add_widget(tool)
			self.add_widget(box)
			tool.bind(on_press=self.tool_press)
		self.height = tool.height * 1.1

	def on_size(self,obj,size):
		return
		with self.canvas.before:
			Color(0.3,0.3,0.3,1)
			Rectangle(pos=self.pos,size=self.size)

	def tool_press(self,o,v=None):
		for n,w in self.tool_widgets.items():
			active = False
			if w == o:
				active = True
			w.setActive(active)

"""
Toolpage options
{
	img_size=1.5,	
	text_size=0.7,
	tool_at:"left","right","top","bottom",
	color_level=0,
	tools:[
		{
			"name":"myid",
			"img_src":"gggggg",
			"text":"gggggg"
			"url":"ggggggggg"
		},
		...
	]
	
"""
class ToolPage(BGColorBehavior, BoxLayout):
	def __init__(self,**opts):
		self.opts = DictObject(**opts)
		self.parenturl = opts.get('parenturl',None)
		if self.opts.tool_at in [ 'top','bottom']:
			orient = 'vertical'
		else:
			orient = 'horizontal'
		color_level=self.opts.color_level or 0
		BoxLayout.__init__(self,orientation=orient)
		BGColorBehavior.__init__(self,color_level=color_level)
		self.content = None
		self.toolbar = None
		self.init()
		self.show_firstpage()
	
	def on_size(self,obj,size):
		if self.content is None:
			return
		x,y = size
		self.toolbar.width = x
		self.content.width = x
		self.content.height = y - self.toolbar.height

	def showPage(self,obj):
		self._show_page(obj.opts)

	def show_firstpage(self,t=None):
		return
		d = self.children[0]
		d.dispatch('on_press')

	def init(self):
		self.initFlag = True
		self.mywidgets = {}
		self.content = BoxLayout()
		self.content.widget_id = 'content'
		for t in self.opts.tools:	
			parenturl = None
			if hasattr(self,'parenturl'):
				parenturl = self.parenturl
			t.img_src = absurl(t.img_src,parenturl)

		opts = self.opts
		self.toolbar = Toolbar(ancestor=self, **self.opts)
		if self.opts.tool_at in ['top','left']:
			self.add_widget(self.toolbar)
			self.add_widget(self.content)
		else:
			self.add_widget(self.content)
			self.add_widget(self.toolbar)

