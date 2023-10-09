from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from ..widget_css import WidgetCSS

class Messager:
	def __init__(self, show_time=0, title=None, **kw):
		self.show_time = show_time
		self.title = title if title else 'Message'
		self.time_task = None
		self.w = Popup(content=BoxLayout(orientation='vertical'),      
						title=self.title,
						size_hint=(0.8,0.8), **kw)
		self.messager = TextInput(size=self.w.content.size,
				background_color=[0.9,0.9,0.9,1],
				foreground_color=[0.3,0.3,0.3,1],
				multiline=True,readonly=True)
		self.w.content.add_widget(self.messager)

	def set_time_task(self):
		if self.show_time:
			self.time_task = Clock.schedule_once(self.hide,
					self.show_time)
	def show_error(self,e):
		self.messager.text = '%s[error]%s\n' % (self.messager.text,str(e))
		self.w.open()
		self.set_time_task()

	def clear_messages(self):
		self.messager.text = ''

	def show_info(self,info):
		self.messager.text = '%s[info]%s\n' % (self.messager.text, info)
		self.w.open()
		self.set_time_task()

	def hide(self, *args):
		if self.time_task:
			self.time_task.cancel()
			self.time_task = None
		self.w.dismiss()

