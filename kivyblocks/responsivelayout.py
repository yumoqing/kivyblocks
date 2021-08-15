
from kivy.utils import platform
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse,Rectangle
from kivy.clock import Clock
from .utils import CSize, isHandHold

class VResponsiveLayout(ScrollView):
	def __init__(self,box_width,cols, **kw):
		self.org_box_width = box_width
		self.org_cols = cols
		self.box_width = box_width
		self.box_cols = cols
		super(VResponsiveLayout, self).__init__(**kw)
		self.options = kw
		self._inner = GridLayout(cols=self.org_cols, padding=2, 
						spacing=2,size_hint=(1,None))
		super(VResponsiveLayout,self).add_widget(self._inner)
		self._inner.bind(
				minimum_height=self._inner.setter('height'))
		self.sizeChangedTask = None
		self.bind(pos=self.setCols,size=self.setCols)
	
	def on_orientation(self,o):
		self.setCols()

	def add_widget(self,widget,**kw):
		width = self.box_width
		if hasattr(widget, 'cols'):
			width = widget.cols * self.box_width
		widget.width = width
		a = self._inner.add_widget(widget,**kw)
		return a

	def clear_widgets(self,**kw):
		a = self._inner.clear_widgets(**kw)

	def remove_widget(self,widget,**kw):
		a = self._inner.remove_widget(widget,**kw)
		return a

	def setCols(self,*args):
		cols = round(self.width / self.org_box_width)
		if cols < 1:
			cols = 1
		if isHandHold() and self.width < self.height and self.org_cols >= 2:
			cols = 2
		box_width = self.width / cols - 2
		self._inner.cols = cols
		for w in self._inner.children:
			w.width = box_width

