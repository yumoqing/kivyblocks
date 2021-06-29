from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.core.window import Window
from kivy.properties import StringProperty

class TwoSides(BoxLayout):
	panel_shape = StringProperty('landscape')
	def __init__(self,landscape={},portrait={},**kw):
		BoxLayout.__init__(self,**kw)
		blocks = Factory.Blocks()
		self.landscape_widget = blocks.widgetBuild(landscape)
		blocks = Factory.Blocks()
		self.portrait_widget = blocks.widgetBuild(portrait)
		self.on_size_task = None
		self.ready_task = None
		self.register_event_type('on_interactive')
		self.register_event_type('on_beforeswitch_landscape')
		self.register_event_type('on_afterswitch_landscape')
		self.register_event_type('on_beforeswitch_portrait')
		self.register_event_type('on_afterswitch_portrait')

	def on_size(self,*args):
		if self.width >= self.height:
			if not self.landscape_widget in self.children:
				self.dispatch('on_beforeswitch_landscape')
				self.clear_widgets()
				self.add_widget(self.landscape_widget)
				self.panel_shape = 'landscape'
				self.dispatch('on_afterswitch_landscape')
		else:
			print('twosides.py:Window.rotation=', Window.rotation,
				Window.size)
			if not self.portrait_widget in self.children:
				self.dispatch('on_beforeswitch_landscape')
				self.clear_widgets()
				self.add_widget(self.portrait_widget)
				self.panel_shape = 'portrait'
				self.dispatch('on_afterswitch_landscape')
				self.dispatch('on_interactive')

	def on_beforeswitch_landscape(self, *args):
		pass

	def on_afterswitch_landscape(self, *args):
		print('twosides.py:Window.rotation=', Window.rotation,
			Window.size)
		pass

	def on_beforeswitch_portrait(self, *args):
		pass

	def on_afterswitch_portrait(self, *args):
		print('twosides.py:Window.rotation=', Window.rotation,
			Window.size)
		pass

	def on_interactive(self, *args):
		pass


