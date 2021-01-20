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
	graph_theme = {
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
		xmax = len(data)
		ymax = 0
		xvalues = [ self._data[i][self.x_field] for i in range(xmax) ]
		self._charts = charts
		plots = []
		for c in charts:
			plotKlass = self.plotmappings.get('charttype')
			if not plot:
				continue
			yvalue = [self._data[i][c['y_field']] for i in range(xmax)]
			color = rgb(c.get('color','d8d8d8'))
			plot = plotKlass(color=color)
			plot.points = [(xvalue[i],yvalue[i]) for i in range(xmax)] 
			plots.append(plot)
			maxv = max(yvalue)
			if ymax < maxv:
				ymax = maxv

		gkw = kw.copy()
		gkw['ymax'] = ymax
		gkw['xmax'] = xmax
		Graph.__init__(self, **kw)
		self.ymax = ymax

		for p in plots:
			self.add_plot(p)
			p.bind_to_graph(self)

	def get_data(self):
		hc = HttpClient()
		d = hc.get(self._dataurl,
				params=self._params,
				headers=self._headers)
		return d

