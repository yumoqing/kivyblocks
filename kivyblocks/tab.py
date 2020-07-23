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
from kivy.factory import Factory

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

Factory.register('TabsPanel',TabsPanel)

if __name__ == '__main__':
	from kivy.app import App
	pass
