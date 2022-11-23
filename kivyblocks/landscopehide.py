
from kivy.graphics import Color, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivyblocks.bgcolorbehavior import BGColorBehavior
from kivyblocks.utils import widget_build
from kivyblocks.mixin import get_mixins, filter_mixin

class LandscopeHide(FloatLayout):
	def __init__(self, fix_desc=None, float_desc=None, **kw):
		self.fix_widget = None
		self.float_widget = None
		self.float_show_landscope = False
		FloatLayout.__init__(self, **kw)
		if fix_desc:
			if isinstance(fix_desc, Widget):
				self.fix_widget = fix_desc
			else:
				self.fix_widget = widget_build(fix_desc)
			self.add_widget(self.fix_widget)
		if float_desc:
			if isinstance(float_desc, Widget):
				self.float_widget = float_desc
			else:
				self.float_widget = widget_build(float_desc)
		self.bind(size=self.size_changed)

	def get_subwidgets(self):
		return (self.fix_widget, self.float_widget)

	def hide_float(self):
		self.float_show_landscope = False
		if not self.is_landscope():
			return
		if self.float_widget not in self.children:
			return 
		self.remove_widget(self.float_widget)

	def force_show_float(self):
		self.float_show_landscope = True
		if self.float_widget in self.children:
			return
		self.show_float()

	def is_landscope(self):
		return self.width > self.height
		
	def size_changed(self, *args):
		self.rate = min(*self.size) / max(*self.size)
		self.show_fix()
		self.show_float()
		self._trigger_layout()
		print(f'landscope={self.is_landscope()}, w={self.width}, h={self.height}, fix_pos={self.fix_widget.pos}, fix_size={self.fix_widget.size}')
		self.canvas.before.clear()
		with self.canvas.before:
			Color(1,0,0,1)
			Line(rectangle=(0,0, self.width, self.height), width=2)

	def show_fix(self):
		if self.is_landscope():
			print('show_fix() landscope')
			self.fix_widget.size_hint = (1, 1)
			self.fix_widget.pos_hint = {'x':0, 'y':0}
		else:
			print('show_fix() not landscope')
			hr = self.width * self.rate / self.height
			self.fix_widget.size_hint = (1, hr)
			self.fix_widget.pos_hint = {'x':0, 'y':(1-hr)}
		
	def show_float(self):
		if self.is_landscope():
			if self.float_show_landscope:
				print('show_float() landscope')
				self.float_widget.size_hint = (None, 1)
				self.float_widget.width = self.height * self.rate
				self.float_widget.pos = (0, 0)
				self.add_widget(self.float_widget)
			else:	
				if self.float_widget in self.children:
					self.remove_widget(self.float_widget)
		else:
			print('show_float() not landscope')
			self.float_widget.size_hint = (1, None)
			self.float_widget.height = self.height - self.fix_widget.height
			self.float_widget.pos = (0, 0)
			if not self.float_widget in self.children:
				self.add_widget(self.float_widget)

if __name__ == '__main__':
	from kivy.app import App
	from kivy.uix.button import Button

	class TestApp(App):
		def build(self):
			x = LandscopeHide(fix_desc=Button(text='Fix'),
								float_desc=Button(text='Float'))
			return x
	TestApp().run()
