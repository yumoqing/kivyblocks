
from math import floor
from kivy.properties import NumericProperty
from kivy.utils import platform
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse,Rectangle
from kivy.clock import Clock
from .utils import CSize, isHandHold, show_widget_info
from .widget_css import WidgetCSS
from .ready import WidgetReady

class VResponsiveLayout(WidgetCSS, WidgetReady, ScrollView):
	box_width = NumericProperty(None)
	box_width_c = NumericProperty(None)
	def __init__(self, **kw):
		self._inner = None
		self.col_width = None
		self.col_width_hint = False
		super(VResponsiveLayout, self).__init__(**kw)
		self.options = kw
		self._inner = GridLayout(cols=1, padding=2, 
						spacing=2,size_hint=(1,None))
		self._inner.col_force_default = True
		self._inner.col_default_width = self.box_width
		super(VResponsiveLayout,self).add_widget(self._inner)
		self._inner.bind(
				minimum_height=self._inner.setter('height'))
		self.setCols()
		self.bind(pos=self.setCols,size=self.setCols)
	
	def on_box_width_c(self, *args):
		if self.box_width:
			return
		self.col_width = CSize(self.box_width)
		self.col_width_hint = False
		self.set_cols()

	def on_box_width(self, *args):
		if not self._inner:
			return
		if self.box_width <= 1:
			self.col_width = self.box_width
			self.col_width_hint = self.box_width
		else:
			self.col_width = self.box_width
		self.col_width_hint = False
		self.set_cols()

	def calculate_col_width(self):
		# cnt * col_width + 2*padding + (cnt-1) * spacing = width
		w = self._inner
		width = w.width - 2 * w.padding
		return width * self.col_width

	def get_col_width(self):
		return self._inner.col_default_width

	def get_cols(self):
		return self._inner.cols

	def set_col_width_cnt(self):
		if self.col_width_hint:
			self._inner.col_default_width = self.calc_col_width()
		else:
			self._inner.col_default_width = self.col_width
		self.setCols()
		for w in self._inner.children:
			w.size_hint_x = None
			w.width = self._inner.col_default_width

	def on_orientation(self,o):
		self.setCols()

	def add_widget(self,widget,**kw):
		a = self._inner.add_widget(widget,**kw)
		return a

	def clear_widgets(self,**kw):
		a = self._inner.clear_widgets(**kw)

	def remove_widget(self,widget,**kw):
		a = self._inner.remove_widget(widget,**kw)
		return a

	def setCols(self,*args):
		cols = floor(self.width / self._inner.col_default_width)
		if cols < 1:
			cols = 1
		self._inner.cols = cols

