from kivy.logger import Logger
from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty, NumericProperty
from kivy.factory import Factory
from kivy.uix.widget import Widget

from .color_definitions import getColors

class NewWidget(Widget):
	bgcolor = ListProperty([])
	fcolor = ListProperty([])
	color_level = NumericProperty(-1)
	def __init__(self, color_level=-1,bgcolor=[],fcolor=[],**kwargs):
		super().__init__(**kwargs)
		self.bgcolor = bgcolor
		self.fcolor = fcolor
		self.color_level = color_level
		self.initColors()
		self.bind(size=self.onSize_bgcolor_behavior,
					pos=self.onSize_bgcolor_behavior)

	def initColors(self):
		if self.color_level != -1:
			fcolor, bgcolor = getColors(self.color_level)
			if self.bgcolor == []:
				self.bgcolor = bgcolor
			if self.fcolor == []:
				self.fcolor = fcolor

	def getParentColorLevel(self):
		if not self.parent:
			self.fcolor, self.bgcolor = getColors(self.color_level)
			
	def on_color_level(self,o,v=None):
		if bgcolor != [] and fcolor != []:
			return

		if color_level != -1:
			fcolor, bgcolor = getColors(self.color_level)
			if self.bgcolor == []:
				self.bgcolor = bgcolor
			if self.fcolor == []:
				self.fcolor = fcolor

	def on_fcolor(self,o,v=None):
		self.color = self.fcolor

	def on_parent(self,o,v=None):
		if self.color_level != -1:
			self.fcolor, self.bgcolor = getColors(self.color_level)

		if self.color_level == -1:
			self.setColorsFromAncestor()

	def onSize_bgcolor_behavior(self,o,v=None):
		if not hasattr(self,'rect'):
			self.on_bgcolor()
		else:
			self.rect.pos = o.pos
			self.rect.size = o.size

	def on_bgcolor(self,o=None,v=None):
		if self.bgcolor == []:
			return
		if self.canvas:
			with self.canvas.before:
				Color(*self.bgcolor)
				self.rect = Rectangle(pos=self.pos, 
								size=self.size)

try:
	Factory.unregister('Widget')
except:
	pass
Factory.register('Widget',cls=NewWidget)
