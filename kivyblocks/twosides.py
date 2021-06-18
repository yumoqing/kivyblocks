from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory

from kivyblocks.ready import WidgetReady

class TwoSides(WidgetReady, BoxLayout):
	def __init__(self,landscape={},portrait={},**kw):
		BoxLayout.__init__(self,**kw)
		WidgetReady.__init__(self)
		blocks = Factory.Blocks()
		self.landscape_widget = blocks.widgetBuild(landscape)
		blocks = Factory.Blocks()
		self.portrait_widget = blocks.widgetBuild(portrait)
		self.on_size_task = None
		self.ready_task = None
		self.register_event_type('on_interactive')

	def on_size(self,*args):
		if self.width >= self.height:
			if not self.landscape_widget in self.children:
				self.clear_widgets()
				self.add_widget(self.landscape_widget)
		else:
			if not self.portrait_widget in self.children:
				self.clear_widgets()
				self.add_widget(self.portrait_widget)
				self.dispatch('on_interactive')

	def on_interactive(self, *args):
		pass


