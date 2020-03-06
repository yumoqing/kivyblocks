import math
import numpy as np

class Point(object):
	def __init__(self, x=0, y=0):
		super().__init__()
		self.x = x
		self.y = y

class Line(object):  # 直线由两个点组成    
	def __init__(self, p1, p2):
		if isinstance(p1,list) or isinstance(p1,tuple):
			self.p1 = Point(*p1)
		else:
			self.p1 = p1
		if isinstance(p2,list) or isinstance(p2,tuple):
			self.p2 = Point(*p2)
		else:
			self.p2 = p2     
	
	def vector(self):
		return self.p1.x - self.p2.x,self.p1.y - self.p2.y

	def lenght(self):
		return math.sqrt(pow((self.p1.x - self.p2.x), 2)
					+ pow((self.p1.y - self.p2.y), 2))

	def get_cross_angle(self, l):        
		# 向量a        
		arr_a = np.array(self.vector())
		# 向量b        
		arr_b = np.array(l.vector())
		cos_value = float(arr_a.dot(arr_b)) / (np.sqrt(arr_a.dot(arr_a)) \
						* np.sqrt(arr_b.dot(arr_b)))  
		# 注意转成浮点数运算        
		return np.arccos(cos_value) * (180 / np.pi)  
		# 两个向量的夹角的角度， 
		# 余弦值：cos_value, np.cos(para), 
		# 其中para是弧度，不是角度

class EllipseUtils(object):
	def __init__(self,pos,size):
		self.pos = Point(pos)
		self.size = size
		self.slides = []
		super().__init__()

	def split(self,data,colors):
		self.slides = []
		kvs = [ [i[self.options['keyField']],i[self.options['valueField']]] for i in data ]
		total = sum([i[1] for i in kvs ])
		start_degree = 0
		cnt = len(kvs)
		for i in range(cnt):
			degree = start_degree + 360 * kvs[i][1] / total
			self.slides.append((degress,colors[i]))
			start_degree = degree
		
	def isInside(self,a,b,x,y):
		if a>b:
			return x**x / a**a + y**y/b**b <= 1
		return x**x / b**b + y**y / a**a <= 1

	def collide_point(self,x,y):
		a = float(self.size[0] / 2)
		b = float(self.size[1] / 2)
		x = x - self.pos[0]
		y = y - self.pos[1]
		if not self.isInside(a,b,x,y):
			return -1
		start_degress = 0
		l = Line((a,b),(a,b*2))
		l1 = Line((a,b),(x,y))
		degress = l.get_cross_angle(l1)
		if x < a:
			degress = 360 - degress
		for i in range(len(self.slides)):
			if start_degress <= degress and degress < self.slides[i][0]:
				return i
			start_degress += self.slides[i][0]
		return -1
