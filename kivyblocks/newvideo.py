import time
from kivy.uix.video import Video
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.properties import BooleanProperty, DictProperty
from kivy.clock import Clock

from ffpyplayer.tools import set_log_callback

from .hack_ffpyplayer import set_headers_pattern, hack_mediaplayer
logger_func = {'quiet': Logger.critical, 'panic': Logger.critical,
               'fatal': Logger.critical, 'error': Logger.error,
               'warning': Logger.warning, 'info': Logger.info,
               'verbose': Logger.debug, 'debug': Logger.debug}


class NewVideo(Video):
	center_screen = BooleanProperty(False)
	h_pattern = DictProperty(None)
	def __init__(self, **kw):
		hack_mediaplayer()
		Video.__init__(self, **kw)
		Window.allow_screensaver = False
		set_log_callback(self.ffplayerLog)
		self.register_event_type('on_open_failed')
		self.register_event_type('on_leave_focus')
		self.register_event_type('on_enter_focus')
		self.register_event_type('on_load_success')
		self.bind(source=self.record_start_time)
		self.bind(loaded=self.on_video_loaded)
		self.load_status = None
		Clock.schedule_interval(self.check_focus,0.2)
		if self.h_pattern:
			[ set_headers_pattern(k,v) for k,v in self.h_pattern.items() ]

	def set_patternheaders(self, pattern, headers_str):
		set_headers_pattern(pattern, headers_str)

	def on_enter_focus(self, v=None):
		pass

	def on_leave_focus(self, v=None):
		pass

	def check_focus(self,*args):
		if not self.parent:
			self.center_screen = False
			return
		if not self.get_root_window():
			self.center_screen = False

		w = self.parent
		pos = w.to_widget(*Window.center)
		if self.collide_point(*pos):
			self.center_screen = True
		else:
			self.center_screen = False

	def on_center_screen(self,o, v):
		if v:
			self.dispatch('on_enter_focus')
		else:
			self.dispatch('on_leave_focus')

	def resize(self, *args):
		v_size = self.get_video_size()
		if v_size:
			self.height = self.width * v_size[1] / v_size[0]

	def on_load_success(self, *args):
		pass

	def record_start_time(self, *args):
		self.start_time = time.time()
		self.load_status = 'start'

	def on_open_failed(self, source, x=None):
		Logger.error(f'NewVideo: source={self.source} open failed')
		self.load_status = 'failed'

	def ffplayerLog(self, msg, level):
		if 'Connection to tcp' in msg and 'failed' in msg:
			self.dispatch('on_open_failed', msg)
		if 'Invalid data found when processing input' in msg:
			self.dispatch('on_open_failed', msg)
		if 'Http error 403' in msg:
			self.dispatch('on_open_failed', msg)
		if 'End of file' in msg:
			self.dispatch('on_open_failed', msg)
		if 'I/O error' in msg:
			self.dispatch('on_open_failed', msg)
		if 'Server returned 4' in msg:
			self.dispatch('on_open_failed', msg)
		if 'Server returned 5' in msg:
			self.dispatch('on_open_failed', msg)
			
		msg = msg.strip()
		if msg:
			logger_func[level]('yffpyplayer: {}'.format(msg))

	def get_video_size(self):
		if hasattr(self._video,'_ffplayer'):
			try:
				return self._video._ffplayer.get_frame()[0][0].get_size()
			except:
				return None
		else:
			Logger.error('NewVideo: _video has not _ffplayer, do nothong')
		return None
		
	def audioswitch(self,btn=None):
		if hasattr(self._video,'_ffplayer'):
			x = self._video._ffplayer.request_channel('audio')
		else:
			Logger.error('NewVideo: _video has not _ffplayer, do nothong')

	def on_video_loaded(self, *args):
		if self.load_status == 'start':
			self.load_status = 'success'
			t = time.time()
			self.dispatch('on_load_success',
							{
								'source':self.source,
								'time':int((t - self.start_time)*100)
							})


	def on_state(self,*args):
		super().on_state(*args)
		if self.state == 'play':
			Window.allow_screensaver = False
		else:
			Window.allow_screensaver = True

	# fix bug for android
	# ValueError: None is not allowed for NewVideo.duration 
	def _on_video_frame(self, *largs):
		video = self._video
		if not video:
			return
		if video.duration is None:
			return
		if video.position is None:
			return
		super()._on_video_frame(*largs)

	#
	# try to fix up the error
	def unload(self,try_cnt=0):
		"""
		File "C:\Python37\lib\threading.py", line 1039, in join
		RuntimeError: cannot join thread before it is started
		"""
		try:
			super().unload()
			return
		except Exception as e:
			if try_cnt > 3:
				print('video.unload() tried 3 time,still error....',e)
				raise e
			time.sleep(0.1)
			return self.unload(try_cnt+1)
