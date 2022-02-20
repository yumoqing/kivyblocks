
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
	columes = NumericProperty(None)
	def __init__(self, **kw):
		self._inner = None
		self.col_width = None
		self.cols = None
		super(VResponsiveLayout, self).__init__(**kw)
		self.options = kw
		self._inner = GridLayout(cols=1, padding=2, 
						spacing=2,size_hint=(1,None))
		self._inner.col_force_default = True
		self._inner.col_default_width = self.box_width
		super(VResponsiveLayout,self).add_widget(self._inner)
		self._inner.bind(
				minimum_height=self._inner.setter('height'))
		self.bind(size=self.set_col_width)
	
	def calculate_col_width(self, cnt):
		# cnt * col_width + 2*padding + (cnt-1) * spacing = width
		w = self._inner
		padding = 0
		if isinstance(w.padding, float):
			padding = w.padding
		elif len(w.padding) < 4:
			padding = w.padding[0]
		else:
			padding = (w.padding[0] + w.padding[2])/2
		spacing = 0
		if isinstance(w.spacing, float):
			spacing = w.spacing
		elif len(w.spacing) < 4:
			spacing = w.spacing[0]
		else:
			spacing = (w.spacing[0] + w.spacing[2]) / 2
		width = (w.width - 2 * padding - cnt * spacing) / cnt
		return width

	def get_col_width(self):
		return self._inner.col_default_width

	def get_cols(self):
		return self._inner.cols

	def set_col_width(self, o, s):
		if self._inner is None:
			return
		self._inner.size_hint = [None, None]
		self._inner.size = self.size
		if isHandHold() and self.width < self.height:
			self.cols = 1
			self.col_width = self.calculate_col_width(self.cols)
			return self.setCols()

		if self.columes is not None and self.columes > 0:
			self.cols = self.columes
			self.col_width = self.calculate_col_width(self.cols)
			return self.setCols()
			
		if self.box_width_c is not None:
			self.cols = floor(self._inner.width / CSize(self.box_width_c))
			if self.cols < 1:
				self.cols = 1
			self.col_width = self.calculate_col_width(self.cols)
			return self.setCols()

		if self.box_width is not None:
			if self.box_width <= 1:
				self.cols = floor(1 / self.box_width)
				self.col_width = self.calculate_col_width(self.cols)
				return self.setCols()
			else:
				self.cols = floor(self._inner.width / self.box_width)
				if self.cols < 1:
					self.cols = 1
				self.col_width = self.calculate_col_width(self.cols)
				return self.setCols()
		return
			
	def on_orientation(self,o):
		self.set_col_width()

	def add_widget(self,widget,**kw):
		a = self._inner.add_widget(widget,**kw)
		return a

	def clear_widgets(self,**kw):
		a = self._inner.clear_widgets(**kw)

	def remove_widget(self,widget,**kw):
		a = self._inner.remove_widget(widget,**kw)
		return a

	def setCols(self,*args):
		self._inner.cols = self.cols
		self._inner.col_default_width = self.col_width
		for w in self._inner.children:
			w.size_hint_x = None
			w.width = self._inner.col_default_width

