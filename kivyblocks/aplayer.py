import sys
import os
from kivy.logger import Logger
from kivy.app import App
from kivy.properties import StringProperty
from kivy.core.audio.audio_ffpyplayer import SoundFFPy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, \
    NumericProperty, DictProperty, OptionProperty

class APlayer(BoxLayout):
	source = StringProperty('')
	def __init__(self,afile=None,loop=False,
			can_openfile=False,
			can_changevolume=False,
			can_cut = False,
			can_replay = False,
			can_move=False):
		super().__init__(orientation='vertical')
		self.ap = None
		self.end_flag = False
		
	def on_source(self,o,s):
		if self.ap:
			self.ap.stop()
		self.ap = SoundFFPy(source=self.source)
		if not self.ap:
			return
		self.play()

	def __del__(self):
		self.end_flag=True
		self.stop()

	def stop(self):
		if not self.ap:
			return
		self.ap.stop()
		self.ap = None

	def play(self):
		if not self.ap:
			return 
		self.ap.bind(on_stop=self.end_play)
		self.ap.play()
		
	def end_play(self,obj):
		self.ap = None
		
if __name__ == '__main__':
	class MyApp(App):
		def build(self):
			af = None
			if len(sys.argv) > 1:
				af = sys.argv[1:]
			return APlayer()
	MyApp().run()
