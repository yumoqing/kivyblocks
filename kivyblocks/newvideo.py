from kivy.uix.video import Video
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.utils import platform
from kivy.factory import Factory
from kivy.properties import BooleanProperty

from ffpyplayer.tools import set_log_callback
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


class NewVideo(Video):
	fullscreen = BooleanProperty(False)
	_fullscreen_state = False

	def __init__(self,**kw):
		super(NewVideo, self).__init__(**kw)
		Window.allow_screensaver = False
		set_log_callback(self.ffplayerLog)
		if hasattr(self._video, '_ffplayer'):
			self.ffplayer = self._video._ffplayer

		Window.bind(on_rotate=self.ctrl_fullscreen)

	def ctrl_fullscreen(self,*args):
		if Window.width > Window.height:
			self.fullscreen = True
		else:
			self.fullscreen = False

	def ffplayerLog(self, msg, level):
		msg = msg.strip()
		if msg:
			logger_func[level]('yffpyplayer: {}'.format(msg))

	def audioswitch(self,btn=None):
		x = self._video._ffplayer.request_channel('audio')

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
			self.pos_hint = {}
			self.size_hint = (1, 1)
		else:
			if platform in desktopOSs:
				Window.restore()
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

Factory.register('NewVideo',NewVideo)
