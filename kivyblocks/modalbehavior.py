
from kivy.core.window import Window
from kivy.properties import DictProperty, BooleanProperty, \
							StringProperty, OptionProperty, \
							NumericProperty

class ModalBehavior(object):
	auto_open = BooleanProperty(True)
	auto_dismiss = BooleanProperty(True)
	target = StringProperty(None)
	show_time = NumericProperty(0)
	anchor = OptionProperty('cc',options=['tl', 'tc', 'tr',
											'cl', 'cc', 'cr',
											'bl', 'bc', 'br'])
	def __init__(self, **kw):
		for k,v in kw.items():
			setattr(self, k,v)
		self.time_task = None
		self._target = None
		self.set_size_anchor()
		self._target.bind(size=self.set_size_anchor)
		self.register_event_type('on_open')
		self.register_event_type('on_pre_open')
		self.register_event_type('on_pre_dismiss')
		self.register_event_type('on_dismiss')
		self.bind(on_touch_down=self.on_touchdown)
		if self.auto_open:
			self.open()

	def on_touchdown(self, o, touch):
		if not self.collide_point(touch.x, touch.y):
			if self.auto_dismiss:
				self.dispatch('on_pre_dismiss')
				self.dismiss()
				return True
				
	def on_target(self, *args):
		self._target = None
		self.set_target(self)
		
	def set_target(self):
		if self._target is None:
			if self.target is None:
				w = Window
			else:
				w = Factory.Blocks.getWidgetById(self.target, from_target=self)
				if w is None:
					w = Window
			self._target = w

	def set_size_anchor(self, *args):
		self.set_target()
		if self.size_hint_x:
			self.width = self.size_hint_x * self._target.width
		if self.size_hint_y:
			self.height = self.size_hint_y * self._target.height
		self.set_modal_anchor()

	def set_modal_anchor(self):
		self.set_target()
		xn = self.anchor[1]
		yn = self.anchor[0]
		x, y = 0, 0
		if xn == 'c':
			x = (self._target.width - self.width) / 2
		elif xn == 'r':
			x = self._target.width - self.width
		if x < 0:
			x = 0
		if yn == 'c':
			y = (self._target.height - self.height) / 2
		elif yn == 't':
			y = self._target.height - self.height
		if y < 0:
			y = 0
		if self._target == Window:
			self.pos = x, y
		else:
			self.pos = self._target.pos[0] + x, self._target.pos[1] + y
		Mx, My = Window.width, Window.height
		self.pos_hint = {'x':self.pos[0]/Mx, 'y':self.pos[1]/My}
		print("modal",self._target.size, self.anchor, self.pos, self.size, self.size_hint)

	def open(self):
		if self.time_task is not None:
			self.time_task.cancel()
			self.time_task = None
		if self.show_time > 0:
			self.time_task = \
				Clock.schedule_once(self.dismiss, self.show_time)
		if self.parent:
			self.parent.remove_widget(self)
		self.dispatch('on_pre_open')
		Window.add_widget(self)
		self.dispatch('on_open')
		if self._target != Window:
			self._target.disabled = True

	def dismiss(self, *args):
		print('dismiss() called')
		if self.time_task:
			self.time_task.cancel()
			self.time_task = None
		self.dispatch('on_pre_dismiss')
		self.dispatch('on_dismiss')
		Window.remove_widget(self)
		if self._target != Window:
			self._target.enabled = False
			
	def on_open(self, *args):
		pass

	def on_dismiss(self, *args):
		pass
			
	def on_pre_open(self, *args):
		pass

	def on_pre_dismiss(self, *args):
		pass

