from kivy.event import EventDispatcher
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import BooleanProperty

desktopOSs=[
	"win",
	"linux",
	"macosx"
]

class WidgetReady(EventDispatcher):
	fullscreen = BooleanProperty(False)
	_fullscreen_state = False

	def __init__(self):
		self.register_event_type('on_ready')
		self._ready = False

	def on_ready(self):
		pass

	def ready(self):
		if self._ready:
			return
		self.dispatch('on_ready')
		self._ready = True

	def reready(self):
		self._ready = False
		self.ready()

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

			# if platform in desktopOSs:
			# 	Window.maximize()
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
			Window.fullscreen = False
			if platform in desktopOSs:
				Window.restore()
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
