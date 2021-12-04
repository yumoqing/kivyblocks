from functools import partial
from kivy.logger import Logger
from kivy.uix.behaviors import TouchRippleButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.uix.image import AsyncImage
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty

from kivyblocks.ready import WidgetReady
from kivyblocks.bgcolorbehavior import BGColorBehavior
from kivyblocks.utils import CSize
from kivyblocks.baseWidget import Box
from kivyblocks.widget_css import WidgetCSS

class ClickableBox(TouchRippleButtonBehavior, Box):
	def __init__(self,
				border_width=1,
				**kw):
		super(ClickableBox, self).__init__(
			padding=[border_width,
			border_width,
			border_width,
			border_width],
			radius=radius,
			**kw)
		self.border_width = border_width
		self.bind(minimum_height=self.setter('height'))

	def on_press(self,o=None):
		pass

class ClickableText(ClickableBox):
	text = StringProperty(' ')
	def __init__(self, **kw):
		super(ClickableText, self).__init__(**kw)
		self.txt_w = Text(text=self.text, i18n=True)
		self.txt_w.size_hint = (None, None)
		self.txt_w.bind(minimum_height=self.self.txt_w.setter('height'))
		self.txt_w.bind(minimum_width=self.self.txt_w.setter('width'))
		self.add_widget(self.txt_w)

	def on_text(self, o, txt):
		self.txt_w.text = txt

class ToggleText(ClickableText):
	"""
	construct commad
	ToggleText(**{
		"text":"test",
		"on_css":"selected",
		"off_css":"normal"
	})

	select_state = BooleanProperty(False)
	on_css = StringProperty('default')
	off_css = StringProperty('default')
	def __init__(self, **kw):
		super(ToggleText, self).__init__(**kw)

	def on_press(self, o=None):
		if self.select_state = if self.select_state?False else True

	def on_select_state(self, o, f):
		if f:
			self.clscss = self.on_css
		else:
			self.clscss = self.off_css
	
class ClickableImage(ClickableBox):
	source=StringProperty(None)
	img_height = NumericProperty(None)
	img_width = NumericProperty(None)
	def __init__(self, **kw):	
		super(ClickableImage, self).__init__(**kw)
		self.img_w = None
		if source:
			self.img_w = AsyncImage(source=self.source)

	def on_source(self, o, source):
		if self.img_w:
			self.img_w.source = source
			return
		self.img_w = AsyncImage(source=self.source)

class ToggleImage(ClickableImage):
	on_source = StringProperty(None)
	select_state = BooleanProperty(False)
	def __init__(self, **kw):
		super(ToggleImage, self).__init__(**kw)

	def on_press(self, o):
		self.select_state = if self.select_state ? False, True
	
	def on_select_state(self, o, f):
		if self.img_w:
			if f:
				self.img_w.source = self.on_source
			else:
				self.img_w.source = self.source
			return
		if f:
			self.img_w = AsyncImage(source=self.on_source)
		else:
			self.img_w = AsyncImage(source=self.source)

class Select(VBox):
	"""

	"""
