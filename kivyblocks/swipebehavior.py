import time
from kivy.logger import Logger
from kivy.event import EventDispatcher

class SwipeBehavior(EventDispatcher):
	def __init__(self, **kwargs):
		self.register_event_type('on_context_menu')
		self.register_event_type('on_swipe_left')
		self.register_event_type('on_swipe_right')
		self.register_event_type('on_swipe_up')
		self.register_event_type('on_swipe_down')
		self.sb_start_point = None
		self.sb_end_point = None
		self.sb_start_time = None
		self.sb_end_time = None
		self.threshold=20
		self.threshold_time = 1.5

	def on_context_menu(self):
		Logger.info('SwipeBehavior:on_context_menu fired')

	def on_swipe_left(self):
		Logger.info('SwipeBehavior:on_swipe_left fired')
		pass

	def on_swipe_right(self):
		Logger.info('SwipeBehavior:on_swipe_right fired')
		pass

	def on_swipe_up(self):
		Logger.info('SwipeBehavior:on_swipe_up fired')
		pass

	def on_swipe_down(self):
		Logger.info('SwipeBehavior:on_swipe_down fired')
		pass

	def on_touch_down(self,touch):
		if self.collide_point(*touch.pos):
			self.sb_start_point = pos
			self.sb_start_time = time.time()
		return super().on_touch_down(touch)

	def on_touch_move(self,touch):
		if self.collide_point(*touch.pos):
			if self.sb_start_point is None:
				self.sb_start_point = touch.pos
			else:
				self.sb_end_point = touch.pos
		return super().on_touch_move()

	def on_touch_up(self,touch):
		if self.collide_point(*touch.pos):
			self.sb_end_point = touch.pos
			self.sb_end_time = time.time()
			self.check_context_menu()
		self.check_swipe()
		self.sb_start_point = None
		self.sb_end_point = None
		self.sb_start_time = None
		self.sb_end_time = None
		super().on_touch_up()

	def check_context_menu(self):
		if not self.sb_start_time:
			return
		if not self.sb_end_time:
			return
		if self.sb_end_time - self.sb_start_time > self.threshold_time:
			self.dispatch('on_context_menu')

	def check_swipe(self):
		if abs(self.sb_end_point.x - self.sb_start_point.x) > \
					abs(self.sb_end_point.y - self.sb_start_point.y):
			if self.sb_end_point.x - self.sb_start_point.x > self.threshold:
				self.dispatch('on_swipe_right')
			elif self.sb_start_point.x - self.sb_end_point.x > self.threshold:
				self.dispatch('on_swipe_left')
		else:
			if self.sb_end_point.y - self.sb_start_point.y > self.threshold:
				self.dispatch('on_swipe_up')
			elif self.sb_start_point.y - self.sb_end_point.x > self.threshold:
				self.dispatch('on_swipe_down')
