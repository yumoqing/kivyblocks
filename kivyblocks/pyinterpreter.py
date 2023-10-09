from traceback import print_exc
from io import StringIO
from contextlib import redirect_stdout

from kivy.app import App
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from appPublic.Singleton import SingletonDecorator, GlobalEnv

from .baseWidget import PressableText
from .tab import TabsPanel
from .utils import *
from kivy.utils import platform
import plyer
if platform == 'android':
	import android
	import jnius
elif platform == 'ios':
	from pyobjus import autoclass, protocol, objc_str
	from pyobjus.dylib_manager import load_framework, INCLUDE

class PyInterpreter(TextInput):
	def __init__(self, **kw):
		kw['multiline'] = True
		super().__init__(**kw)
		self.env = {}
		for n,f in Factory.classes.items():
			if f['cls']:
				self.env[n] = f['cls']
		self.text = '>>>'
		self.focus = True
		self.scroll_line = -1
		# self.bind(on_key_up=self.check_enter_key)

	def find_line_start_idx(self):
		lines = self.text.split('\n')
		lines[-1] = '>>>'
		txt = '\n'.join(lines)
		idx = len(txt)
		return idx

	def keyboard_on_key_down(self, o, keycode, text, modifiers):
		_, key = keycode
		print('key=', key, 'pos=', self.cursor_pos, self.cursor_index())
		script = None
		if key == 'enter':
			script = self.get_script()
		if key == 'home':
			stop_idx = self.find_line_start_idx()
			self.cursor = self.get_cursor_from_index(stop_idx)
			return 
		if key == 'left':
			stop_idx = self.find_line_start_idx()
			idx = self.cursor_index(cursor=self.cursor)
			if idx <= stop_idx:
				return 
		if key == 'up' or key == 'down':
			self.scroll_script(key)
			return
		if key == 'backspace' and self.text[-3:] == '>>>':
			return 
		ret = super().keyboard_on_key_down(o, keycode, text, modifiers)
		if script:
			self.exec_script(script)
		elif key == 'enter':
			self.text += '>>>'
		return ret

	def scroll_script(self, key):
		lines = self.text.split('\n')
		slines = [l for l in lines if l.startswith('>>>') and l!='>>>']
		maxl = len(slines) - 1
		if self.scroll_line < 0:
			self.scroll_line = maxl
		if self.scroll_line == maxl and key == 'down':
			return
		if self.scroll_line == 0 and key == 'up':
			return
		if key == 'down':
			self.scroll_line += 1
		else:
			self.scroll_line -= 1
		lines[-1] = slines[self.scroll_line]
		self.text = '\n'.join(lines)

	def get_script(self):	
		ts = self.text.split('\n')
		s = ts[-1][3:]
		print('script=',s)
		return s

	def exec_script(self, script):
		env = globals().copy()
		f = StringIO()
		with redirect_stdout(f):
			try:
				exec(script, env, self.env)
			except Exception as e:
				print('Exception:', e)
				print_exc()
		f.seek(0)
		s = f.getvalue()
		self.text = self.text + s + '\n>>>'
		print('result=', s)

