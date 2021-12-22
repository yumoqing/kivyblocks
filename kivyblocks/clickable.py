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
from kivyblocks.utils import CSize, SUPER
from kivyblocks.baseWidget import Box, Text
from kivyblocks.widget_css import WidgetCSS

class TinyText(Text):
	def __init__(self, **kw):
		SUPER(TinyText, self, kw)
		self.on_texture_size(self, (1,1))

	def on_texture_size(self, o, ts):
		self._label.refresh()
		self.size = self.texture_size

class ClickableBox(TouchRippleButtonBehavior, Box):
	def __init__(self,
				border_width=1,
				**kw):
		SUPER(ClickableBox, self, kw)
		self.border_width = border_width
		# self.bind(minimum_height=self.setter('height'))
		# self.bind(minimum_width=self.setter('width'))
		self.bind(children=self.reset_size)

	def reset_size(self, o, s):
		self.size_hint = (None,None)
		if self.orientation == 'horizontal':
			self.height = max([c.height for c in self.children])
			self.width = sum([c.width for c in self.children])
		else:
			self.height = sum([c.height for c in self.children])
			self.width = max([c.width for c in self.children])

	def on_press(self,o=None):
		pass

class ClickableText(ClickableBox):
	text = StringProperty(' ')
	fontsize = NumericProperty(1)
	def __init__(self, **kw):
		print('ClickableText begin inited')
		self.txt_w = None
		SUPER(ClickableText, self, kw)
		self.txt_w = TinyText(otext=self.text, 
						i18n=True,
						font_size=CSize(self.fontsize))
		self.txt_w.bind(texture_size=self.reset_size)
		self.add_widget(self.txt_w)
		self.txt_w.size_hint = (None, None)
		self.txt_w.size = self.txt_w.texture_size

	def on_text(self, o, txt):
		if self.txt_w:
			self.txt_w.text = self.text
			
			

class ClickableIconText(ClickableText):
	source = StringProperty(None)
	img_kw = DictProperty({})
	def __init__(self, **kw):
		self.img_w = None
		SUPER(ClickableIconText, self, kw)
		print('ClickableIconText inited')

	def on_source(self, o, source):
		if self.img_w:
			self.img_w.source = source
			return
		self.img_w = AsyncImage(source=self.source, **self.img_kw)
		self.add_widget(self.img_w, index=len(self.children))

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
		SUPER(ToggleText, self, kw)

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
		SUPER(ToggleIconText, self, kw)
		self.source = self.source_off
		self.img_w = AsyncImage(source=self.source, **self.img_kw)
		self.add_widget(self.img_w, index=len(self.children))
		
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
		SUPER(ClickableImage, self, kw)
		# self.img_w = AsyncImage(source=self.source, **self.img_kw)
		# self.add_widget(self.img_w)

	def on_source(self, o, source):
		if self.source is None:
			self.source = blockImage('broken.png')
		self.build_widget()

	def on_img_kw(self, o, img_kw):
		self.build_widget()

	def build_widget(self):
		if not self.source:
			return
		if not self.img_kw:
			self.img_kw = {}

		if self.img_w:
			self.img_w.source = self.source
			for k,v in self.img_kw.items():
				setattr(self.img_w, k,v)
			return
		self.img_w = AsyncImage(source=self.source, **self.img_kw)
		self.add_widget(self.img_w)

class ToggleImage(ClickableImage):
	source_on = StringProperty(None)
	source_off = StringProperty(None)
	select_state = BooleanProperty(False)
	def __init__(self, **kw):
		SUPER(ToggleImage, self, kw)
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

class CheckBox(ToggleImage):
	otext = StringProperty(None)
	def __init__(self, **kw):	
		SUPER(CheckBox, self, kw)
		self.source_on = blockImage('checkbox-on.png')
		self.source_off = blockImage('ceckbox-off.png')
		if self.otext:
			self.txt_w = TinyText(otext=self.otext, i18n=True)
			self.add_widget(self.txt_w)

	def getValue(self):
		return self.state()

	def setValue(self, v):
		self.select_state = False if v else True

r = Factory.register
r('TinyText', TinyText)
r('CheckBox', CheckBox)
r('ClickableBox', ClickableBox)
r('ClickableText',ClickableText)
r('ClickableIconText',ClickableIconText)
r('ToggleText',ToggleText)
r('ToggleIconText',ToggleIconText)
r('ClickableImage',ClickableImage)
r('ToggleImage',ToggleImage)
