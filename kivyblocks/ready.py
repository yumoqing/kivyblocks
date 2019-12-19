from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

class WidgetReady(Widget):
	ready = BooleanProperty(False)
	kwargs_keys = ['bg_color']
	def __init__(self, **kw):
		self.bg_color = kw.get('bg_color',None)
		self.all_ready = {}
		self.all_ready[self] = False
		self.backgroundcolorTask = None
		if self.bg_color is not None:
			self.setupBackgroundColor()

	def setupBackgroundColor(self):
		self.bind(pos=self.backgroundcolorfunc)
		self.bind(size=self.backgroundcolorfunc)

	def backgroundcolorfunc(self,o,v):
		if self.backgroundcolorTask is not None:
			self.backgroundcolorTask.cancel()
		self.backgroundcolorTask = Clock.schedule_once(self._setBackgroundColor)

	def _setBackgroundColor(self,t=0):
		self.canvas.before.clear()
		with self.canvas.before:
			Color(*self.bg_color)
			Rectangle(size=self.size,pos=self.pos)

	def addChild(self,w):
		"""
		need to call addChild to make widget to wait the subwidget on_ready event
		w the subwidget of self
		"""
		if hasattr(w,'ready'):
			self.all_ready[w] = False
			w.bind(on_ready=self.childReady)

	def childReady(self,c,v=None):
		self.all_ready[c] = True
		if all(self.all_ready.values()):
			self.ready = True

	def on_ready(self,o,v=None):
		print(self,'on_ready')

	def built(self):
		"""
		when self built, call it at end to issue the on_ready event
		"""
		self.all_ready[self] = True
		if all(self.all_ready.values()):
			self.ready = True
	
	def setBackgroundColor(self,bgcolor):
		self.bg_color = bgcolor
		self._setBackgroundColor(0)

