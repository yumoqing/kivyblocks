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
		
	def on_source(self,o,s):
		Logger.info('APlayer:self.source=%s',self.source)
		self.ap = SoundFFPy(source=self.source)
		if not self.ap:
			return

		self.ap.bind(on_play=self.begin_play)
		self.ap.bind(on_stop=self.end_play)
		self.play()

	def __del__(self):
		self.stop()

	def stop(self):
		if not self.ap:
			return
		self.ap.stop()

	def play(self):
		if not self.ap:
			return 
		self.ap.play()
		
	def begin_play(self,obj):
		pass

	def end_play(self,obj):
		del self.ap
		self.ap = None
		
	def endplay(self,btn):
		self.ap.seek(self.ap.length - 0.01 )

	def replay(self,btn):
		self.ap.seek(0)

	def volumeinc(self,btn):
		self.ap.volume += 0.05
		if self.ap.volume > 1.0:
			self.ap.volume = 1.0

	def volumedec(self,btn):
		self.ap.volume -= 0.05
		if self.ap.volume < 0.0:
			self.ap.volume = 0.0

	def moveback(self,btn):
		f = self.ap.get_pos()
		self.ap.seek(f - 2)

	def moveforward(self,btn):
		f = self.ap.get_pos()
		self.ap.seek(f + 2)

if __name__ == '__main__':
	class MyApp(App):
		def build(self):
			af = None
			if len(sys.argv) > 1:
				af = sys.argv[1:]
			return APlayer()
	MyApp().run()
