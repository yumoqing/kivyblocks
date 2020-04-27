from kivy.logger import Logger
from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty
from .color_definitions import getColors

_logcnt = 0
class BGColorBehavior(object):
	def __init__(self, bgcolor=[],fgcolor=[], color_level=-1,**kwargs):
		self.color_level = color_level
		self.bgcolor = bgcolor
		self.fgcolor = fgcolor
		self.normal_bgcolor = bgcolor
		self.normal_fgcolor = fgcolor
		self.selected_bgcolor = bgcolor
		self.selected_fgcolor = fgcolor
		self.useOwnColor = False
		self.useOwnBG = False
		self.useOwnFG = False
		if color_level != -1:
			fg,bg= getColors(color_level)
			self.fgcolor = fg
			self.bgcolor = bg
			self.normal_bgcolor = bg
			self.normal_fgcolor = fg
			fg,bg= getColors(color_level,selected=True)
			self.selected_bgcolor = bg
			self.selected_fgcolor = fg
			self.useOwnColor = True
		else:
			if bgcolor != [] and fgcolor != []:
				self.useOwnColor = True
			elif bgcolor != []:
				self.useOwnBG = True
			elif fgcolor != []:
				self.useOwnFG = True
		if self.fgcolor!=[]:
			self.color = self.fgcolor
		self.bind(size=self.onSize_bgcolor_behavior,
					pos=self.onSize_bgcolor_behavior)
		self.bind(parent=self.useAcestorColor)
		self.on_bgcolor()

	def useAcestorColor(self,o,v=None):
		if self.useOwnColor:
			return
		
		p = self.parent
		cnt = 0
		while p:
			if isinstance(p,BGColorBehavior):
				break
			p = p.parent
			cnt += 1
			if cnt > 100:
				return
		if not self.useOwnBG and p:
			self.bgcolor = p.bgcolor
			self.on_bgcolor()
		if not self.useOwnFG and p:
			self.fgcolor = p.bgcolor
			self.color = self.fgcolor

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
				self.rect = Rectangle(pos=self.pos, 
								size=self.size)

	def selected(self):
		self.bgcolor = self.selected_bgcolor
		self.on_bgcolor()

	def unselected(self):
		self.bgcolor = self.normal_bgcolor
		self.on_bgcolor()
