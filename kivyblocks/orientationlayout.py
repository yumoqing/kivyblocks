from kivy.factory import Factory
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivyblocks.swipebehavior import SwipeBehavior
from kivyblocks.ready import WidgetReady

class OrientationLayout(WidgetReady, SwipeBehavior, FloatLayout):
	"""
	TwinStyleLayout layout two widget verical when parital orientation
	and second widget hide when it is in landscape
	"""
	def __init__(self,	main_widget=None, second_widget=None, **kw):
		self.main_widget = main_widget
		self.second_widget = second_widget
		self.widget_main = main_widget
		self.widget_second = second_widget
		self.second_flg = False
		FloatLayout.__init__(self, **kw)
		SwipeBehavior.__init__(self)
		WidgetReady.__init__(self)
		Clock.schedule_once(self.build_children,0)
		self.bind(on_swipe_left=self.toggle_second)
		self.bind(on_swipe_right=self.toggle_second)
	
	def build_children(self, *args):
		if isinstance(self.main_widget, dict):
			blocks = Factory.Blocks()
			blocks.bind(on_built=self.main_widget_built)
			blocks.bind(on_failed=self.widget_build_failed)
			blocks.widgetBuild(self.main_widget, ancestor=self)
		if isinstance(self.second_widget, dict):
			blocks = Factory.Blocks()
			blocks.bind(on_built=self.second_widget_built)
			blocks.bind(on_failed=self.widget_build_failed)
			blocks.widgetBuild(self.second_widget, ancestor=self)

	def isLandscape(self):
		return self.width > self.height

	def toggle_second(self,*args):
		print('toggle_second() called ..')
		if self.isLandscape():
			if self.second_flg:
				print('remove second widget ..')
				self.remove_widget(self.widget_second)
				self.second_flg = False
			else:
				print('add second widget ..')
				self.add_widget(self.widget_second)
				self.second_flg = True
				self.on_size(self.size)


	def on_ready(self,*args):
		Clock.schedule_once(self.two_widget_layout,0)

	def on_size(self,*args):
		Clock.schedule_once(self.two_widget_layout,0)

	def on_pos(self,*args):
		Clock.schedule_once(self.two_widget_layout,0)

	def two_widget_layout(self, *args):
		if not isinstance(self.widget_main, Widget) or not isinstance(self.widget_second, Widget):
			# Clock.schedule_once(self.two_widget_layout,0)
			return

		if self.isLandscape():
			self.horizontal_layout()
		else:
			self.vertical_layout()

	def horizontal_layout(self):
		self.widget_main.size_hint_x = 1
		self.widget_main.size_hint_y = 1
		self.widget_main.size = self.size
		self.widget_main.pos = self.pos
		self.widget_second.height = self.height
		self.widget_second.size_hint_x = None
		self.widget_second.size_hint_y = 1
		self.widget_second.width = self.width * self.height / self.width
		self.widget_second.pos = (0,0)
		self.widget_second.opacity = 0.6
		if not self.widget_main in self.children:
			self.add_widget(self.widget_main)
		if self.widget_second in self.children:
			self.remove_widget(self.widget_second)
		print('main_widget:width=%.02f,height=%.02f,pos=(%.02f,%.02f)' % (self.widget_main.width,self.widget_main.height,*self.widget_main.pos))
		print('second_widget:width=%.02f,height=%.02f,pos=(%.02f,%.02f)' % (self.widget_second.width,self.widget_second.height,*self.widget_second.pos))
		if self.second_flg:
			self.add_widget(self.widget_second)


	def vertical_layout(self):
		self.widget_main.size_hint_x = 1
		self.widget_main.size_hint_y = None
		self.widget_main.width = self.width
		self.widget_main.height = self.width / 16 * 10
		self.widget_main.pos = (0, self.height - self.widget_main.height)
		self.widget_second.width = self.width
		self.widget_second.size_hint_x = 1
		self.widget_second.size_hint_y = None
		self.widget_second.height = self.height - self.widget_main.height
		self.widget_second.pos = (0,0)
		self.widget_second.opacity = 1
		if not self.widget_main in self.children:
			self.add_widget(self.widget_main)
		if not self.widget_second in self.children:
			self.add_widget(self.widget_second)
		print('main_widget:width=%.02f,height=%.02f,pos=(%.02f,%.02f)' % (self.widget_main.width,self.widget_main.height,*self.widget_main.pos))
		print('second_widget:width=%.02f,height=%.02f,pos=(%.02f,%.02f)' % (self.widget_second.width,self.widget_second.height,*self.widget_second.pos))

	def main_widget_built(self,o,w):
		print('main_widget_built() called ...')
		self.widget_main = w
		self.add_widget(self.widget_main)
		if isinstance(self.widget_main, Widget) and isinstance(self.widget_second, Widget):
			print('ready() called ..')
			self.reready()


	def second_widget_built(self,o,w):
		print('second_widget_built() called ...')
		self.widget_second = w
		if isinstance(self.widget_main, Widget) and isinstance(self.widget_second, Widget):
			print('ready() called ..')
			self.reready()
	
	def widget_build_failed(self, o, e):
		pass
