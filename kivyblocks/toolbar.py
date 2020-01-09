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
from .kivysize import KivySizes
from .ready import WidgetReady
from .i18n import I18nText 
"""
toobar={
	"mode":"icon", "icontext","text"
	img_size=1.5,	
	text_size=0.7,
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
class Tool(ButtonBehavior, WidgetReady,BoxLayout):
	normal_bgColor=[0.1,0,0,1]
	active_bgColor=[0.4,0.4,0.4,1]
	def __init__(self,ancestor=None,**opts):
		if ancestor is None:
			ancestor = App.get_running_app().root
		ancestor.widget_ids[opts['name']] = self
		ButtonBehavior.__init__(self)
		bc = opts.get('bg_color',self.normal_bgColor)
		WidgetReady.__init__(self,bg_color=self.normal_bgColor)
		BoxLayout.__init__(self,
					orientation='vertical',size_hint=(None,None))
		self.opts = DictObject(**opts)
		if not self.opts.img_size:
			self.opts.img_size = 2
		if not self.opts.text_size:
			self.opts.text_size = 0.7
		app = App.get_running_app()
		ks = KivySizes()
		size = ks.unitedSize(self.opts.img_size or 2)
		img = AsyncImage(source=self.opts.img_src,size_hint=(None,None),
			size=(size,size))
		tsize = ks.unitedSize(self.opts.text_size)
		label = self.opts.label or self.opts.name
		lbl = I18nText(otext=label,font_size=int(tsize))
		lbl.text_size = (size, 1.3 * tsize)
		self.add_widget(img)
		self.add_widget(lbl)
		self.size = (size * 1.1, (size + 2 * tsize)*1.1)
		
	def on_size(self,obj,size):
		if self.parent:
			print('********center*dd**********')
			self.center = self.parent.center

	def on_press(self):
		print('Tool(). pressed ...............')

	def setActive(self,flag):
		if flag:
			self.setBackgroundColor(self.active_bgColor)
		else:
			self.setBackgroundColor(self.normal_bgColor)


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
class Toolbar(GridLayout):
	def __init__(self, ancestor=None,**opts):
		self.opts = DictObject(**opts)
		self.tool_widgets={}
		super().__init__(cols = len(self.opts.tools))
		self.size_hint = (1,None)
		first = True
		for opt in self.opts.tools:
			opt.img_size = self.opts.img_size
			opt.text_size = self.opts.text_size
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
				h.widget_ids['_home_'] = tool
			self.tool_widgets[opt.name] = tool
			box = BoxLayout()
			box.add_widget(tool)
			self.add_widget(box)
			tool.bind(on_press=self.tool_press)
		self.height = tool.height * 1.1

	def on_size(self,obj,size):
		with self.canvas.before:
			Color(0.3,0.3,0.3,1)
			Rectangle(pos=self.pos,size=self.size)

	def tool_press(self,o,v=None):
		o.background_color = [0.3,1,1,0.5]
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
class ToolPage(BoxLayout):
	def __init__(self,**opts):
		self.opts = DictObject(**opts)
		self.parenturl = opts.get('parenturl',None)
		self.widget_ids = {}
		if self.opts.tool_at in [ 'top','bottom']:
			orient = 'vertical'
		else:
			orient = 'horizontal'

		super().__init__(orientation=orient)
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
		d = self.widget_ids['_home_']
		d.dispatch('on_press')

	def init(self):
		self.initFlag = True
		self.mywidgets = {}
		self.content = BoxLayout()
		self.widget_ids['content'] = self.content
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
		Clock.schedule_once(self.show_firstpage,0.5)

if __name__ == '__main__':
	from blocksapp import BlocksApp
	app = BlocksApp()
	app.run()
