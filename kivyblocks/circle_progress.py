from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty, ColorProperty
from kivy.app import App
from kivyblocks.baseWidget import VBox
class CircleProgress(VBox):
	total_cnt = NumericProperty(100)
	cur_cnt = NumericProperty(0)
	circle_color = ColorProperty([0.7,0.7,0.7,1])
	present_color = ColorProperty([1,0,0,1])
	line_width = NumericProperty(2)
	def __init__(self, **kw):
		self.present_w = Label(text='0%', color=self.present_color)
		super().__init__(**kw)
		self.draw_circle()
		self.add_widget(self.present_w)

	def draw_circle(self):
		r = min(*self.size) / 2 - self.line_width
		rate = self.cur_cnt / self.total_cnt
		angle_end = rate * 360
		print(f'angle={angle_end}, {self.total_cnt} - {self.cur_cnt}, {r}, {self.size}')
		# self.canvas.before.clear()
		# with self.canvas.before:
		self.canvas.after.clear()
		with self.canvas.after:
			Color(*self.circle_color)
			Line(circle=(self.center_x,self.center_y, r), 
						width=4)
			Color(*self.present_color)
			Line(circle=(self.center_x,self.center_y, r, 0, angle_end), 
						width=4)
		self.present_w.text = '%d%%' % int(rate * 100)

	def progress(self, cur_cnt):
		if cur_cnt >= self.total_cnt:
			self.cur_cnt = self.total_cnt
		elif cur_cnt < 0:
			self.cur_cnt = 0
		else:
			self.cur_cnt = cur_cnt

	def on_cur_cnt(self, o, v):
		self.draw_circle()

if __name__ == '__main__':
	class TestApp(App):
		def build(self):
			x = CircleProgress(total_cnt=1000)
			self.task = Clock.schedule_interval(self.inc_v, 0.5)
			return x
		
		def inc_v(self, t=None):
			cnt = self.root.cur_cnt + 5
			self.root.progress(cnt)

	TestApp().run()

