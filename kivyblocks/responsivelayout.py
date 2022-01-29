
from math import floor
from kivy.properties import NumericProperty
from kivy.utils import platform
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse,Rectangle
from kivy.clock import Clock
from .utils import CSize, isHandHold, show_widget_info

class VResponsiveLayout(ScrollView):
	box_width = NumericProperty(1)
	def __init__(self, **kw):
		self._inner = None
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
	
	def on_box_width(self, *args):
		if not self._inner:
			return
		self._inner.col_default_width = self.box_width
		for w in self._inner.children:
			w.size_hint_x = None
			w.width = self.box_width
		self.setCols()

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
		cols = floor(self.width / self.box_width)
		if cols < 1:
			cols = 1
		self._inner.cols = cols

