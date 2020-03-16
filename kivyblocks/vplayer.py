import os
import sys
import time
from kivy.utils import platform
from traceback import print_exc
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.video import Video
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger

from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, \
    NumericProperty, DictProperty, OptionProperty
from pythonosc import dispatcher, osc_server
from ffpyplayer.tools import set_log_callback
from .utils import *
from .baseWidget import PressableImage

desktopOSs=[
	"win",
	"linux",
	"macosx"
]

logger_func = {'quiet': Logger.critical, 'panic': Logger.critical,
               'fatal': Logger.critical, 'error': Logger.error,
               'warning': Logger.warning, 'info': Logger.info,
               'verbose': Logger.debug, 'debug': Logger.debug}

othersplatforms=['ios','android']

class BaseVPlayer(FloatLayout):
	fullscreen = BooleanProperty(False)
	def __init__(self,vfile=None):
		super().__init__()
		self.register_event_type('on_source_error')
		Window.allow_screensaver = False
		self._video = Video(allow_stretch=True,pos_hint={'x': 0, 'y': 0},size_hint=(1,1))
		self.add_widget(self._video)
		self.ffplayer = None
		if type(vfile) == type([]):
			self.playlist = vfile
		else:
			self.playlist = [vfile]
		self.curplay = 0
		self._video.bind(eos=self.video_end)
		self._video.bind(state=self.on_state)
		set_log_callback(self.ffplayerLog)
		self.play()
		if hasattr(self._video._video, '_ffplayer'):
			self.ffplayer = self._video._video._ffplayer

	def on_source_error(self,o,v):
		Logger.info('safecorner: {} error'.format(v))

	def ffplayerLog(self, msg, level):
		msg = msg.strip()
		if msg:
			logger_func[level]('yffpyplayer: {}'.format(msg))
		if level == 'error' and self._video.source in msg:
			self.dispatch('on_source_error',self,self._video.source)

	def play(self,o=None,v=None):
		if self.curplay >= 0:
			self._video.source = self.playlist[self.curplay]
			self._video.state = 'play'
	
	def on_playend(self,o=None,v=None):
		pass

	def addPlaylist(self,lst):
		self.playlist += lst

	def video_end(self,t,v):
		pass

	def on_state(self,o,v):
		if self._video.state == 'play':
			Window.allow_screensaver = False
		else:
			Window.allow_screensaver = True
		print('onstate()',o,v,self._video.state)

	def on_fullscreen(self, instance, value):
		window = self.get_parent_window()
		print('window.size=',window.size,'Window size=',Window.size)
		if not window:
			Logger.warning('VideoPlayer: Cannot switch to fullscreen, '
						   'window not found.')
			if value:
				self.fullscreen = False
			return
		if not self.parent:
			Logger.warning('VideoPlayer: Cannot switch to fullscreen, '
						   'no parent.')
			if value:
				self.fullscreen = False
			return

		if value:
			Window.fullscreen = True

			self._fullscreen_state = state = {
				'parent': self.parent,
				'pos': self.pos,
				'size': self.size,
				'pos_hint': self.pos_hint,
				'size_hint': self.size_hint,
				'window_children': window.children[:]}

			if platform in desktopOSs:
				Window.maximize()
			# remove all window children
			for child in window.children[:]:
				window.remove_widget(child)

			# put the video in fullscreen
			if state['parent'] is not window:
				state['parent'].remove_widget(self)
			window.add_widget(self)

			# ensure the video widget is in 0, 0, and the size will be
			# readjusted
			self.pos = (0, 0)
			self.size = (100, 100)
			self.pos_hint = {}
			self.size_hint = (1, 1)
		else:
			Window.fullscreen = False
			state = self._fullscreen_state
			window.remove_widget(self)
			for child in state['window_children']:
				window.add_widget(child)
			self.pos_hint = state['pos_hint']
			self.size_hint = state['size_hint']
			self.pos = state['pos']
			self.size = state['size']
			if state['parent'] is not window:
				state['parent'].add_widget(self)
			if platform in desktopOSs:
				Window.restore()

	def endplay(self,btn):
		self._video.seek(1.0,precise=True)

	def replay(self,btn):
		self._video.seek(0.0,precise=True)

	def audioswitch(self,btn):
		print('*********AUDIOSwitch 1**************', self.ffplayer)
		if self.ffplayer is not None:
			print('*********AUDIOSwitch 2**************')
			self.ffplayer.request_channel('audio')

	def setVolume(self,obj,v):
		self._video.volume = v

	def setPosition(self,obj,v):
		self._video.seek(v)

	def mute(self,btn):
		if self._video.volume > 0.001:
			self.old_volume = self._video.volume
			self._video.volume = 0.0
		else:
			self._video.volume = self.old_volume

	def stop(self):
		self._video.state = 'stop'

	def pause(self,t=None):
		if self._video.state == 'play':
			self._video.state = 'pause'
		else:
			self._video.state = 'play'

	def __del__(self):
		pass
	
