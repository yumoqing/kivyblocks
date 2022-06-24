from kivy.logger import Logger
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivyblocks.utils import CSize

from .colorcalc import *

csses = {
	"default":{
		"bgcolor":[0.35,0.35,0.35,1],
		"fgcolor":[0.85,0.85,0.85,1]
	}
}

csskeys=[
	"height_nm",
	"width_nm",
	"height_c",
	"width_c",
	"fgcolor_s",
	"bgcolor_s",
	"bgcolor",
	"fgcolor",
	"csscls",
	"radius",
	"height",
	"width",
]

def register_css(cssname, cssdic):
	dic = {k:v for k,v in cssdic.items() if k in csskeys }
	csses.update({cssname:dic})

def get_css(cssname,default='default'):
	return csses.get(cssname, csses.get(default))

class WidgetCSS(object):
	height_nm = NumericProperty(None)
	width_nm = NumericProperty(None)
	height_c = NumericProperty(None)
	width_c = NumericProperty(None)
	fgcolor_s = StringProperty(None)
	bgcolor_s = StringProperty(None)
	bgcolor = ListProperty(None)
	fgcolor = ListProperty(None)
	csscls = StringProperty("default")
	radius = ListProperty(None)
	background_rect = None
	bg_func = Rectangle

	def on_canvas(self, o, s):
		#Logger.info('WidgetCSS:on_canvas():%s',self.__class__.__name__)
		self.set_background_color()

	def on_size(self, o, s):
		try:
			super(WidgetCSS, self).on_size(o, s)
		except:
			pass
		self.set_background_color()

	def on_pos(self, o, p):
		self.set_background_color()

	def on_height_nm(self, o, v):	
		if not self.height_nm:
			return
		if self.height_nm <= 1:
			self.size_hint_y = self.height_nm
		else:
			self.size_hint_y = None
			self.height = height_nm

	def on_width_nm(self, o, v):
		if not self.width_nm:
			return
		if self.width_nm <= 1:
			self.size_hint_x = self.width_nm
		else:
			self.size_hint_x = None
			self.width = self.width_nm

	def on_csscls(self, o, csscls):
		self.set_css(self.csscls)

	def set_css(self, css_str):
		css = {}
		for css_name in css_str.split(' '):
			css.update(get_css(css_name))
		for k,v in css.items():
			setattr(self,k,v)

	def on_height_c(self, o, c):
		if not self.height_c:
			return
		self.size_hint_y = None
		self.height = CSize(self.height_c)

	def on_width_c(self, o, c):
		if not self.width_c:
			return
		self.size_hint_x = None
		self.width = CSize(self.width_c)

	def set_child_fgcolor(self, c):
		if not self.fgcolor:
			return
		if isinstance(c, WidgetCSS):
			return 
		if isinstance(c, TextInput):
			c.foreground_color = self.fgcolor
			return
		if isinstance(c, Label):
			c.color = self.fgcolor
			return
		for x in c.children:
			self.set_child_fgcolor(x)

	def on_children(self, o, c):
		for c in self.children:
			self.set_child_fgcolor(c)
			
	def on_fgcolor_s(self, o, c):
		if not c:
			return
		self.fgcolor = toArrayColor(c)

	def on_bgcolor_s(self, o, c):
		if not c:
			return
		self.bgcolor = toArrayColor(c)

	def on_fgcolor(self, o, c):
		if not self.fgcolor:
			return
		if isinstance(self, TextInput):
			self.foreground_color = self.fgcolor
		if isinstance(self, Label):
			self.color = self.fgcolor
			return
		for c in self.children:
			self.set_child_fgcolor(c)
		return

	def on_bgcolor(self, o, c):
		if not self.bgcolor:
			return
		if isinstance(self, TextInput):
			self.background_color = self.bgcolor
			return
		if isinstance(self, Button):
			self.background_color = self.bgcolor
			return
		self.set_background_color()

	def on_radius(self, o, r):
		if not self.radius:
			self.bg_func = Rectangle
		else:
			self.bg_func = RoundedRectangle
		self.set_background_color()

	def set_background_color(self, *args):
		if not self.bgcolor:
			return
		if not self.canvas:
			#Logger.info('WidgetCSS: set_bg_color(), canvas is null(%s)',
			#		self.__class__.__name__)
			return

		# self.canvas.before.clear()
		with self.canvas.before:
			Color(*self.bgcolor)
			if self.radius:
				self.background_rect = self.bg_func(pos=self.pos,
							size=self.size,
							radius=self.radius)
			else:
				self.background_rect = self.bg_func(pos=self.pos, 
							size=self.size)

