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

	def ffplayerLog(self, msg, level):
		msg = msg.strip()
		if msg:
			logger_func[level]('yffpyplayer: {}'.format(msg))

	def audioswitch(self,btn=None):
		if hasattr(self._video,'_ffplayer'):
			x = self._video._ffplayer.request_channel('audio')
		else:
			print('NewVideo _video has not _ffplayer, do nothong')

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
