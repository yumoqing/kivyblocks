import math
from kivyblocks.graph import *
from kivy.utils import get_color_from_hex as rgb
from .threadcall import HttpClient

class Chart2d(Graph):
	"""
	json format:
	{
		"widgettype":"Chart2d",
		"options":{
			"xlabel":"Xlabel",
			"ylable":"Ylabel",
			"x_ticks_minor":1,
			"x_ticks_major":5,
			"y_ticks_minor":1,
			"y_ticks_major":5,
			"x_grid_label":true,
			"y_grid_label":true,
			"padding":5,
			"xlog":false,
			"ylog":false,
			"x_grid":true,
			"y_grid":true,
			"xmin":0,
			"xmax":100,
			"ymax":100,
			"ymin":1,
			"x_field":"xxx",
			"dataurl":"xxx",
			"charts":[
				{
					"y_field":"yy",
					"color":"efefef",
					"charttype":"LinePlot"
				}
			]
				
		}
	}
	"""
	plotmappings={
		"line":LinePlot,
		"hbar":BarPlot
	}
	default_options = {
		"x_grid_label":True,
		"y_grid_label":True,
		"xlabel":"Xlabel",
		"ylabel":"Ylabel",
		"xmin":0,
		"xmax":100,
		"ymax":100,
		"ymin":1,
		"x_grid":True,
		"y_grid":True,
		"padding":5,
		"xlog":False,
		"ylog":False,
		'x_ticks_minor':1,
		'x_ticks_major':5,
		"y_ticks_minor":1,
		"y_ticks_major":5,
		'label_options': {
			'color': rgb('444444'),  # color of tick labels and titles
		'bold': True},
		'background_color': rgb('f8f8f2'),  # canvas background color
		'tick_color': rgb('808080'),  # ticks and grid
		'border_color': rgb('808080')  # border drawn around each graph
	}

	def __init__(self, dataurl='', 
						data=None,
						x_field='',
						params={}, 
						headers={}, 
						charts=[], 
						**kw):
		self._dataurl = dataurl
		self._params = params
		self._headers = {}
		self.x_field = x_field
		self._data = data
		if not self._data:
			self._data = self.get_data()
		print('_data=',self._data, 'url=', self._dataurl)
		xmax = len(self._data)
		ymax = 0
		xvalue = [ self._data[i][self.x_field] for i in range(xmax) ]
		self._charts = charts
		print('charts=', charts)
		plots = []
		for c in charts:
			plotKlass = self.plotmappings.get(c['charttype'])
			if not plotKlass:
				print('charttype not defined', c)
				continue
			yvalue = [self._data[i][c['y_field']] for i in range(xmax)]
			print('yvalue=', yvalue)
			color = rgb(c.get('color','d8d8d8'))
			plot = plotKlass(color=color)
			plot.points = [(i,yvalue[i]) for i in range(xmax)] 
			plots.append(plot)
			maxv = max(yvalue)
			if ymax < maxv:
				ymax = maxv

		gkw = self.default_options.copy()
		gkw.update(kw)
		gkw['ymax'] = math.ceil(ymax)
		gkw['y_ticks_minor'] = gkw['ymax'] / 10
		gkw['y_ticks_major'] = gkw['ymax'] / 2
		gkw['x_ticks_minor'] = 1
		if gkw['x_ticks_major'] > xmax:
			gkw['x_ticks_major'] = xmax
		gkw['xmax'] = xmax
		print('gkw=', gkw)
		Graph.__init__(self, **gkw)

		print('plots=', plots)
		for p in plots:
			print('points=', p.points)
			self.add_plot(p)
			if hasattr(p,'bind_to_graph'):
				p.bind_to_graph(self)

	def get_data(self):
		hc = HttpClient()
		d = hc.get(self._dataurl,
				params=self._params,
				headers=self._headers)
		return d

