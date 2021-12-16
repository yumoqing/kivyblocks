from functools import partial
from kivy.logger import Logger
from kivy.uix.behaviors import TouchRippleButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.uix.image import AsyncImage
from kivy.properties import NumericProperty, DictProperty, \
		ObjectProperty, StringProperty, BooleanProperty

from kivyblocks.ready import WidgetReady
from kivyblocks.bgcolorbehavior import BGColorBehavior
from kivyblocks.utils import CSize
from kivyblocks.baseWidget import Box, Text
from kivyblocks.widget_css import WidgetCSS

class TinyText(Text):
	def on_texture_size(self, o, ts):
		self.size = self.texture_size
		print('TinyText:texture_size=', self.texture_size)

class ClickableBox(TouchRippleButtonBehavior, Box):
	def __init__(self,
				border_width=1,
				**kw):
		super(ClickableBox, self).__init__(
			padding=[border_width,
			border_width,
			border_width,
			border_width],
			**kw)
		self.border_width = border_width
		# self.bind(minimum_height=self.setter('height'))
		# self.bind(minimum_width=self.setter('width'))

	def on_press(self,o=None):
		pass

class ClickableText(ClickableBox):
	text = StringProperty(' ')
	def __init__(self, **kw):
		print('ClickableText begin inited')
		self.txt_w = None
		super(ClickableText, self).__init__(**kw)
		self.txt_w = TinyText(text=self.text, i18n=True)
		self.txt_w.bind(texture_size=self.reset_size)
		self.add_widget(self.txt_w)
		self.txt_w.size_hint = (None, None)
		self.txt_w.size = self.txt_w.texture_size
		#self.txt_w.bind(minimum_height=self.txt_w.setter('height'))
		#self.txt_w.bind(minimum_width=self.txt_w.setter('width'))
		print('ClickableText inited')

	def reset_size(self, o, s):
		self.size_hint = (None,None)
		self.size = self.txt_w.texture_size

	def on_text(self, o, txt):
		print('on_text fired')
		if self.txt_w:
			self.txt_w.text = self.text
			
			

class ClickableIconText(ClickableText):
	source = StringProperty(None)
	img_kw = DictProperty({})
	def __init__(self, **kw):
		self.img_w = None
		super(ClickableIconText, self).__init__(**kw)
		print('ClickableIconText inited')

	def reset_size(self, o, s):
		self.size_hint = (None,None)
		if self.orientation == 'horizontal':
			self.height = max(self.txt_w.texture_size[1], self.img_w.height)
			self.width = self.txt_w.texture_size[0] + self.img_w.width
		else:
			self.height = self.txt_w.texture_size[1] + self.img_w.height
			self.width = max(self.txt_w.texture_size[0], self.img_w.width)


	def on_source(self, o, source):
		if self.img_w:
			self.img_w.source = source
			return
		self.img_w = AsyncImage(source=self.source, **self.img_kw)
		self.add_widget(self.img_w, index=-1)

class ToggleText(ClickableText):
	"""
	construct commad
	ToggleText(**{
		"text":"test",
		"css_on":"selected",
		"css_off":"normal"
	})
	"""

	select_state = BooleanProperty(False)
	css_on = StringProperty('default')
	css_off = StringProperty('default')
	def __init__(self, **kw):
		super(ToggleText, self).__init__(**kw)

	def toggle(self):
		self.select_state = False if self.select_state else True

	def select(self, flag):
		if flag:
			self.select_state = True
		else:
			self.select_state = False

	def state(self):
		return self.select_state

	def on_select_state(self, o, f):
		self.csscls = self.css_on if f else self.css_off
		print(f'using {self.csscls}')
	
class ToggleIconText(ToggleText):
	"""
	{
		"orientation",
		"text",
		"css_on",
		"css_off",
		"source_on",
		"source_off"
	}
	"""
	source_on = StringProperty(None)
	source_off = StringProperty(None)
	source = StringProperty(None)
	img_kw = DictProperty({})
	def __init__(self, **kw):
		self.img_w = None
		super(ToggleIconText, self).__init__(**kw)
		self.source = self.source_off
		self.img_w = AsyncImage(source=self.source, **self.img_kw)
		self.add_widget(self.img_w, index=-1)
		
	def reset_size(self, o, s):
		self.size_hint = (None,None)
		if self.orientation == 'horizontal':
			self.height = max(self.txt_w.texture_size[1], self.img_w.height)
			self.width = self.txt_w.texture_size[0] + self.img_w.width
		else:
			self.height = self.txt_w.texture_size[1] + self.img_w.height
			self.width = max(self.txt_w.texture_size[0], self.img_w.width)
		print(f'ToggleIconText:w,h={self.width},{self.height}')

	def on_select_state(self, o, f):
		super(ToggleIconText, self).on_select_state(o,f)
		self.source = self.source_on if f else self.source_off

	def on_source(self, o, source):
		if self.img_w:
			self.img_w.source = self.source

class ClickableImage(ClickableBox):
	source=StringProperty(None)
	img_kw = DictProperty(None)
	def __init__(self, **kw):	
		self.img_w = None
		super(ClickableImage, self).__init__(**kw)
		self.img_w = AsyncImage(source=self.source, **self.img_kw)
		self.add_widget(self.img_w)

	def on_source(self, o, source):
		if self.img_w:
			self.img_w.source = source
			return
		self.img_w = AsyncImage(source=self.source, **self.img_kw)
		self.add_widget(self.img_w)

class ToggleImage(ClickableImage):
	source_on = StringProperty(None)
	source_off = StringProperty(None)
	select_state = BooleanProperty(False)
	def __init__(self, **kw):
		super(ToggleImage, self).__init__(**kw)
		self.source = self.source_on

	def toggle(self):
		self.select_state = False if self.select_state else True

	def select(self, flag):
		if flag:
			self.select_state = True
		else:
			self.select_state = False

	def state(self):
		return self.select_state

	def on_select_state(self, o, f):
		if f:
			self.source = self.source_on
		else:
			self.source = self.source_off

r = Factory.register
r('TinyText', TinyText)
r('ClickableBox', ClickableBox)
r('ClickableText',ClickableText)
r('ClickableIconText',ClickableIconText)
r('ToggleText',ToggleText)
r('ToggleIconText',ToggleIconText)
r('ClickableImage',ClickableImage)
r('ToggleImage',ToggleImage)
