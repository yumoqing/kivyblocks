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
		if hasattr(self._video, '_ffplayer'):
			self.ffplayer = self._video._ffplayer

	def on_state(self,*args):
		print('new state = ',self.state)
		if self.state == 'play':
			Window.allow_screensaver = False
		else:
			Window.allow_screensaver = True
			
	def ffplayerLog(self, msg, level):
		msg = msg.strip()
		if msg:
			logger_func[level]('yffpyplayer: {}'.format(msg))

	def audioswitch(self,btn=None):
		x = self._video._ffplayer.request_channel('audio')

