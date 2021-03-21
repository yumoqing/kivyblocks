from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivyblocks.utils import CSize

kivyblocks_css_keys = [
	"height_nm",
	"width_nm",
	"height_cm",
	"width_cm",
	"bgcolor",
	"fgcolor",
	"radius",
	"spacing",
	"padding",
	"border"
]

kivyblocks_csses = {
	"default":{
	},
}

class WidgetCSS(object):
	height_nm = NumericProperty(None)
	width_nm = NumericProperty(None)
	height_cm = NumericProperty(None)
	width_cm = NumericProperty(None)
	bgcolor = ListProperty(None)
	fgcolor = ListProperty(None)
	csscls = StringProperty(None)
	radius = ListProperty(None)

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
		if isinstance(self.csscls, str):
			self.set_css(sef.csscls)

	def _get_css_dict_by_name(self, css_name):
		dic = kivyblocks_csses.get(css_name,{})
		return dic

	def set_css(self, css_str):
		css = {}
		for css_name in css_str.split(' '):
			css.update(self._get_css_dict_by_name(css_name))
		for k,v in css.items():
			setattr(self,k,v)

	def on_height_cm(self, o, c):
		if not height_cm:
			return
		self.size_hint_y = None
		self.height = CSize(self.height_cm)

	def on_width_cm(self, o, c):
		if not width_cm:
			return
		self.size_hint_x = None
		self.width = CSize(self.width_cm)

	def on_fgcolor(self, o, c):
		if not self.fgcolor:
			return
		if isinstance(self, TextInput):
			self.foreground_color = fgcolor
		if isinstance(self, Label):
			self.color = fgcolor
			return
		return

	def on_bgcolor(self, o, c):
		if not self.bgcolor:
			return
		if isinstance(self, TextInput):
			self.background_color = bgcolor
			return
		if isinstance(self, Button):
			self.background_color = bgcolor
			return
		self.set_background_color()

	def on_radius(self, o, r):
		if not radius:
			return
		self.set_background_color()

	def set_background_color(self, *args):
		if not self.bgcolor:
			return
		if not self.canvas:
			return

		with self.canvas.before:
			Color(*self.bgcolor)
			if self.radius and len(self.radius) == 4:
				self.background_rect = RoundedRectangle(pos=self.pos,
							size=self.size,
							radius=self.radius)
			else:
				self.background_rect = Rectangle(pos=self.pos, 
							size=self.size)

