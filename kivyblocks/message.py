
from kivy.factory import Factory
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, \
		OptionProperty
from kivy.uix.image import AsyncImage
from .utils import *
from .baseWidget import Modal, Text, HBox,VBox, TimedModal
from .widget_css import register_css
from .clickable import ClickableIconText
from .toggleitems import PressableBox

error_default_title_css = {
	"bgcolor":[0.88,0,0,1],
	"fgcolor":[0.12,0.12,0.12,1]
}

conform_default_title_css = {
	"bgcolor":[0.88,0.88,0.88,1],
	"fgcolor":[0.12,0.12,0.12,1]
}
conform_default_body_css = {
	"bgcolor":[0.92,0.92,0.92,1],
	"fgcolor":[0.16,0.16,0.16,1]
}

conform_button_default_css = {
	"bgcolor":[0.05,0.85,0.05,1],
	"fgcolor":[0.95,0.95,0.95,1]
}

cancel_button_default_css = {
	"bgcolor":[0.85, 0.5, 0.5, 1],
	"fgcolor":[0.9, 0.90, 0.9, 1]
}

register_css('conform_default_title_css', conform_default_title_css)
register_css('message_default_title_css', conform_default_title_css)
register_css('error_default_title_css', error_default_title_css)
register_css('conform_default_body_css', conform_default_body_css)
register_css('message_default_body_css', conform_default_body_css)
register_css('conform_button_default_css', conform_button_default_css)
register_css('cancel_button_default_css', cancel_button_default_css)

class Message(TimedModal):
	title = StringProperty(None)
	default_title = 'Message'
	default_message = 'Message'
	title_icon = StringProperty(blockImage('info.png'))
	message = StringProperty(None)
	body_css = StringProperty('message_default_body_css')
	title_css = StringProperty('message_default_title_css')
	show_position = OptionProperty('br', options=['tl','tc','tr',
													'cl','cc','cr',
													'bl','bc','br'])
	width_c = NumericProperty(15)
	height_c = NumericProperty(6)
	def __init__(self, **kw):
		SUPER(Message, self, kw)
		self.size_hint = None, None
		self.set_position()
		b = VBox(csscls=self.title_css)
		b1 = HBox(size_hint_y=None, height=CSize(2))
		b1.add_widget(AsyncImage(source=self.title_icon,
									size_hint=[None,None],
									height=CSize(1.2),
									width=CSize(1.2)))
		b1.add_widget(Text(otext=self.title or self.default_title,
									font_size=CSize(1.2),
									i18n=True,
									wrap=True,
									halign='left',
									valign='center',
									))
		b.add_widget(b1)
		b2 = HBox(csscls=self.body_css)
		b2.add_widget(Text(text=self.message or self.default_message,
									i18n=True,
									wrap=True,
									halign='left',
									size_hint=(1,1),
									font_size=CSize(1)))
		b.add_widget(b2)
		self.add_widget(b)
	
	def on_size(self, *args):
		self.set_position()
		try:
			super().on_size(*args)
		except:
			pass

	def set_position(self):
		# self.pos_hint = None, None
		self.size_hint = None, None
		self.width = CSize(self.width_c)
		self.height = CSize(self.height_c)
		xn = self.show_position[1]
		yn = self.show_position[0]

		if xn == 'l':	
			self.anchor_x = 'left'
		elif xn == 'c':
			self.anchor_x = 'center'
		else:
			self.anchor_x = 'right'
		if yn == 't':
			self.anchor_y = 'top'
		elif yn == 'c':
			self.anchor_y = 'center'
		else:
			self.anchor_y = 'bottom'

class Error(Message):
	default_title = 'Error'
	default_message = 'Error message'
	title_icon = StringProperty(blockImage('error.png'))
	title_css = StringProperty('error_default_title_css')

class Conform(Modal):
	title = StringProperty(None)
	title_icon = StringProperty(None)
	message = StringProperty(None)
	conform_icon = StringProperty(None)
	cancel_icon = StringProperty(None)
	title_css = StringProperty('conform_default_title_css')
	body_css = StringProperty('conform_default_body_css')
	conform_css = StringProperty('conform_button_default_css')
	cancel_css = StringProperty('cancel_button_default_css')
	def __init__(self, **kw):
		super(Conform, self).__init__(**kw)
		self.register_event_type('on_cancel')
		self.register_event_type('on_conform')
		self.auto_dismiss = False
		b = VBox(csscls=self.title_css)
		b1 = HBox(size_hint_y=None, height=CSize(2))
		b1.add_widget(AsyncImage(source=self.title_icon or \
									blockImage('question.png'),
									size_hint=[None,None],
									height=CSize(1.2),
									width=CSize(1.2)))
		b1.add_widget(Text(otext=self.title or 'Conform',
									font_size=CSize(1.2),
									i18n=True,
									wrap=True,
									halign='left',
									valign='center',
									))
		b.add_widget(b1)
		b2 = HBox(csscls=self.body_css)
		
		b2.add_widget(Text(text=self.message or 'Please conform',
									i18n=True,
									wrap=True,
									halign='left',
									size_hint=(1,1),
									font_size=CSize(1)))
		b.add_widget(b2)
		b3 = HBox(size_hint_y=None, 
					height=CSize(2), 
					csscls=self.body_css)
		w_cancel = ClickableIconText(text='Cancel',
							source=self.cancel_icon or
									blockImage('cancel.png'),
							img_kw={
								"size_hint":[None, None],
								"height":CSize(1),
								"width":CSize(1)
							},
							csscls=self.cancel_css
							)
		w_conform = ClickableIconText(text='Conform',
							source=self.conform_icon or
									blockImage('question.png'),
							img_kw={
								"size_hint":[None, None],
								"height":CSize(1),
								"width":CSize(1)
							},
							csscls=self.conform_css
							)
		w_cancel.bind(on_press=self.cancel_press)
		w_conform.bind(on_press=self.conform_press)

		b3.add_widget(w_conform)
		b3.add_widget(w_cancel)
		b.add_widget(b3)
		self.add_widget(b)

	def cancel_press(self,o, v=None):
		self.dispatch('on_cancel')

	def conform_press(self, o, v=None):
		self.dispatch('on_conform')

	def on_cancel(self):
		self.dismiss()

	def on_conform(self):
		self.dismiss()


