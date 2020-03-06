from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from kivyblocks.colorcalc import toArrayColor

class ChartPart(object):
	def __init__(self,pos,width,height):
		self.pos = pos
		self.width = width
		self.height = height

	def collide_point(self,x,y):
		raise NotImplementedError

	def draw(self):
		raise NotImplementedError

	def mark(self):
		raise NotImplementedError
		
class Chart(Widget):
	def __init__(self,**options):
		super().__init__()
		self.options = options
		self.bg_color = toArrayColor(self.options.get('bg_color',[0.3,0.3,0.3,1]))
		self.markpart = None
		self.bind(size=self.onSize,pos=self.onSize)
		self.register_event_type("on_press")

	def unmark(self):
		self.canvas.after.clear()

	def getData(self):
		url = self.options.get('url')
		if url:
			hc = App.get_running_app().hc
			params = self.options.get('params',{})
			d = hc.get(url,parms=param)
			self.data = d.get('data',[])
		else:
			self.data = self.options.get('data',[])
		self.chartparts = []

	def on_touch_down(self,touch):
		if touch.is_mouse_scrolling:
			return False
		if not self.collide_point(touch.x,touch.y):
			return False
		self.markpart = None
		self.unmark()
		for part in self.chartparts:
			if part.collide_point(touch.x,touch.y):
				self.markPart(part)
				self.dispatch('on_press',self,self.data[part.data_offset])
		return super(Chart, self).on_touch_down(touch)

	def on_press(self,o,data):
		print('data=',data)

	def draw(self):
		with self.canvas.before:
			Color(*self.bg_color)
			Rectangle(pos=self.pos,size=self.size)

		self.canvas.clear()
		for part in self.chartparts:
			part.draw()

	def markPart(self,part):
		self.markpart = part
		part.mark()

	def onSize(self,o,v):
		self.build()

	def build(self):
		self.getData()
		self.data2part()
		self.draw()
