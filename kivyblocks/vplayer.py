import os
import sys
import time
import threading

from appPublic.sockPackage import get_free_local_addr
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
from ffpyplayer.tools import set_log_callback
from .utils import *
from .paging import PageLoader
from .baseWidget import PressableImage
from .swipebehavior import SwipeBehavior

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
	def __init__(self,vfile=None,loop=None,mute=False):
		FloatLayout.__init__(self)
		self.loop = loop
		self.muteFlg = mute
		self.register_event_type('on_source_error')
		self.register_event_type('on_next')
		self.register_event_type('on_previous')
		Window.allow_screensaver = False
		self._video = Video(allow_stretch=True)
		self.add_widget(self._video)
		self.nextdir = None
		self.playlist = []
		self.curplay = 0
		self.old_volume = 0
		self._video.bind(state=self.on_state)
		# self._video.bind(loaded=self.playVideo) no effect
		self._video.bind(position=self.positionChanged)
		if loop:
			self.eos = 'loop'
		
		# self.bind(on_swipe_down=self.previous)
		# self.bind(on_swipe_up=self.next)
		set_log_callback(self.ffplayerLog)
		if hasattr(self._video._video, '_ffplayer'):
			self.ffplayer = self._video._video._ffplayer
		if vfile is not None:
			self.setSource(vfile)

	def on_size(self,*args):
		self._video.size = self.size
		print('****on_size()****',self.pos,self.size,self._video.pos,self._video.size)
	
	def positionChanged(self,o,v):
		if self.muteFlg:
			self._video.volume = 0

	def playVideo(self,o=None,v=None):
		# print('-------------VPlayer():playVideo()')
		self._video.state = 'play'
		self.nextdir = None

	def setSource(self,s):
		self.stop()
		self.curplay = 0
		self.playlist = [s]
		self._video.source = self.playlist[self.curplay]
		Logger.info('kivyblocks: Vplayer().setSource,s=%s',s)
		self.playVideo()

	def on_source_error(self,o,v):
		Logger.info('safecorner: {} error'.format(v))

	def on_next(self,o=None, v=None):
		pass

	def on_previous(self, o=None, v=None):
		pass

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
		else:
			Logger.info('VPlaer: self.curpay < 0')
			
	def next(self,o=None,v=None):
		self.nextdir = 'down'
		self.stop()
		self.dispatch('on_next',self)

	def previous(self,o=None,v=None):
		self.nextdir = 'up'
		self.stop()
		self.dispatch('on_previous',self)

	def on_state(self,o=None,v=None):
		if self._video.state == 'play':
			Window.allow_screensaver = False
		else:
			Window.allow_screensaver = True
		if self._video.state == 'stop':
			Logger.info('VPlayer: state==stop,nextdir=%s',self.nextdir)
			if self.nextdir is None:
				self.dispatch('on_next',self)
			self.nextdir = None

	def on_fullscreen(self, instance, value):
		window = self.get_parent_window()
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

	def endplay(self,btn=None):
		self._video.seek(1.0,precise=True)

	def replay(self,btn=None):
		self._video.seek(0.0,precise=True)

	def audioswitch(self,btn=None):
		x = self._video._video._ffplayer.request_channel('audio')

	def setVolume(self,obj,v):
		self._video.volume = v
		if v >= 0.01:
			self.muteFlg = False
		else:
			self.muteFlg = True

	def setPosition(self,obj,v):
		self._video.seek(v)

	def mute(self,btn=None):
		if self._video.volume > 0.001:
			self.old_volume = self._video.volume
			self._video.volume = 0.0
		else:
			self._video.volume = self.old_volume

	def stop(self):
		self._video.unload()

	def pause(self,t=None):
		if self._video.state == 'play':
			self._video.state = 'pause'
		else:
			self._video.state = 'play'

	def __del__(self):
		self.stop()
	
class Swipe_VPlayer(BaseVPlayer, SwipeBehavior):
	def __init__(self,vfile=None, loop=False, mute=False):
		BaseVPlayer.__init__(self,vfile=vfile, loop=loop, mute=mute)
		SwipeBehavior.__init__(self)
		self.bind(on_swipe_down=self.previous)
		self.bind(on_swipe_up=self.next)

class VPlayer(Swipe_VPlayer):
	def __init__(self,vfile=None, loop=False,mute=False, opbar=True):
		self.opbar = opbar
		self.menubar = None
		self._popup = None
		self.menu_status = False
		self.manualMode = False
		self.pb = None
		super().__init__(vfile=vfile,loop=loop,mute=mute)
		self._video.bind(on_touch_down=self.show_hide_menu)
	
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

	def positionChanged(self,o,v):
		self.update_slider(None)

	def update_slider(self,t):
		if self._video.state != 'play':
			return
		if self.pb is None:
			return
		v = self._video.position
		if v is None:
			return
		self.curposition.text = self.totime(v)
		if not self.manualMode:
			self.slider.value = v
			self.slider.max = self._video.duration
		self.maxposition.text = self.totime(self._video.duration)

	def __del__(self):
		self.stop()

	def beforeDestroy(self):
		print('beforeDestroy() called')
		self.stop()
		return True

	def show_hide_menu(self,obj,touch):
		if not self.collide_point(*touch.pos):
			print('not inside the player',touch.pos,self.pos,self.size)
			return 

		if touch.is_double_tap:
			self.fullscreen = False if self.fullscreen else True
			print('doube_tap')
			return 

		if not self.opbar:
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
		self.btn_pause = PressableImage(source=blockImage('pause.png'),
					size_hint=(None,None),
					size=CSize(3,3)
		)
		if self._video.state == 'pause':
			self.btn_pause.source = blockImage('play.png')
		self.btn_pause.bind(on_press=self.pause)
		self.menubar.add_widget(self.btn_pause)
		"""
		self.btn_mute = PressableImage(source=blockImage('mute.png'),
					size_hint=(None,None),
					size=CSize(3,3)
		)
		self.btn_mute.bind(on_press=self.mute)
		self.menubar.add_widget(self.btn_mute)
		"""
		btn_cut = PressableImage(source=blockImage('next.png'),
				size_hint=(None,None),
				size=CSize(3,3)
		)
		btn_cut.bind(on_press=self.endplay)
		self.menubar.add_widget(btn_cut)
		btn_replay = PressableImage(source=blockImage('replay.png'),
				size_hint=(None,None),
				size=CSize(3,3)
		)
		btn_replay.bind(on_press=self.replay)
		self.menubar.add_widget(btn_replay)

		self.btn_audioswitch = PressableImage( \
					source=blockImage('musictrack.png'),
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
				btn.source = blockImage('volume.png')
			else:
				btn.source = blockImage('mute.png')

	def pause(self,t=None):
		BaseVPlayer.pause(self,t)
		if self.menubar:
			if self._video.state == 'pause':
				self.btn_pause.source  = blockImage('play.png')
			else:
				self.btn_pause.source = blockImage('pause.png')

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
