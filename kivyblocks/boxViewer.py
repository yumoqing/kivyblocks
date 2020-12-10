"""
BoxViewer options:
{
	"dataloader":{
		"url",
		"method",
		"params"
		"filter":{
		}
	}
	"boxwidth",
	"boxheight",
	"viewer"
	"toolbar":{
	}
}
"""
from traceback import print_exc
from functools import partial
from appPublic.dictExt import dictExtend
from kivy.app import App
from kivy.factory import Factory
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from .responsivelayout import VResponsiveLayout
from .toolbar import Toolbar
from .paging import Paging, RelatedLoader
from .utils import CSize
from .ready import WidgetReady


class BoxViewer(WidgetReady, BoxLayout):
	def __init__(self, **options):
		self.options = options
		self.subwidgets = []
		self.toolbar = None
		self.parenturl = None
		self.dataloader = None
		self.initflag = False
		remind = ['toolbar',
				'dataloader',
				'orientation',
				'viewer',
				'boxwidth',
				'boxheight',
				'color_level',
				'radius',
				'viewer_url'
				'viewer'
				]
		kwargs = {k:v for k,v in options.items() if k not in remind }
		BoxLayout.__init__(self, orientation='vertical', **kwargs)
		WidgetReady.__init__(self)
		self.selected_data = None
		self.color_level = self.options.get('color_level',-1)
		self.radius = self.options.get('radius',[])
		self.box_width = CSize(options['boxwidth'])
		self.box_height = CSize(options['boxheight'])
		self.viewContainer = VResponsiveLayout(cols=2,box_width=self.box_width)
		if options.get('toolbar'):
			self.toolbar = Toolbar(options['toolbar'])
		lopts = options['dataloader'].copy()
		if lopts.get('options'):
			lopts = lopts.get('options')
		self.dataloader = RelatedLoader(target=self,**lopts)
		self.dataloader.bind(on_deletepage=self.deleteWidgets)
		self.dataloader.bind(on_pageloaded=self.addPageWidgets)
		self.dataloader.bind(on_newbegin=self.deleteAllWidgets)
		self.params = self.options['dataloader']['options'].get('params',{})

		if self.toolbar:
			self.add_widget(self.toolbar)
		if self.dataloader.widget:
			self.add_widget(self.dataloader.widget)
			self.dataloader.bind(on_submit=self.getParams)
		self.add_widget(self.viewContainer)
		self.register_event_type('on_selected')
		self.viewContainer.bind(size=self.resetCols,
								pos=self.resetCols)
		self.viewContainer.bind(on_scroll_stop=self.on_scroll_stop)
		# use_keyboard() will block the python
		# no reason !!!!
		# self.use_keyboard()

	def key_handle(self,keyinfo):
		print('keyinfo=',keyinfo,'...................')

	def getParams(self,o,p):
		self.params = p

	def deleteAllWidgets(self,o):
		self.viewContainer.clear_widgets()
		self.subwidgets = []

	def addPageWidgets(self,o,data):
		widgets = []
		recs = data['data']
		page = data['page']
		dir = data['dir']
		idx = 0
		if dir == 'up':
			recs.reverse()
			idx = -1
		for r in recs:
			self.showObject(widgets, r, index=idx)

		self.subwidgets += widgets

		self.dataloader.bufferObjects(page, widgets)
		x = self.dataloader.getLocater()
		self.locater(x)

	def deleteWidgets(self,o,data):
		for w in data:
			self.viewContainer.remove_widget(w)
		self.subwidget = [i for i in self.subwidgets if i in data]

	def on_selected(self, data=None):
		pass

	def locater(self, pos):
		self.viewContainer.scroll_y = pos

	def resetCols(self,o=None, v=None):
		h = 0
		if self.toolbar:
			h += self.toolbar.height
		if self.dataloader.widget:
			h += self.dataloader.widget.height
		self.viewContainer.height = self.height - h

		self.viewContainer.setCols()
		if not self.initflag:
			self.dataloader.loadPage(1)
			self.initflag = True

	def showObject(self, holders, rec,index=0):
		opts = {
			"size_hint":[None,None],
			"height":self.box_height,
			"width":self.box_width,
			"color_level":self.color_level,
			"radius":self.radius
		}
		desc = {
			"widgettype":"PressableBox",
			"options":opts
		}
		blocks = Factory.Blocks()
		box = blocks.w_build(desc)
		box.setValue(rec)
		box.bind(on_press=self.select_record)
		self.viewContainer.add_widget(box,index=index)
		self.subwidgets.append(box)
		holders.append(box)
		desc = {}
		if self.options.get('viewer_url'):
			desc = {
				"widgettype":"urlwidget",
				"optons":{
					"params":rec,
					"method":"GET",
					"url":self.options.get('viewer_url')
				}
			}
		else:
			desc = self.options.get('viewer').copy()
			if desc['widgettype'] == 'urlwidget':
				desc = dictExtend(desc,{'options':{'params':rec}})
			else:
				desc = dictExtend(desc,{'options':{'record':rec}})
		def add2box(p,o,w):
			p.add_widget(w)

		blocks = Factory.Blocks()
		blocks.bind(on_built=partial(add2box,box))
		blocks.widgetBuild(desc)

	def on_scroll_stop(self,o,v=None):
		if o.scroll_y <= 0.001:
			self.dataloader.loadNextPage()
		if o.scroll_y >= 0.999:
			self.dataloader.loadPreviousPage()

	def select_record(self,o,v=None):
		print('BoxViewer(),on_selected() called\n',
				'normal_bgcolor=',o.normal_bgcolor,'\n',
				'selected_bgcolor=',o.selected_bgcolor,'\n',
				'bg_color=',o.bgcolor,'\n',
				'color_level=',self.color_level)

		for w in self.subwidgets:
			w.unselected()
		o.selected()
		self.selected_data = o.getValue()
		self.dispatch('on_selected',self.selected_data)

	def getValue(self):
		return self.selected_data
		d = {
			"caller":self,
			"page_rows":1,
			"page":self.selected_data['__posInSet__'],
			"dataurl":self.options['dataloader']['options']['dataurl'],
			"params":self.params
		}
		return d
