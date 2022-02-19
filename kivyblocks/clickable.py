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
from kivyblocks.utils import CSize, SUPER, blockImage
from kivyblocks.baseWidget import Box, Text
from kivyblocks.widget_css import WidgetCSS
from .uitype.factory import UiFactory, get_value
from .command_action import cmd_action

class TinyText(Text):
	def __init__(self, **kw):
		SUPER(TinyText, self, kw)
		self.size_hint = (None, None)
		self.on_texture_size(self, (1,1))

	def on_texture_size(self, o, ts):
		self.texture_update()
		self.size = self.texture_size

class ClickableBox(TouchRippleButtonBehavior, Box):
	def __init__(self,
				border_width=1,
				**kw):
		SUPER(ClickableBox, self, kw)
		self.size_hint = [None, None]
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

class _IconBehavior:
	source=StringProperty(None)
	img_kw = DictProperty(None)

	def on_source(self, o, source):
		if self.source is None:
			try:
				self.remove_widget(self.img_w)
			except:
				pass
			self.img_w = None
			return
		self.build_icon()

	def on_img_kw(self, o, img_kw):
		self.build_icon()

	def build_icon(self):
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

class _TextBehavior:
	text = StringProperty(None)
	fontsize = NumericProperty(1)

	def create_text_widget(self):
		if self.text is None:
			return
		self.txt_w = TinyText(otext=self.text, 
						i18n=True,
						font_size=CSize(self.fontsize))
		self.txt_w.font_size = CSize(self.fontsize)
		self.txt_w.bind(texture_size=self.reset_size)
		self.txt_w.size_hint = (None, None)
		self.txt_w.size = self.txt_w.texture_size
		self.add_widget(self.txt_w)

	def on_fontsize(self, o, fs):
		if self.txt_w:
			self.txt_w.font_size = CSize(self.fontsize)
			self.txt_w.texture_update()

	def on_text(self, o, txt):
		if self.text is None:
			return
		if not self.txt_w:
			return
		if self.txt_w:
			self.txt_w.text = self.text
			self.txt_w.texture_update()

class ClickableText(_TextBehavior, ClickableBox):
	def __init__(self, **kw):
		self.txt_w = None
		SUPER(ClickableText, self, kw)
		self.create_text_widget()

class ClickableIconText(_IconBehavior, _TextBehavior, ClickableBox):
	def __init__(self, **kw):
		self.txt_w = None
		self.img_w = None
		SUPER(ClickableIconText, self, kw)
		self.build_icon()
		self.create_text_widget()

class CommandBox(ClickableIconText):
	value = DictProperty(None)
	params = DictProperty(None)
	conform = DictProperty(None)
	target = StringProperty(None)
	datawidget = StringProperty(None)
	datamethod = StringProperty(None)
	url = StringProperty(None)
	rfname = StringProperty(None)
	method = StringProperty(None)
	script = StringProperty(None)
	actions = DictProperty(None)
	def on_press(self, *args):
		if self.datawidget is None:
			self.datawidget = 'self'
			self.datamethod = 'getValue'

		desc = dict(target=self.target,
			datawidget = self.datawidget,
			datamethod = self.method,
			url=self.url,
			params=self.params,
			conform = self.conform,
			rfname = self.rfname,
			method = self.method,
			script = self.script,
			actions = self.actions
		)
		cmd_action(desc, self)

	def setValue(self, value:dict):
		self.value = value

	def getValue(self):
		return self.value

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
		if source is None:
			return
		if self.img_w:
			self.img_w.source = self.source

class ClickableImage(_IconBehavior, ClickableBox):
	def __init__(self, **kw):	
		self.img_w = None
		SUPER(ClickableImage, self, kw)
		self.build_icon()

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

class SingleCheckBox(ClickableBox):
	otext = StringProperty(None)
	select_state = BooleanProperty(False)
	def __init__(self, **kw):	
		self.old_state = None
		self.register_event_type('on_changed')
		SUPER(SingleCheckBox, self, kw)
		self.source_on = blockImage('checkbox-on.png')
		self.source_off = blockImage('checkbox-off.png')
		self.select(False)
		self.create_img_w()
		if self.otext:
			self.txt_w = TinyText(otext=self.otext, i18n=True)
			self.txt_w.bind(size=self.reset_size)
			self.add_widget(self.txt_w)
		self.reset_size(self, None)

	def on_changed(self, o=None):
		pass

	def on_press(self, o=None):
		self.toggle()

	def select(self, f):
		self.select_state = f
	
	def change_img_source(self):
		self.img_w.source = self.source_on if self.select_state else \
							self.source_off

	def toggle(self):
		self.select_state = False if self.select_state else True

	def state(self):
		return self.select_state

	def on_select_state(self, o, f):
		self.change_img_source()
		self.dispatch('on_changed', self.select_state)

	def getValue(self):
		return self.state()

	def setValue(self, v):
		self.select(True if v else False)

	def create_img_w(self):
		if self.select_state:
			self.img_w = AsyncImage(source=self.source_on, 
						size_hint=(None, None),
						size=CSize(1, 1)
						)
		else:
			self.img_w = AsyncImage(source=self.source_off, 
						size_hint=(None, None),
						size=CSize(1, 1)
						)
		self.add_widget(self.img_w)
		self.img_w.bind(size=self.reset_size)

def build_checkbox(desc, rec=None):
	v = get_value(desc, rec)
	if v is None:
		v = False
	x = SingleCheckBox(select_state=v)
	return x

def build_cmdbox_view(desc, rec=None):
	vd = None
	if rec is not None:
		vd = {f:rec.get(f) for f in desc.get('data') }
	kw = {
		'text' : desc.get('label'),
		'source' : desc.get('icon'),
		'img_kw' : desc.get('img_kw',{
			'size_hint':[None, None],
			'height':CSize(1),
			'width':CSize(1)
		}),
		'rfname':desc.get('rfname'),
		'script':desc.get('script'),
		'params':desc.get('params'),
		'conform':desc.get('conform'),
		'target':desc.get('target'),
		'datawidget':desc.get('datawidget'),
		'datamethod':desc.get('datamethod'),
		'method':desc.get('method'),
		'url':desc.get('url')
	}
	if desc.get('uiparams'):
		kw.update(desc.get('uiparams'))
	x = CommandBox(**kw)
	x.setValue(vd)
	return x

UiFactory.register('checkbox', build_checkbox, build_checkbox)
UiFactory.register('cmdbox', build_cmdbox_view, build_cmdbox_view)

r = Factory.register
r('CommandBox', CommandBox)
r('TinyText', TinyText)
r('SingleCheckBox', SingleCheckBox)
r('ClickableBox', ClickableBox)
r('ClickableText',ClickableText)
r('ClickableIconText',ClickableIconText)
r('ToggleText',ToggleText)
r('ToggleIconText',ToggleIconText)
r('ClickableImage',ClickableImage)
r('ToggleImage',ToggleImage)