class OSCVPlayer(BaseVPlayer):
	def __init__(self,ip,port,vfile=None):
		self.ip = ip
		self.port = port
		self.dispatcher = dispatcher.Dispatcher()
		self.server = osc_server.ThreadingOSCUDPServer( (self.ip, self.port), self.dispatcher)
		BaseVPlayer.__init__(self,vfile=vfile)
		self.map('/mute',self.mute)
		self.map('/pause',self.pause)
		self.map('/atrack',self.audioswitch)
		self.map('/endplay',self.endplay)
		self.map('/replay',self.replay)
		self.map('/setvalume',self.setVolume)
		self.map('/setposition',self.setPosition)
		self.map('/next',self.next)
	
		self.server.serve_forever()
		self.fullscreen = True
		label = Label(text='%s %d' % (self.ip,self.port), font_size=CSize(2))
		label.size = self.width - label.width, 0
		self.add_widget(label)

	def next(self,obj):
		self.source = self.vfile + '?t=%f' % time.time()

	def map(self,p,f):
		self.dispatcher.map(p,f,None)

class VPlayer(BaseVPlayer):
	def __init__(self,vfile=None,
			playlist=None,
			loop=False
		):
		super().__init__(vfile=vfile)
		self.loop = loop
		self.menubar = None
		self._popup = None
		self.menu_status = False
		self.manualMode = False
		self.update_task = None
		self.pb = None
		if vfile:
			if type(vfile) == type([]):
				self.playlist = vfile
			else:
				self.playlist = [vfile]
			self.curplay = 0
			self.play()
		else:
			self.playlist = []
			self.curplay = -1
		self._video.bind(on_touch_down=self.show_hide_menu)
		self.register_event_type('on_playend')
	
	def video_end(self,t,v):
		self.curplay += 1
		if not self.loop and self.curplay >= len(self.playlist):
			self.dispatch('on_playend')
			print('*****EOS return *************')
			self.beforeDestroy()
			return
		self.curplay = self.curplay % len(self.playlist)
		self._video.source = self.playlist[self.curplay]

	def totime(self,dur):
		h = dur / 3600
		m = dur % 3600 / 60
		s = dur % 60
		return '%02d:%02d:%02d' % (h,m,s)
		
	def createProgressBar(self):
		if self.pb is None:
			self.pb = BoxLayout(orientation='horizontal',
				size_hint = (0.99,None),height=CSize(1.4))
			self.curposition = Label(text='0',width=CSize(4),
				size_hint_x=None)
			self.curposition.align='right'
			self.maxposition = Label(text=self.totime(self._video.duration),
				width=CSize(4),size_hint_x=None)
			self.maxposition.align = 'left'
			self.slider = Slider(min=0, 
				max=self._video.duration, 
				value=0, 
				orientation='horizontal', 
				step=0.01)
			self.slider.bind(on_touch_down=self.enterManualMode)
			self.slider.bind(on_touch_up=self.endManualMode)
			self.manual_mode=False

			self.pb.add_widget(self.curposition)
			self.pb.add_widget(self.slider)
			self.pb.add_widget(self.maxposition)
			self.menubar.add_widget(self.pb)

	def enterManualMode(self,obj,touch):
		if not self.slider.collide_point(*touch.pos):
			return
		self.manualMode = True

	def endManualMode(self,obj,touch):
		if not self.manualMode:
			return
		if self._video.duration < 0.0001:
			return
		self._video.seek(self.slider.value/self._video.duration)
		self.manualMode = False

	def update_slider(self,t):
		if self.pb is None:
			return
		self.curposition.text = self.totime(self._video.position)
		if not self.manualMode:
			self.slider.value = self._video.position
			self.slider.max = self._video.duration
		self.maxposition.text = self.totime(self._video.duration)

	def __del__(self):
		self.beforeDestroy()

	def beforeDestroy(self):
		print('beforeDestroy() called')
		self._video.state = 'stop'
		return True

	def show_hide_menu(self,obj,touch):
		if not self.collide_point(*touch.pos):
			print('not inside the player')
			return 

		if touch.is_double_tap:
			self.fullscreen = False if self.fullscreen else True
			print('doube_tap')
			return 

		if not self.menubar:
			self.buildMenu()
			return

		if self.menu_status:
			self.remove_widget(self.menubar)
		else:
			self.add_widget(self.menubar)
		self.menu_status = not self.menu_status

	def buildMenu(self):
		self.menubar = BoxLayout(orientation='horizontal',
			size_hint_y=None,height=CSize(1.4))
		self.btn_pause = PressableImage(source=blockImage('pause.jpg'),
					size_hint=(None,None),
					size=CSize(3,3)
		)
		if self._video.state == 'pause':
			self.btn_pause.source = blockImage('play.jpg')
		self.btn_pause.bind(on_press=self.pause)
		self.menubar.add_widget(self.btn_pause)
		self.btn_mute = PressableImage(source=blockImage('mute.jpg'),
					size_hint=(None,None),
					size=CSize(3,3)
		)
		self.btn_mute.bind(on_press=self.mute)
		self.menubar.add_widget(self.btn_mute)
		btn_cut = PressableImage(source=blockImage('next.jpg'),
				size_hint=(None,None),
				size=CSize(3,3)
		)
		btn_cut.bind(on_press=self.endplay)
		self.menubar.add_widget(btn_cut)
		btn_replay = PressableImage(source=blockImage('replay.jpg'),
				size_hint=(None,None),
				size=CSize(3,3)
		)
		btn_replay.bind(on_press=self.replay)
		self.menubar.add_widget(btn_replay)

		self.btn_audioswitch = PressableImage( \
					source=blockImage('musictrack.jpg'),
				size_hint=(None,None),
				size=CSize(3,3)
		)
					
		self.btn_audioswitch.bind(on_press=self.audioswitch)
		self.menubar.add_widget(self.btn_audioswitch)
		slider = Slider(min=0,
                                max=1,
                                value=self._video.volume,
                                orientation='horizontal',
								size_hint=(None,None),
								height = CSize(2),
								width = CSize(10),
                                step=0.07)
		slider.bind(on_touch_up=self.setVolume)
		self.menubar.add_widget(slider)
		self.menubar.pos = CSize(0,0)
		self.createProgressBar()
		self.add_widget(self.menubar)
		self.menu_status = True

	def setVolume(self,obj,v=None):
		BaseVPlayer.setVolume(self,obj,obj.value)

	def mute(self,btn):
		BaseVPlayer.mute(self,btn)
		if self.menubar:
			if self._video.volume < 0.001:
				btn.source = blockImage('volume.jpg')
			else:
				btn.source = blockImage('mute.jpg')

	def pause(self,t=None):
		BaseVPlayer.pause(self,t)
		if self.menubar:
			if self._video.state == 'pause':
				self.btn_pause.source  = blockImage('play.jpg')
			else:
				self.btn_pause.source = blockImage('pause.jpg')

	def on_state(self,o,v):
		BaseVPlayer.on_state(self,o,v)
		if self._video.state == 'play':
			self.update_task = Clock.schedule_interval(self.update_slider,1)
		else:
			if self.update_task:
				self.update_task.cancel()
			self.update_task = None

if __name__ == '__main__':
	class MyApp(App):
		def build(self):
			vf = None
			if len(sys.argv) > 1:
				vf = sys.argv[1:]
			self.player = VPlayer(vfile=vf,
				loop=True,
				can_openfile=True,
				can_move = True,
				can_cut=True,
				can_replay=True,
				can_changevolume = True
			)
			return self.player

	MyApp().run()
