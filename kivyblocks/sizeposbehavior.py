
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty
from kivy.graphics import Color, Line

class SizePosBehavior(object):
	resizable = BooleanProperty(False)
	movable = BooleanProperty(False)
	border_width = NumericProperty(8)
	def __init__(self, **kw):
		self.trigger_task = None
		self.act_type = None
		self.bind(on_touch_down, self.touchdown)
		self.bind(on_touch_move, self.touchmove)
		self.bind(on_touch_up, self.touchup)
		self.sp_enable = kw.get('sp_enable', False)
		
	@classmethod
	def properties(self):
		return [
			'resizable',
			'movable',
			'border_width'
		]

	def enable_resize_move(self):
		self.sp_enable = True

	def disable_resize_move(self):
		self.sp_enable = False

	def identify_type(self):
		x, y = self.start_touch_pos
		minx, maxx = self.pos[0] + self.border_width, self.width - self.border_width
		miny, maxy = self.pos[1] + self.border_width, self.height - self.border_width
		self.act_type = 'resize'
		if x >= minx and x < maxx:
			if y >= miny and y <= maxy:
				self.act_type = 'move'
				return
		if x - self.pos[0] < self.border_width:
			self.lines.append('left')
		if maxx - x < self.border_width:
			self.lines.append('top')
		if y - self.pos[1] < self.border_width:
			self.lines.append('right')
		if maxy - y < self.border_width:
			self.lines.append('bottom')

	def touchdown(self, o, touch):
		if not self.collide_point(*touch.pos):
			return
		if not self.sp_eanble:
			return
		touch.grab(self)
		self.start_touch_pos = touch.pos
		self.start_offset = touch.pos[0] - self.pos[0], touch.pos[1] - self.pos[1]
		self.act_type = None
		self.lines = []
		self.trigger_task = Clock.schedule_once(self.identify_type, 0.5)

	def touchmove(self, o, touch):
		if not self.parent.collide_point(*touch.pos):
			return
		if not self.sp_eanble:
			return
		if self.act_type is None:
			return
		if touch.grab_current != self:
			return
		if self.act_type == 'move':
			pos = touch.pos
			maxx = self.parent.width
			maxy = self.parent.height
			x = pos[0] - self.start_offset[0]
			y = pos[1] - self.start_offset[1]
			if x < 0:
				x = 0
			if x > maxx - self.width:
				x = maxx - self.width
			if y < 0:
				y = 0
			if y > maxy - self.height:
				y = maxy - self.height
			self.pos = x, y
			self.pos_hint = {'x':x/maxx, 'y':y/maxy}
			self.draw_box()
		if self.act_type == 'resize':
			pos = touch.pos
			xoffset = pos[0] - self.start_touch_pos[0]
			yoffset = pos[1] - self.start_touch_pos[1]
			for l in self.lines:
				if l == 'left':
					self.width -= xoffset
					self.x -= xoffset
				elif l == 'top':
					self.height -= yoffset
					self.y -= yoffset
				elif l == 'right':
					self.width += xoffset
				else:
					self.heigth += yoffset

	def touchup(self, o, touch):
		if self.trigger_task:
			self.trigger_task.cancel()
		self.trigger_task = None
		if touch.grab_current is self:
			touch.ungrab(self)
		if not self.sp_enable:
			return
		self.start_touch_pos = None
		self.start_offset = None

	def draw_border(self):
		if not self.sp_eanble:
			return
		self.canvas.after.clear()
		with self.canvas.after:
			Color(1,0,0,1)
			Line(rectangle=(*self.pos, *self.size), width=1)

	def undraw_border(self):
		self.canvas.after.clear()
