from kivy.logger import Logger
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivyblocks.utils import CSize
from kivy.app import App

class WidgetCSS(object):
	height_nm = NumericProperty(None)
	width_nm = NumericProperty(None)
	height_cm = NumericProperty(None)
	width_cm = NumericProperty(None)
	bgcolor = ListProperty(None)
	fgcolor = ListProperty(None)
	csscls = StringProperty("default")
	radius = ListProperty(None)
	background_rec = None
	bg_func = Rectangle

	def on_size(self, o, s):
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
		if isinstance(self.csscls, str):
			self.set_css(self.csscls)

	def set_css(self, css_str):
		css = {}
		app = App.get_running_app()
		for css_name in css_str.split(' '):
			css.update(app.get_css(css_name))
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

	def set_child_fgcolor(self, c):
		if not hasattr(c,'fgcolor'):
			return 
		if c.fgcolor:
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
			return
		self.bg_func = RoundedRectangle
		# self.set_background_color()

	def set_background_color(self, *args):
		if not self.bgcolor:
			Logger.info('WidgetCSS: set_bg_color(), bgcolor is null, (%s)',
					self.__class__.__name__)
			return
		if not self.canvas:
			Logger.info('WidgetCSS: set_bg_color(), canvas is null(%s)',
					self.__class__.__name__)
			return

		with self.canvas.before:
			Color(*self.bgcolor)
			if self.radius:
				self.background_rect = self.bg_func(pos=self.pos,
							size=self.size,
							radius=self.radius)
			else:
				self.background_rect = self.bg_func(pos=self.pos, 
							size=self.size)
