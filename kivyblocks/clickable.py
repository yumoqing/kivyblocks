from functools import partial
from kivy.logger import Logger
from kivy.uix.behaviors import TouchRippleButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
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

	def on_press(self,o=None):
		pass

class ClickableText(ClickableBox):
	text = StringProperty(' ')
	def __init__(self, **kw):
		super(ClickableText, self).__init__(**kw)
		self.txt_w = Text(text=self.text, i18n=True)
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
	source=StringProperty('none')

class ToggleImage(
class PressableBox(TouchRippleButtonBehavior, Box):
	normal_css = StringProperty("default")
	actived_css = StringProperty("default")
	box_actived = BooleanProperty(False)
	def __init__(self,
				border_width=1,
				user_data=None,
				radius=[],
				**kw):
		super(PressableBox, self).__init__(
			padding=[border_width,
			border_width,
			border_width,
			border_width],
			radius=radius,
			**kw)
		self.border_width = border_width
		self.user_data = user_data
		self.actived = False
		self.csscls = self.normal_css

	def active(self, flag):
		self.box_actived = flag

	def on_box_actived(self, o, v):
		if self.box_actived:
			self.csscls = self.actived_css
		else:
			self.csscls = self.normal_css

	def on_press(self,o=None):
		self.box_actived = True


	def setValue(self,d):
		self.user_data = d

	def getValue(self):
		return self.user_data

