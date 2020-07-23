"""
{
	"widgettype":"BLKTabbedPanel",
	"options":{
		"tab_pos":"top_left"
	},
	"tabs":[
		{
			"text":"tab1",
			"icon":"/img/hhhh.png",
			"refresh_press":Fasle,
			"content":{
				"widgettype":"urlwidegt",
				"url":"reggtY",
			}
		},
		{
		}
	]
}
"""
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.clock import Clock
from kivyblocks.blocks import Blocks

class TabsPanel(BGColorBehavior, TabbedPanel):
	def __init__(self,**options):
		self.tabs_list = options.get('tabs')
		self.color_level = options.get('color_level',0)
		opts = {k:v for k,v in options.items() if k not in ['tabs','color_level']}
		TabbedPanel.__init__(self,**opts)
		BGColorBehavior.__init__(self)
		Clock.schedule_once(self.addTabs,0)

	def add_tab(self,text,desc):
		def add(o,w):
			self.add_widget(TabbedPanelItem(text=text,content=w))
		blocks = Blocks()
		blocks.bind(on_built=add)
		blocks.widgetBuild(desc,ancestor=self)

	def add_tabs(self,*args):
		for d in self.tabs_list:
			text = d['text']
			desc = d['content']
			self.add_tab(text,desc)

		w = block.widgetBuild((
class BLKTabItem(BGColorBehavior, TabbedPanelItem):
	def __init__(self,parent,color_level=0,text="",content={}):
		self.parent=parent
		self.color_level = color_level

class BLKTabedPanel(BGColorBehavior, TabbedPanel):
	def __init__(self,color_level=0, tabs=[], **kwargs):
		self.tabs_desc = tabs
		self.color_level = color_level
		TabbedPanel.__init__(**kwargs)
		BGColorBehavior.__init__(self)

class 
