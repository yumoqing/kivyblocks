from kivy.logger import Logger
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import ListProperty
from .color_definitions import getColors

_logcnt = 0
class BGColorBehavior(object):
	def __init__(self, color_level=-1,radius=[],**kwargs):
		if color_level==-1:
			color_level = 0
		self.color_level = color_level
		self.radius = radius
		self.bgcolor = []
		self.fgcolor = []
		fg,bg= getColors(color_level)
		self.fgcolor = fg
		self.bgcolor = bg
		self.normal_bgcolor = bg
		self.normal_fgcolor = fg
		fg,bg= getColors(color_level,selected=True)
		self.selected_bgcolor = bg
		self.selected_fgcolor = fg
		self.on_bgcolor()

		self.bind(size=self.onSize_bgcolor_behavior,
				pos=self.onSize_bgcolor_behavior)

	def onSize_bgcolor_behavior(self,o,v=None):
		if not hasattr(self,'rect'):
			self.on_bgcolor()
		else:
			self.rect.pos = self.pos
			self.rect.size = self.size

	def on_bgcolor(self,o=None,v=None):
		if self.bgcolor == []:
			return
		if self.canvas:
			with self.canvas.before:
				Color(*self.bgcolor)
				if self.radius != []:
					self.rect = RoundedRectangle(pos=self.pos,
								size=self.size,
								radius=self.radius)
				else:
					self.rect = Rectangle(pos=self.pos, 
								size=self.size)
		else:
			print('on_bgcolor():self.canvas is None')

	def is_selected(self):
		return self.bgcolor == self.selected_bgcolor

	def selected(self):
		if self.bgcolor == self.selected_bgcolor:
			return
		self.bgcolor = self.selected_bgcolor
		self.color = self.fgcolor = self.selected_fgcolor
		self.on_bgcolor()

	def unselected(self):
		if self.bgcolor == self.normal_bgcolor:
			return
		self.bgcolor = self.normal_bgcolor
		self.color = self.fgcolor = self.normal_fgcolor
		self.on_bgcolor()
