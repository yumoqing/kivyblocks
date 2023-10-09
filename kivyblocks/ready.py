

from traceback import print_exc
from contextlib import contextmanager
from kivy.graphics import Fbo, Color, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from kivy.app import App
from kivy.properties import BooleanProperty
from plyer import filechooser

desktopOSs=[
	"win",
	"linux",
	"macosx"
]

class WidgetReady(object):
	fullscreen = BooleanProperty(False)
	ready = BooleanProperty(False)
	_fullscreen = False

	@contextmanager
	def fboContext(self):
		self._fbo = Fbo(size=self.size)
		with self._fbo:
			self._background_color = Color(0,0,0,1)
			self._background_rect = Rectangle(size=self.size)

		try:
			yield self._fbo
		except Exception as e:
			print_exc()
			print('Exeception=',e)
			
		with self.canvas:
			self._fbo_rect = Rectangle(size=self.size,
								texture=self._fbo.texture)

	def on_ready(self, *args):
		pass

	def set_ready(self, *args):
		self.ready = True

	def reready(self):
		self.ready = False
		Clock.schedule_once(self.set_ready, 0.1)

	def use_keyboard(self):
		self.my_kb = Window.request_keyboard(None, self)
		if not self.my_kb:
			print('my_kb is None........')
			return 
		self.my_kb.bind(on_key_down=self._on_keyboard_down)
		if self.my_kb.widget:
			self.my_kb.set_mode_free()

	def key_handle(self,keyinfo):
		pass

	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
		print('The key', keycode, 'have been pressed')
		print(' - text is %r' % text)
		print(' - modifiers are %r' % modifiers)
		keyinfo = {
			"keyname":keycode[1],
			"modifiers":modifiers
		}
		self.key_handle(keyinfo)
		return True

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

		app = App.get_running_app()
		if value:
			Window.fullscreen = True
			app.fs_widget = self
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

			if state['parent'] is not window:
				state['parent'].remove_widget(self)
			window.add_widget(self)

			self.pos = (0, 0)
			self.pos_hint = {}
			self.size_hint = (1, 1)
		else:
			app.fs_widget = None
			Window.fullscreen = False
			#if platform in desktopOSs:
			#	Window.restore()
			state = self._fullscreen_state
			window.remove_widget(self)
			for c in state['window_children']:
				if c in Window.children:
					Window.remove_widget(c)
			for child in state['window_children']:
				window.add_widget(child)
			self.pos_hint = state['pos_hint']
			self.size_hint = state['size_hint']
			self.pos = state['pos']
			self.size = state['size']
			if state['parent'] is not window:
				state['parent'].add_widget(self)

	def file_open_for_read(self, *args, **kw):
		method_name = kw.get('on_selection')
		if method_name is None:
			return
		f = getattr(self, method_name)
		if f is None:
			return 
		kw['on_selection'] = f
		filechooser.open_file(**kw)

	def file_open_for_write(self, *args, **kw):
		method_name = kw.get('on_selection')
		if method_name is None:
			return
		f = getattr(self, method_name)
		if f is None:
			return 
		kw['on_selection'] = f
		filechooser.save_file(**kw)
		
