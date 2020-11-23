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
	def __init__(self,**kw):
		Video.__init__(self, **kw)
		BGColorBehavior.__init__(self)
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
		 Traceback (most recent call last):
		   File "main.py", line 288, in <module>
			 myapp.run()
		   File "C:\Python37\lib\site-packages\kivy\app.py", line 855, in run
			 runTouchApp()
		   File "C:\Python37\lib\site-packages\kivy\base.py", line 504, in runTouchApp
			 EventLoop.window.mainloop()
		   File "C:\Python37\lib\site-packages\kivy\core\window\window_sdl2.py", line 747, in mainloop
			 self._mainloop()
		   File "C:\Python37\lib\site-packages\kivy\core\window\window_sdl2.py", line 479, in _mainloop
			 EventLoop.idle()
		   File "C:\Python37\lib\site-packages\kivy\base.py", line 348, in idle
			 Clock.tick_draw()
		   File "C:\Python37\lib\site-packages\kivy\clock.py", line 598, in tick_draw
			 self._process_events_before_frame()
		   File "kivy\_clock.pyx", line 427, in kivy._clock.CyClockBase._process_events_before_frame
		   File "kivy\_clock.pyx", line 467, in kivy._clock.CyClockBase._process_events_before_frame
		   File "kivy\_clock.pyx", line 465, in kivy._clock.CyClockBase._process_events_before_frame
		   File "kivy\_clock.pyx", line 167, in kivy._clock.ClockEvent.tick
		   File "C:\Python37\lib\site-packages\kivy\uix\video.py", line 174, in _do_video_load
			 self.unload()
		   File "C:\Python37\lib\site-packages\kivy\uix\video.py", line 240, in unload
			 self._video.stop()
		   File "C:\Python37\lib\site-packages\kivy\core\video\video_ffpyplayer.py", line 325, in stop
			 self.unload()
		   File "C:\Python37\lib\site-packages\kivy\core\video\video_ffpyplayer.py", line 366, in unload
			 self._thread.join()
		   File "C:\Python37\lib\threading.py", line 1039, in join
			 raise RuntimeError("cannot join thread before it is started")
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
			return unload(try_cnt+1)
