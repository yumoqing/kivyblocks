from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.factory import Factory
from kivyblocks.widget_css import WidgetCSS
from kivyblocks.ready import WidgetReady

class TypeWriterBox(WidgetCSS, WidgetReady, Widget):
	def __init__(self, **kw):
		super(TypeWriterBox, self).__init__(**kw)
		self.size_hint_y = None
		self.sub_widgets = []
		self.curbox = self.add_vertical_box()
		self.bind(minimum_height=self.setter('height'))

	def on_width(self, o, size):
		self.relocate()

	def add_widget(self, w, *args):
		width = 0
		for c in self.curbox.children:
			width += c.width
		if width + c.width > self.width:
			self.curbox = self.add_vertical_box()
		self.curbox.add_widget(w, *args)
		self.sub_widgets.append(w)

	def del_widget(self, w):
		self.sub_widgets = [i for i in self.sub_widgets.copy() if i !=w ]
		self.relocate()

	def add_veritcal_box(self):
		box = BoxLayout(orientation='vertical', size_hint_y=None)
		box.bind(minimum_height = box.setter('height'))
		super(TypeWriterBox, self).add_widget(box)
		return box

	def relocate(self):
		with self.fboContext():
			for b in self.children:
				b.clear_widgets()
			width = 0
			self.clear_widgets()
			self.curbox = add_vertical_box()
			for w in self.sub_widgets:
				if width + w.width > self.width:
					self.curbox = self.add_vertical_box()
					width = 0
				self.curbox.add_widget(w)

Factory.register('TypeWriterBox', TypeWriterBox)
