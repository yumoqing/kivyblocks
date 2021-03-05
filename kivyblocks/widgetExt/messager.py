from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from appPublic.Singleton import SingletonDecorator

@SingletonDecorator
class Messager:
	def __init__(self, show_time=0):
		self.show_time = show_time
		self.time_task = None
		self.w = Popup(content=BoxLayout(orientation='vertical'),      
					title="Error info",size_hint=(0.8,0.8))
		self.messager = TextInput(size=self.w.content.size,
				multiline=True,readonly=True)
		self.w.content.add_widget(self.messager)

	def set_time_task(self):
		if self.show_time:
			self.time_task = Clock.schedule_once(self.hide,
					self.show_time)
	def show_error(self,e):
		self.w.title = "error"
		self.messager.text = str(e)
		self.w.open()
		self.set_time_task()

	def show_info(self,info):
		self.w.title = "info"
		self.messager.text = str(info)
		self.w.open()
		self.set_time_task()

	def hide(self, *args):
		if self.time_task:
			self.time_task.cancel()
			self.time_task = None
		self.w.dismiss()

