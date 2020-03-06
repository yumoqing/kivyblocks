from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivyblocks.colorcalc import *
from kivyblocks.charts.chart import Chart,ChartPart

class BarPart(ChartPart):
	def __init__(self,widget,pos,size,color,data_offset):
		self.widget = widget
		self.pos = pos
		self.size = size
		self.color = color
		self.data_offset = data_offset

	def collide_point(self,x,y):
		minx = self.widget.pos[0] + self.pos[0]
		maxx = minx + self.size[0]
		miny = self.widget.pos[1] + self.pos[1]
		maxy = miny + self.size[1]
		if minx <= x and x <= maxx and \
				miny <= y and y <= maxy:
			return True
		return False

	def draw(self):
		with self.widget.canvas:
			Color(*self.color)
			Rectangle(pos=(self.widget.pos[0] + self.pos[0],
							self.widget.pos[1] + self.pos[1]),
							size = self.size)

	def mark(self):
		rcolor = reverseColor(self.color)
		rcolor.append(0.8)
		with self.widget.canvas.after:
			Color(*reverseColor(self.color))
			Rectangle(pos=(self.widget.pos[0] + self.pos[0],
							self.widget.pos[1] + self.pos[1]),
							size = self.size)

class Bar(Chart):
	"""
	a BAR class
	"""
	def __init__(self,**options):
		"""
		options={
			width,
			height,
			title,
			keyField,
			valueField,
			color1:
			color2：
			data=[
				{
					name,
					value,
				},{
				}
			]
		}
		"""
		self.data = None
		super().__init__(**options)

	def data2part(self):
		data = self.data
		kvs = [ [i[self.options['keyField']],i[self.options['valueField']]] for i in data ]
		m = max([i[1] for i in kvs ])
		cnt = len(kvs)
		points = divide([0,0],[self.width,0],cnt)
		color1='8833ee'
		color2='ed8234'
		colors = divideColor(color1,color2,cnt-1)
		for i in range(cnt):
			h = self.height * kvs[i][1] / m
			c = colors[i]
			part = BarPart(self,
						points[i],
						(points[i+1][0] - points[i][0],h),
						colors[i],
						i
					)
			self.chartparts.append(part)
		
