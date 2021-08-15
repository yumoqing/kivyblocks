from kivy.factory import Factory
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivyblocks.swipebehavior import SwipeBehavior
from kivyblocks.ready import WidgetReady

class OrientationLayout(FloatLayout, WidgetReady, SwipeBehavior):
	"""
	TwinStyleLayout layout two widget verical when parital orientation
	and second widget hide when it is in landscape
	"""
	def __init__(self,	main_widget=None, second_widget=None, **kw):
		self.main_widget = main_widget
		self.second_widget = second_widget
		self.widget_main = None
		self.widget_second = None
		self.second_flg = False
		super(OrientationLayout, self).__init__(**kw)
		self.build_children()
		self.bind(on_swipe_left=self.toggle_second)
		self.bind(on_swipe_right=self.toggle_second)
		self.bind(size=self.on_size_changed)
		self.bind(pos=self.on_size_changed)
		self.second_showed = None
		self.reready()
		self.register_event_type('on_interactive')
	
	def build_children(self, *args):
		blocks = Factory.Blocks()
		self.widget_main = blocks.widgetBuild(self.main_widget)
		blocks = Factory.Blocks()
		self.widget_second = blocks.widgetBuild(self.second_widget)

	def isLandscape(self):
		return self.width > self.height

	def toggle_second(self,*args):
		if self.isLandscape():
			if self.second_flg:
				self.remove_widget(self.widget_second)
				self.second_flg = False
				self.dispatch('on_interactive')
			else:
				self.add_widget(self.widget_second)
				self.second_flg = True
				self.on_size_changed(self.size)
				self.dispatch('on_interactive')

	def on_size_changed(self,*args):
		Clock.schedule_once(self.two_widget_layout,0)

	def on_interactive(self, *args):
		print('on_orientation_changed fired')

	def two_widget_layout(self, *args):
		if not isinstance(self.widget_main, Widget) or \
				not isinstance(self.widget_second, Widget):
			# Clock.schedule_once(self.two_widget_layout,0)
			return

		if self.isLandscape():
			self.horizontal_layout()
		else:
			self.vertical_layout()
		self.do_layout()

	def horizontal_layout(self):
		self.widget_main.size_hint = (None,None)
		self.widget_main.size = self.size
		self.widget_main.pos = self.pos
		self.widget_second.height = self.height
		self.widget_second.size_hint = (None,None)
		self.widget_second.width = self.width * self.height / self.width
		self.widget_second.pos = (0,0)
		self.widget_second.opacity = 0.6
		self.clear_widgets()
		self.add_widget(self.widget_main)
		if self.second_flg:
			self.add_widget(self.widget_second)

	def vertical_layout(self):
		self.widget_main.size_hint = (None,None)
		self.widget_main.size = (self.width, \
										self.width / 16 * 10)
		self.widget_main.pos = (0, self.height - self.widget_main.height)
		self.widget_second.size_hint = (None, None)
		self.widget_second.size = (self.width, \
							self.height - self.widget_main.height)
		self.widget_second.pos = (0,0)
		self.widget_second.opacity = 0.6
		self.clear_widgets()
		self.add_widget(self.widget_main)
		self.add_widget(self.widget_second)

	def widget_build_failed(self, o, e):
		pass

