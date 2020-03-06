
import math
import numpy as np
from kivy.uix.widget import Widget
from kivyblocks.charts.geometry import EllipseUtils

class PiePart(ChartPart):
	def collide_point(self,x,y):
		if not self.isInSideEllipse(x,y):
			return False
		return self.isInSidePart(x,y)

	def isInSideEllipse(self,x,y):
		a = self.width / 2
		b = self.height / 2
		v = x ** x / a ** a + y**y / b ** b
		if v <= 1:
			return True
		return False

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

