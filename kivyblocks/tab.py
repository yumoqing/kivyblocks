"""
{
	"widgettype":"TabsPanel",
	"options":{
		"tab_pos":"top_left"
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
	},
}
"""
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.factory import Factory

from .bgcolorbehavior import BGColorBehavior

class TabsPanel(BGColorBehavior, TabbedPanel):
	def __init__(self,color_level=-1,
					radius=[],
					**options):
		self.tabs_list = options.get('tabs')
		TabbedPanel.__init__(self,**options)
		BGColorBehavior.__init__(self,color_level=color_level,
						radius=radius)
		Clock.schedule_once(self.add_tabs,0)

	def add_tab(self,text,desc):
		def add(o,w):
			self.add_widget(TabbedPanelItem(text=text,content=w))
		blocks = Factory.Blocks()
		blocks.bind(on_built=add)
		blocks.widgetBuild(desc)

	def add_tabs(self,*args):
		for d in self.tabs_list:
			text = d['text']
			desc = d['content']
			self.add_tab(text,desc)

Factory.register('TabsPanel',TabsPanel)

if __name__ == '__main__':
	from kivy.app import App
	pass
