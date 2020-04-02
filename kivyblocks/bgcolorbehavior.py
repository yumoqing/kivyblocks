from kivy.logger import Logger
from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty

_logcnt = 0
class BGColorBehavior(object):
	bgcolor = ListProperty([])
	def __init__(self, bgcolor=[1,0,0,1],**kwargs):
		self.bgcolor = bgcolor
		self.bind(size=self.on_bgcolor,pos=self.on_bgcolor)

	def on_bgcolor(self,o=None,v=None):
		global _logcnt
		Logger.info('bgcolorBehavior: on_bgcolor(),o=%s,v=%s,logcnt=%d',\
						o.text if hasattr(o,'text') else o,v,_logcnt)
		_logcnt += 1
		x = abs(self.size[0] - 100.0)
		y = abs(self.size[1] - 100.0)
		if self.size[0] < 0.0001 or self.size[1] < 0.0001:
			return
		if x < 0.0001 and y < 0.0001:
			return
		if self.canvas:
			with self.canvas.before:
				Color(*self.bgcolor)
				Rectangle(pos=self.pos, size=self.size)

