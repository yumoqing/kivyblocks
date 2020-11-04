from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory

class DoubleFace(BoxLayout):
	def __init__(self,landscape={},portrait={},**kw):
		BoxLayout.__init__(self,**kw)
		self.landscape_built = False
		self.portrait_built = False
		self.landscape_widget = None
		self.portrait_widget = None
		blocks = Factory.Blocks()
		blocks.bind(on_built=self.landscape_built)
		blocks.widgetBuilt(landscape,ancestor=self)
		blocks = Factory.Blocks()
		blocks.bind(on_built=self.portrait_built)
		blocks.widgetBuild(portrait,ancestor=self)
		self.on_size_task = None

	def landscape_built(self,o,w):
		self.landscape_widget = w
		self.landscape_built = True

	def partrait_built(self,o,w):
		self.portrait_widget = w
		self.portrait_built = True

	def on_size(self,*args):
		if not self.landscape_built or not self.portrait_built:
			if not self.on_size_task is None:
				self.on_size_task.cancel()
			self.on_size_task.schedule_once(self.on_size,0.2)
			return
		if self.width >= self.height:
			if not self.landscape_widget in self.children:
				self.clear_widget()
				self.add_widget(self.landscape_widget)
		else:
			if not self.portrait_widget in self.children:
				self.clear_widget()
				self.add_widget(self.portrait_widget)

