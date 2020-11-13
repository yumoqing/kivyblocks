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
		self.register_event_type('on_key_down')
		self._ready = False

	def on_ready(self):
		pass
	def on_key_down(self,keyinfo):
		"""
		keyinfo is a dict with:
			keyname
			modifiers
		keys
		"""
		print(kinfo)

	def ready(self):
		if self._ready:
			return
		self.dispatch('on_ready')
		self._ready = True

	def reready(self):
		self._ready = False
		self.ready()

	def use_keyboard(self, keyinfos=[]):
		"""
		keyinfos is a list of aceepted keys keyinfo 
		if the on_key_down's key is one of the keyinfos, 
		fire a event, and return True, 
		else just return False
		"""
		self.my_kb = Window.request_keyboard(self.unuse_keyboard, self, "text")
		self.my_kb.bind(on_key_down=self._on_keyboard_down)
		if self.my_kb.widget:
			pass #self.my_kb.set_mode_free()
		self.keyinfos = keyinfos

	def unuse_keyboard(self):
		print('My keyboard have been closed!')
		self.my_kb.unbind(on_key_down=self._on_keyboard_down)
		self.my_kb = None

	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
		print('The key', keycode, 'have been pressed')
		print(' - text is %r' % text)
		print(' - modifiers are %r' % modifiers)

		def listqual(l1,l2):
			a = [i for i in l1 if i not in l2]
			b = [i for i in l2 if i not in l1]
			if len(a) == 0 and len(b) == 0:
				return True
			return False
		# Keycode is composed of an integer + a string
		# If we hit escape, release the keyboard
		if keycode[1] == 'escape':
			keyboard.release()

		for ki in self.keyinfos:
			if ki['keyname'] == keycode[1] and listequal(ki['modifiers'],modifiers):
				keyinfo = {
					"keyname":keycode[1],
					"modifiers":modifiers
				}
				self.dispatch('on_key_down',keyinfo)
				return True

		# Return True to accept the key. Otherwise, it will be used by
		# the system.
		return False

	def on_fullscreen(self, instance, value):
		window = self.get_parent_window()
		if not window:
			Logger.warning('VideoPlayer: Cannot switch to fullscreen, '
						   'window not found.')
			return
		if not self.parent:
			Logger.warning('VideoPlayer: Cannot switch to fullscreen, '
						   'no parent.')
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
			#if platform in desktopOSs:
			#	Window.restore()
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
