from kivy.utils import get_color_from_hex
#from kivy.app import App
#from kivy.uix.widget import Widget
#from kivy.graphics import Color, Rectangle, Ellipse
#from kivy.uix.boxlayout import BoxLayout
import math

def toArrayColor(color):
	if isinstance(color,str):
		color = get_color_from_hex(color)
		if len(color) == 3:
			color.append(1)
	return color
	
def distance(color1,color2):
	color1 = toArrayColor(color1)
	color2 = toArrayColor(color2)
	x = math.pow(abs(color2[0] - color1[0]),2) + \
		math.pow(abs(color2[1] - color1[1]),2) + \
		math.pow(abs(color2[2] - color1[2]),2)
	d = math.sqrt(x)
	return d

def reverseColor(color):
	center = [0.5,0.5,0.5]
	if color == [0.5,0.5,0.5]:
		return [1,1,1]
	d = distance(color,center)
	d1 = d + 0.5
	point= [0,0,0]
	for i in range(3):
		m = color[i] - center[i]
		m1 = abs(m) * d1 / d
		point[i] = color[i] - m1 if m < 0 else color[i] + m1
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
