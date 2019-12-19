import sys
import os
from kivy.app import App
from kivy.core.audio import SoundLoader
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
	def __init__(self,afile=None,loop=False,
			can_openfile=False,
			can_changevolume=False,
			can_cut = False,
			can_replay = False,
			can_move=False):
		super().__init__(orientation='vertical')
		self.loop = loop
		self.old_path = os.getcwd()
		self.can_openfile = can_openfile
		self.can_cut = can_cut
		self.can_replay = can_replay
		self.can_move = can_move
		self.can_changevolume = can_changevolume
		self._popup = None
		self.pb = None
		self.ap = None
		if afile is None:
			self.playlist = []
		else:
			if type(afile) == type([]):
				self.playlist = afile
			else:
				self.playlist = [afile]
		self.curplay = -1
		self.addMenu()
		if len(self.playlist) > 0:
			self.curplay = 0
			self.createSound(self.playlist[self.curplay])

	def totime(self,dur):
		h = dur / 3600
		m = dur % 3600 / 60
		s = dur % 60
		return '%02d:%02d:%02d' % (h,m,s)

	def createSound(self,source):
		self.ap = SoundLoader.load(source)
		self.ap.bind(on_play=self.begin_play)
		self.ap.bind(on_stop=self.end_play)
		self.ap.play()
		
	def begin_play(self,obj):
		if self.pb:
			return
		self.pb = BoxLayout(orientation='horizontal',
			size_hint = (0.99,None),height=40)
		self.curposition = Label(text=self.totime(self.ap.get_pos()),width=60,
			size_hint_x=None)
		self.curposition.align='right'
		self.maxposition = Label(text=self.totime(self.ap.length),
			width=60,size_hint_x=None)
		self.maxposition.align = 'left'
		max = int(self.ap.length*1000)
		self.progressbar = ProgressBar(value=0,max=max)
		self.add_widget(self.pb)
		self.pb.add_widget(self.curposition)
		self.pb.add_widget(self.progressbar)
		self.pb.add_widget(self.maxposition)
		self.pb.pos = (0,0)
		Clock.schedule_interval(self.update_progressbar,1)

	def update_progressbar(self,t):
		pos = self.ap.get_pos()
		max = self.ap.length
		self.curposition.text = self.totime(pos)
		self.progressbar.value = int(pos*1000)
		self.progressbar.max = int(max*1000)
		self.maxposition.text = self.totime(max)


	def end_play(self,obj):
		self.curplay += 1
		if not self.loop and self.curplay >= len(self.playlist):
			self.parent.remove_widget(self)
			return
		del self.ap
		self.curplay  = self.curplay % len(self.playlist)
		self.createSound(self.playlist[self.curplay])
		
	def addMenu(self):
		self.menubar = BoxLayout(orientation='horizontal',
			size_hint_y=None,height=40)
		if self.can_openfile:
			btn_open = Button(text='open')
			btn_open.bind(on_press=self.openfile)
			self.menubar.add_widget(btn_open)
		if self.can_move:
			btn_back = Button(text='<<')
			btn_forward = Button(text='>>')
			btn_forward.bind(on_press=self.moveforward)
			btn_back.bind(on_press=self.moveback)
			self.menubar.add_widget(btn_back)
			self.menubar.add_widget(btn_forward)
		if self.can_changevolume:
			btn_volumeinc = Button(text='+')
			btn_volumedec = Button(text='-')
			btn_volumeinc.bind(on_press=self.volumeinc)
			btn_volumedec.bind(on_press=self.volumedec)
			self.menubar.add_widget(btn_volumedec)
			self.menubar.add_widget(btn_volumeinc)
		if self.can_cut:
			btn_cut = Button(text='>>|')
			btn_cut.bind(on_press=self.endplay)
			self.menubar.add_widget(btn_cut)
		if self.can_replay:
			btn_replay = Button(text='replay')
			btn_replay.bind(on_press=self.replay)
			self.menubar.add_widget(btn_replay)
		self.menubar.pos = 0,45
		self.add_widget(self.menubar)
	
	def openfile(self,t):
		def afilter(path,filename):
			aexts = [
				'.wav',
				'.mp3',
				'.ape',
				'.flac'

			]
			for ext in aexts:
				if filename.endswith(ext):
					return True
			return False

		if self._popup is None:
			c = BoxLayout(orientation='vertical')
			self.file_chooser = FileChooserListView()
			self.file_chooser.filters = [afilter]
			self.file_chooser.multiselect = True
			self.file_chooser.path = self.old_path
			#self.file_chooser.bind(on_submit=self.loadFilepath)
			c.add_widget(self.file_chooser)
			b = BoxLayout(size_hint_y=None,height=35)
			c.add_widget(b)
			#cancel = Button(text='Cancel')
			#cancel.bind(on_press=self.cancelopen)
			load = Button(text='load')
			load.bind(on_press=self.playfile)
			b.add_widget(load)
			#b.add_widget(cancel)
			self._popup = Popup(title='Open file',content=c,size_hint=(0.9,0.9))
		self._popup.open()

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

	def playfile(self,object):
		self.playlist = []
		for f in self.file_chooser.selection:
			fp = os.path.join(self.file_chooser.path,f)
			self.playlist.append(fp)
		if len(self.playlist) == 0:
			return
		self._popup.dismiss()
		if self.ap is not None:
			self.ap.stop()
			return 
		self.curplay = 0
		self.createSound(self.playlist[self.curplay])



if __name__ == '__main__':
	class MyApp(App):
		def build(self):
			af = None
			if len(sys.argv) > 1:
				af = sys.argv[1:]
			return APlayer(afile=af,
                                loop=True,
                                can_openfile=True,
                                can_move = True,
                                can_cut=True,
                                can_replay=True,
                                can_changevolume = True
                        )
	MyApp().run()
