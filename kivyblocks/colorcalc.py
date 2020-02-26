from kivy.utils import get_color_from_hex
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.boxlayout import BoxLayout
import math

def toArrayColor(color):
	if isinstance(color,str):
		sc = color
		return get_color_from_hex(sc)
	return color
	
def distance(color1,color2):
	color1 = toArrayColor(color1)
	color2 = toArrayColor(color2)
	x = math.pow(abs(color2[0] - color1[0]),2) + \
		math.pow(abs(color2[1] - color1[1]),2) + \
		math.pow(abs(color2[2] - color1[2]),2)
	d = math.sqrt(x)

def reverseColor(color):
	center = [0.5,0.5,0.5]
	if color == [0.5,0.5,0.5]:
		return [1,1,1]
	d = distance(color,center)
	d1 = d + 0.5
	point= [0,0,0]
	for i in range(3):
		m = color[i] - center[i]
		m1 = m * d1 / d
		point[i] = color[i] - m1 if m < 0? color[i] + m1
	return point

#DIVIDE
def divideColor(color1,color2,divide_cnt):
	color1 = toArrayColor(color1)
	color2 = toArrayColor(color2)
	return divide(color1,color2,divide_cnt)

def divide(point1,point2,divide_cnt):
	ps = [point1]
	dim = len(point1)
	for i in range(1,divide_cnt):
		p = []
		cnt = divide_cnt
		for j in range(dim):
			m = (i*point2[j] + (cnt - i) * point1[j]) / cnt
			p.append(m)
		ps.append(p)
	ps.append(point2)
	return ps

class Bar(Widget):
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
			data=[
				{
					name,
					value,
				},{
				}
			]
		}
		"""
		self.options = options
		self.initflag = False
		super().__init__()
		self.bind(size=self.onSize,pos=self.onSize)

	def data2bar(self):
		data = self.options.get('data',[])
		kvs = [ [i[self.options['keyField']],i[self.options['valueField']]] for i in data ]
		m = max([i[1] for i in kvs ])
		cnt = len(kvs)
		points = divide([0,0],[self.width,0],cnt)
		color1='8833ee'
		color2='ed8234'
		colors = divideColor(color1,color2,cnt-1)
		self.canvas.clear()
		for i in range(cnt):
			h = self.height * kvs[i][1] / m
			with self.canvas:
				Color(*colors[i])
				Rectangle(pos=points[i],
					size=(points[i+1][0] - points[i][0],h))
		
	def onSize(self,o,v):
		self.build()

	def build(self):
		self.initflag = True
		self.data2bar()

class Pie(Widget):
	def __init__(self,**options):
		"""
		options={
			width,
			height,
			title,
			keyField,
			valueField,
			data=[
				{
					name,
					value,
				},{
				}
			]
		}
		"""
		self.options = options
		self.initflag = False
		super().__init__()
		self.bind(size=self.onSize,pos=self.onSize)

	def data2pie(self):
		data = self.options.get('data',[])
		kvs = [ [i[self.options['keyField']],i[self.options['valueField']]] for i in data ]
		total = sum([i[1] for i in kvs ])
		start_degree = 0
		cnt = len(kvs)
		color1='8833ee'
		color2='ed8234'
		colors = divideColor(color1,color2,cnt-1)
		self.canvas.clear()
		for i in range(cnt):
			degree = start_degree + 360 * kvs[i][1] / total
			with self.canvas:
				Color(*colors[i])
				Ellipse(pos=self.pos,
					size=self.size,
						angle_start=start_degree,
						angle_end= degree)
			start_degree = degree
		
	def onSize(self,o,v):
		self.data2pie()

class MyApp(App):
	def build(self):
		d = {
			"keyField":"name",
			"valueField":"value",
			"data":[
				{'name':'you','value':102.0},
				{'name':'me','value':42.0},
				{'name':'she','value':92.0},
				{'name':'she','value':52.0},
				{'name':'she','value':42.0},
				{'name':'she','value':82.0},
				{'name':'she','value':17.0},
				{'name':'he','value':77.0}
			]
		}

		return Pie(**d)

if __name__ == '__main__':
	MyApp().run()
