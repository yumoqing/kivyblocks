from kivy.graphics import Color, Rectangle
from kivy.logger import logging

from kivyblocks.colorcalc import toArrayColor

from appPublic.jsonConfig import getConfig

from .color_definitions import getColors, getSelectedColors
from .color_definitions import getInfoColors, getErrorColors

class StyleBehavior(object):
	def __init__(self,level=0):
		config = getConfig()
		style = config.style
		self.style_level = level
		self.selected_flag = False
		logging.info('Tree : style=%s,level=%d',style, level)
		c1, c2 = getColors(style,level)
		self.text_color, self.bg_color = toArrayColor(c1),toArrayColor(c2)
		c1, c2 = getSelectedColors(style,level)
		self.s_text_color,self.s_bg_color = toArrayColor(c1), toArrayColor(c2)
		self.bind(size=self.setBGColor,pos=self.setBGColor)

	def setBGColor(self,o=None,v=None):
		c = self.bg_color
		if self.selected_flag:
			c = self.s_bg_color
		logging.info('selected=%s,color=%s',str(self.selected_flag),str(c))
		with self.canvas.before:
			Color(*c)
			Rectangle(pos=self.pos,size=self.size)

	def selected(self):
		self.selected_flag = True
		self.setBGColor()

	def unselected(self):
		self.selected_flag = False
		self.setBGColor()
