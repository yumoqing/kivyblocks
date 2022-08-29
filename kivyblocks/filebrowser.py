from kivy.uix.floatlayout import FloatLayout
from kivy.event import EventDispatcher
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView, FileChooserIconView
from kivyblocks.i18n import I18n
from kivyblocks.utils import blockImage,CSize
from kivyblocks.baseWidget import PressableImage, StrInput

import os

class FileLoaderBrowser(Popup):
	def __init__(self,rootpath='/', title='load file', choose_dir=False, **kwargs):
		i18n = I18n()
		self.content = BoxLayout(orientation='vertical')
		Popup.__init__(self, content = self.content, 
					title=i18n(title), 
					size_hint=(0.9,0.9))
		self.register_event_type('on_selected')
		self.choose_dir = choose_dir

		self.list_widget = FileChooserListView(rootpath=rootpath)
		self.icon_widget = FileChooserIconView(rootpath=rootpath)
		self.list_widget.bind(on_touch_up=self.on_release)
		self.icon_widget.bind(on_touch_up=self.on_release)
		self.list_widget.bind(on_submit=self.do_submit)
		self.icon_widget.bind(on_submit=self.do_submit)
		self.btn_load = Button(text=i18n('load'),size_hint=(None,None),
						size=CSize(8,2))
		self.btn_list_view = PressableImage(	\
						source=blockImage('list_view.png'),
						size_hint=(None,None),
						size=CSize(2,2))
		self.btn_icon_view = PressableImage(	\
						source=blockImage('icon_view.png'),
						size_hint=(None,None),
						size=CSize(2,2))
		self.btn_list_view.bind(on_press=self.change_view_mode)
		self.btn_icon_view.bind(on_press=self.change_view_mode)
		self.btn_load.bind(on_release=self.do_load)
		self.control_box = BoxLayout(orientation='horizontal',
				size_hint_y=None,
				height=CSize(2.5)
				)
		self.txt_input = Factory.StrInput()
		self.view_mode = 'list_view'
		self.show_list_view()

	def on_selected(self,fn):
		print(fn,'selected')

	def on_release(self,o,v=None):
		Clock.schedule_once(self.set_txt_input,0.4)

	def set_txt_input(self,t=None):
		self.txt_input.text = self.cur_widget.path

	def target_selected(self):
		fn = self.txt_input.text
		if not self.choose_dir and os.path.isdir(fn):
			return 
		if self.choose_dir and os.path.isfile(fn):
			fn = os.path.dirname(fn)
		self.dispatch('on_selected',fn)
		self.dismiss()

	def do_submit(self,o,a,b):
		if not self.cur_widget.selection:
			return
		self.txt_input.text = self.cur_widget.selection[0]
		self.target_selected()

	def do_load(self,o,d=None):
		if self.cur_widget.selection:
			self.txt_input.text = self.cur_widget.selection[0]
		if self.txt_input.text == '':
			return
		self.target_selected()

	def change_view_mode(self,o,v=None):
		self.content.clear_widgets()
		if self.view_mode == 'list_view':
			self.show_icon_view()
		else:
			self.show_list_view()

	def show_list_view(self):
		self.cur_widget = self.list_widget
		self.view_mode = 'list_view'
		self.cur_widget.path = self.icon_widget.path
		self.content.add_widget(self.list_widget)
		self.content.add_widget(self.txt_input)
		self.content.add_widget(self.control_box)
		self.control_box.clear_widgets()
		self.control_box.add_widget(self.btn_load)
		self.control_box.add_widget(self.btn_list_view)

	def show_icon_view(self):
		self.cur_widget = self.icon_widget
		self.view_mode = 'icon_view'
		self.cur_widget.path = self.list_widget.path
		self.content.add_widget(self.icon_widget)
		self.content.add_widget(self.txt_input)
		self.content.add_widget(self.control_box)
		self.control_box.clear_widgets()
		self.control_box.add_widget(self.btn_load)
		self.control_box.add_widget(self.btn_icon_view)

if __name__ == '__main__':
	from kivy.app import App
	class Test(App):
		def build(self):
			x = FileLoaderBrowser()
			return x
	app = Test()
	app.run()
