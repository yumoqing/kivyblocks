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
from functools import partial

from traceback import print_exc
from functools import partial
from appPublic.dictExt import dictExtend
from kivy.app import App
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Fbo, Color, Rectangle
from kivy.properties import NumericProperty, StringProperty, DictProperty
from .responsivelayout import VResponsiveLayout
from .toolbar import Toolbar
from .paging import Paging, RelatedLoader
from .utils import CSize, SUPER
from .ready import WidgetReady
from .baseWidget import VBox


class BoxViewer(VBox):
	toolbar = DictProperty(None)
	dataloader = DictProperty(None)
	boxwidth = NumericProperty(None)
	boxwidth_c = NumericProperty(None)
	boxheight = NumericProperty(None)
	boxheight_c = NumericProperty(None)
	viewer = DictProperty(None)
	viewer_url = StringProperty(None)
	viewer_css = StringProperty('viewer_css')
	def __init__(self, **options):
		self.subwidgets = []
		self.toolbar_w = None
		self._dataloader = None
		self.initflag = False
		SUPER(BoxViewer, self, options)
		self.selected_data = None
		self.viewContainer = VResponsiveLayout(box_width=self.box_width)
		if self.toolbar:
			self.toolbar_w = Toolbar(self.toolbar)
		lopts = self.dataloader.get('options', {}).copy()
		self._dataloader = RelatedLoader(target=self,**lopts)
		self._dataloader.bind(on_deletepage=self.deleteWidgets)
		self._dataloader.bind(on_pageloaded=self.addPageWidgets)
		self._dataloader.bind(on_newbegin=self.deleteAllWidgets)
		self.params = lopts.get('params',{})

		if self.toolbar_w:
			self.add_widget(self.toolbar_w)
		if self._dataloader.widget:
			self.add_widget(self._dataloader.widget)
			self._dataloader.widget.bind(on_submit=self.getParams)
		self.add_widget(self.viewContainer)
		self.register_event_type('on_selected')
		self.bind(size=self.resetCols,
								pos=self.resetCols)
		self.viewContainer.bind(on_scroll_stop=self.on_scroll_stop)

	def on_boxheight(self, *args):
		self.box_height = self.boxheight

	def on_boxheight_c(self, *args):
		self.box_height = CSize(self.boxheight_c)

	def on_boxwidth_c(self, *args):
		self.box_width = CSize(self.boxwidth_c)

	def on_boxwidth(self, *args):
		self.box_width = self.boxwidth

	def key_handle(self,keyinfo):
		print('keyinfo=',keyinfo,'...................')

	def getParams(self,o,p):
		self.params = p

	def deleteAllWidgets(self,o):
		self.viewContainer.clear_widgets()
		self.subwidgets = []
	
	def getShowRows(self):
		wc = self.viewContainer.get_cols()
		hc = int(self.viewContainer.height / self.box_height)
		self.show_rows = wc * hc

	def addPageWidgets(self,o,data):
		widgets = []
		recs = data['data']
		page = data['page']
		dir = data['dir']
		idx = 0
		if dir == 'up':
			recs.reverse()
			idx = -1
		with self.fboContext():
			for r in recs:
				self.showObject(widgets, r, index=idx)
		
		data['widgets'] = widgets
		data['idx'] = idx

	def add_page_delay(self, data, *args):
		recs = data['data']
		page = data['page']
		idx = data['idx']
		widgets = data['widgets']

		self._fbo = Fbo(size=self.size)
		with self._fbo:
			self._background_color = Color(0,0,0,1)
			self._background_rect = Rectangle(size=self.size)
		for r in recs:
			self.showObject(widgets, r, index=idx)
		with self.canvas:
			self._fbo_rect = Rectangle(size=self.size,
								texture=self._fbo.texture)

		self.subwidgets += widgets

		self._dataloader.bufferObjects(page, widgets)
		x = self._dataloader.getLocater()
		self.locater(x)

	def loadData(self, **kw):
		self.params = kw
		self.deleteAllWidgets(None)
		self._dataloader.loadPage(1)
		self.initflag = True

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
		if self._dataloader.widget:
			h += self._dataloader.widget.height
		self.viewContainer.height = self.height - h

		self.viewContainer.setCols()
		self.getShowRows()
		if not self.initflag:
			self._dataloader.loadPage(1)
			self.initflag = True

	def showObject(self, holders, rec,index=0):
		opts = {
			"csscls":self.viewer_css
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
		if self.viewer_url:
			desc = {
				"widgettype":"urlwidget",
				"options":{
					"params":rec,
					"method":"GET",
					"url":self.viewer_url
				}
			}
		else:
			desc = self.viewer.copy()
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
			self._dataloader.loadNextPage()
		if o.scroll_y >= 0.999:
			self._dataloader.loadPreviousPage()

	def select_record(self,o,v=None):
		for w in self.subwidgets:
			w.box_actived = False
		o.box_actived = True
		self.selected_data = o.getValue()
		self.dispatch('on_selected',self.selected_data)

	def getValue(self):
		return self.selected_data
		d = {
			"caller":self,
			"page_rows":1,
			"page":self.selected_data['__posInSet__'],
			"dataurl":self.dataloader['options']['dataurl'],
			"params":self.params
		}
		return d
