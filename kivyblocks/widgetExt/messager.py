from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from appPublic.Singleton import SingletonDecorator

@SingletonDecorator
class Messager:
	def __init__(self):
		self.w = Popup(content=BoxLayout(orientation='vertical'),      
					title="Error info",size_hint=(0.8,0.8))
		self.messager = TextInput(size=self.w.content.size,
				multiline=True,readonly=True)
		self.w.content.add_widget(self.messager)

	def show_error(self,e):
		self.w.title = "error"
		self.messager.text = str(e)
		self.w.open()

	def show_info(self,info):
		self.w.title = "info"
		self.messager.text = str(info)
		self.w.open()

	def hide_error(self):
		self.w.dismiss()

