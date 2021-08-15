import time
from kivy.logger import Logger

class SwipeBehavior(object):
	def __init__(self, **kwargs):
		object.__init__(self)
		self.swipeenable = True
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
		self.threshold_time = 0.6
		self.bind(on_touch_down=self.on_touchdown)
		self.bind(on_touch_move=self.on_touchmove)
		self.bind(on_touch_up=self.on_touchup)

	def disable_swipe(self):
		self.swipeenable = False

	def enable_swipe(self):
		self.swipeenable = True

	def on_context_menu(self):
		pass
		# Logger.info('SwipeBehavior:on_context_menu fired')

	def on_swipe_left(self):
		pass
		# Logger.info('SwipeBehavior:on_swipe_left fired')

	def on_swipe_right(self):
		pass
		# Logger.info('SwipeBehavior:on_swipe_right fired')

	def on_swipe_up(self):
		pass
		# Logger.info('SwipeBehavior:on_swipe_up fired')

	def on_swipe_down(self):
		pass
		# Logger.info('SwipeBehavior:on_swipe_down fired')

	def on_touchdown(self,o, touch):
		if touch.is_mouse_scrolling:
			# Logger.info('SwipeBehavior:is_mouse_scrolling')
			return False
		if not self.collide_point(touch.x, touch.y):
			return False

		# Logger.info('SwipeBehavior:touch_down fired')
		if self.swipeenable:
			# Logger.info('SwipeBehavior:touch_down fired')
			self.sb_start_point = touch.pos
			self.sb_start_time = time.time()

	def on_touchmove(self,o,touch):
		if self.collide_point(*touch.pos) and self.swipeenable:
			# Logger.info('SwipeBehavior:touch_move fired')
			if self.sb_start_point is None:
				self.sb_start_point = touch.pos
			else:
				self.sb_end_point = touch.pos

	def on_touchup(self,o,touch):
		ret = False
		if self.collide_point(*touch.pos) and self.swipeenable:
			# Logger.info('SwipeBehavior:touch_up fired')
			self.sb_end_point = touch.pos
			self.sb_end_time = time.time()
			self.check_context_menu()
			ret = True
		self.check_swipe()
		self.sb_start_point = None
		self.sb_end_point = None
		self.sb_start_time = None
		self.sb_end_time = None

	def check_context_menu(self):
		if not self.sb_start_time:
			return
		if not self.sb_end_time:
			return
		period_time = self.sb_end_time - self.sb_start_time
		# Logger.info('SwipeBehavior:period_time=%f,threshold_time=%f',
		#				period_time, self.threshold_time)
		if period_time >= self.threshold_time:
			self.dispatch('on_context_menu')

	def check_swipe(self):
		if not self.sb_end_point:
			return

		if not self.sb_start_point:
			return

		if abs(self.sb_end_point[0] - self.sb_start_point[0]) > \
					abs(self.sb_end_point[1] - self.sb_start_point[1]):
			Logger.info('SwipeBehavior:check_swipe x>y')
			if self.sb_end_point[0] - self.sb_start_point[0] >= \
						self.threshold:
				self.dispatch('on_swipe_right')
			elif self.sb_start_point[0] - self.sb_end_point[0] >= \
						self.threshold:
				self.dispatch('on_swipe_left')
		else:
			# Logger.info('SwipeBehavior:check_swipe x<y')
			if self.sb_end_point[1] - self.sb_start_point[1] >= \
						self.threshold:
				self.dispatch('on_swipe_up')
			elif self.sb_start_point[1] - self.sb_end_point[1] >= \
						self.threshold:
				self.dispatch('on_swipe_down')
