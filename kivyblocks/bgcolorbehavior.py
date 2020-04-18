from kivy.logger import Logger
from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty

_logcnt = 0
class BGColorBehavior(object):
	bgcolor = ListProperty([])
	def __init__(self, bgcolor=[0,0,0,1],**kwargs):
		self.bgcolor = bgcolor
		self.bind(size=self.onSize_bgcolor_behavior,
					pos=self.onSize_bgcolor_behavior)
		self.on_bgcolor()

	def onSize_bgcolor_behavior(self,o,v=None):
		if not hasattr(self,'rect'):
			self.on_bgcolor()
		else:
			self.rect.pos = o.pos
			self.rect.size = o.size

	def on_bgcolor(self,o=None,v=None):
		if self.canvas:
			with self.canvas.before:
				Color(*self.bgcolor)
				self.rect = Rectangle(pos=self.pos, 
								size=self.size)

