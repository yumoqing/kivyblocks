from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory

from kivyblocks.ready import WidgetReady

class DoubleFace(WidgetReady, BoxLayout):
	def __init__(self,landscape={},portrait={},**kw):
		BoxLayout.__init__(self,**kw)
		WidgetReady.__init__(self)
		self.parenturl = kw.get('parenturl')
		self.landscape_built = False
		self.portrait_built = False
		self.landscape_widget = None
		self.portrait_widget = None
		blocks = Factory.Blocks()
		blocks.bind(on_built=self.landscape_build)
		blocks.widgetBuild(landscape,ancestor=self)
		blocks = Factory.Blocks()
		blocks.bind(on_built=self.portrait_build)
		blocks.widgetBuild(portrait,ancestor=self)
		self.on_size_task = None
		self.ready_task = None

	def ready(self, *args):
		if self._ready:
			return
		if not self.landscape_built or not self.portrait_built:
			if not self.ready_task is None:
				self.ready_task.cancel()
			self.ready_task = Clock.schedule_once(self.ready,0.2)
			return 
		self.dispatch('on_ready')
		self._ready = True

	def landscape_build(self,o,w):
		self.landscape_widget = w
		self.landscape_built = True

	def portrait_build(self,o,w):
		self.portrait_widget = w
		self.portrait_built = True

	def on_size(self,*args):
		if not self.landscape_built or not self.portrait_built:
			if not self.on_size_task is None:
				self.on_size_task.cancel()
			self.on_size_task = Clock.schedule_once(self.on_size,0.2)
			return
		if self.width >= self.height:
			if not self.landscape_widget in self.children:
				self.clear_widgets()
				self.add_widget(self.landscape_widget)
		else:
			if not self.portrait_widget in self.children:
				self.clear_widgets()
				self.add_widget(self.portrait_widget)


Factory.register('DoubleFace',DoubleFace)
