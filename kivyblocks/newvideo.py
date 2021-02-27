import time
from kivy.uix.video import Video
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.properties import BooleanProperty

from ffpyplayer.tools import set_log_callback

from kivyblocks.bgcolorbehavior import BGColorBehavior
logger_func = {'quiet': Logger.critical, 'panic': Logger.critical,
               'fatal': Logger.critical, 'error': Logger.error,
               'warning': Logger.warning, 'info': Logger.info,
               'verbose': Logger.debug, 'debug': Logger.debug}


class NewVideo(BGColorBehavior, Video):
	def __init__(self,color_level=-1,radius=[],**kw):
		Video.__init__(self, **kw)
		BGColorBehavior.__init__(self,
			color_level=color_level,
			radius=radius)
		Window.allow_screensaver = False
		set_log_callback(self.ffplayerLog)
		self.register_event_type('on_open_failed')
		self.register_event_type('on_load_success')
		self.bind(source=self.record_start_time)
		self.load_status = None

	def resize(self, size):
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
		"""
		if 'Connection to tcp' in msg and 'failed' in msg:
			self.dispatch('on_open_failed', self.source)
		if 'Invalid data found when processing input' in msg:
			self.dispatch('on_open_failed', self.source)
		if 'End of file' in msg:
			self.dispatch('on_open_failed', self.source)
		if 'I/O error' in msg:
			self.dispatch('on_open_failed', self.source)
		if 'Server returned 404 Not Found' in msg:
			self.dispatch('on_open_failed', self.source)
		"""
		if 'Server returned 4' in msg:
			self.dispatch('on_open_failed', self.source)
		if 'Server returned 5' in msg:
			self.dispatch('on_open_failed', self.source)
			
		msg = msg.strip()
		if msg:
			logger_func[level]('yffpyplayer: {}'.format(msg))

	def get_video_size(self):
		if hasattr(self._video,'_ffplayer'):
			return self._video._ffplayer.get_frame()[0][0].get_size()
		else:
			Logger.error('NewVideo: _video has not _ffplayer, do nothong')
		
	def audioswitch(self,btn=None):
		if hasattr(self._video,'_ffplayer'):
			x = self._video._ffplayer.request_channel('audio')
		else:
			Logger.error('NewVideo: _video has not _ffplayer, do nothong')

	def on_state(self,*args):
		super().on_state(*args)
		if self.state == 'play':
			if self.load_status == 'start':
				self.load_status = 'success'
				t = time.time()
				self.dispatch('on_load_success',
								{
									'source':self.source,
									'time':int((t - self.start_time)*100)
								})

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
