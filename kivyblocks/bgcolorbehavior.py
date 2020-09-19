from kivy.logger import Logger
from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty
from .color_definitions import getColors

_logcnt = 0
class BGColorBehavior(object):
	def __init__(self, color_level=-1,**kwargs):
		self.color_level = color_level
		self.bgcolor = []
		self.fgcolor = []
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
			self.on_bgcolor()

		self.bind(size=self.onSize_bgcolor_behavior,
					pos=self.onSize_bgcolor_behavior)

	def useAcestorColor(self,selected=False):
		p = self.parent
		cnt = 0
		while p:
			if isinstance(p,BGColorBehavior) and p.useOwnColor:
				if selected:
					self.bgcolor = p.selected_bgcolor
					self.color = self.fgcolor = p.selected_fgcolor
				else:
					self.bgcolor = p.normal_bgcolor
					self.color = self.fgcolor = p.normal_fgcolor
				self.on_bgcolor()
				return
			p = p.parent
			cnt += 1
			if cnt > 100:
				break
		fg,bg= getColors(0,selected=selected)
		self.bgcolor = bg
		self.color = self.fgcolor = fg
		self.on_bgcolor()

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
		if self.useOwnColor:
			self.bgcolor = self.selected_bgcolor
			self.color = self.fgcolor = self.selected_fgcolor
			self.on_bgcolor()
		else:
			print('BGColorBehavior():selected(),useAcestorColor()')
			self.useAcestorColor(selected=True)

	def unselected(self):
		if self.useOwnColor:
			self.bgcolor = self.normal_bgcolor
			self.color = self.fgcolor = self.normal_fgcolor
			self.on_bgcolor()
		else:
			print('BGColorBehavior():unselected(),useAcestorColor()')
			self.useAcestorColor(selected=False)
