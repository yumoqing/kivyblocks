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
from appPublic.uniqueID import getID

from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.factory import Factory
from kivyblocks.utils import SUPER
from kivyblocks.widget_css import WidgetCSS

class TabsPanel(WidgetCSS, TabbedPanel):
	def __init__(self, tabs=[], **options):
		self.tabs_list = tabs
		SUPER(TabsPanel, self, options)
		# TabbedPanel.__init__(self,**options)
		# BGColorBehavior.__init__(self)
		self.old_content = None
		self.def_tab = None
		self.register_event_type('on_content_show')
		self.register_event_type('on_content_hide')
		Clock.schedule_once(self.add_tabs,0)

	def add_tab(self,desc):
		if not desc.get('name'):
			desc['name'] = getID()
		blocks = Factory.Blocks()
		w = blocks.widgetBuild(desc['content'])
		if w is None:
			return
		if not hasattr(w,'widget_id'):
			w.widget_id = desc['name']
		item = TabbedPanelItem(text=desc['text'],content=w)
		if desc.get('isdefault', False):
			self.def_tab = item
		self.add_widget(item)

	def add_tabs(self,*args):
		for d in self.tabs_list:
			self.add_tab(d)
		if self.def_tab:
			self.switch_to(self.def_tab)
		self.bind(current_tab = self.content_changed)
	
	def content_changed(self, o, v=None):
		if self.old_content:
			self.dispatch('on_content_hide', self.old_content)
		self.old_content = self.current_tab.content
		self.dispatch('on_content_show', self.old_content)

	def on_content_show(self, *args):
		print('content show', args)
	
	def on_content_hide(self, *args):
		print('content hide', args)

if __name__ == '__main__':
	from kivy.app import App
	pass
