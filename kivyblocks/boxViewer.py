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
from kivy.app import App
from kivy.factory import Factory
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from .responsivelayout import VResponsiveLayout
from .toolbar import Toolbar
from .paging import Paging, RelatedLoader
from .utils import CSize

class BoxViewer(BoxLayout):
	def __init__(self, **options):
		self.toolbar = None
		self.parenturl = None
		self.dataloader = None
		self.initflag = False
		BoxLayout.__init__(self, orientation='vertical')
		self.selected_data = None
		self.options = options
		self.box_width = CSize(options['boxwidth'])
		self.box_height = CSize(options['boxheight'])
		self.viewContainer = VResponsiveLayout(cols=2,box_width=self.box_width)
		if options.get('toolbar'):
			self.toolbar = Toolbar(options['toolbar'])
		lopts = options['dataloader'].copy()
		self.dataloader = RelatedLoader(target=self,**lopts['options'])
		self.dataloader.bind(on_deletepage=self.deleteWidgets)
		self.dataloader.bind(on_pageloaded=self.addPageWidgets)
		self.dataloader.bind(on_newbegin=self.deleteAllWidgets)

		if self.toolbar:
			self.add_widget(self.toolbar)
		if self.dataloader.widget:
			self.add_widget(self.dataloader.widget)
		self.add_widget(self.viewContainer)
		self.register_event_type('on_selected')
		self.viewContainer.bind(size=self.resetCols,
								pos=self.resetCols)
		self.viewContainer.bind(on_scroll_stop=self.on_scroll_stop)

	def deleteAllWidgets(self,o):
		self.viewContainer.clear_widgets()

	def addPageWidgets(self,o,data):
		widgets = []
		recs = data['data']
		dir = data['dir']
		idx = 0
		if dir == 'up':
			recs.reverse()
			idx = -1
		print('addPageWidgets(),begin')
		for r in recs:
			self.showObject(widgets, r, index=idx)

		print('addPageWidgets(),widgets=',len(widgets))
		self.dataloader.bufferObjects(widgets)
		x = self.dataloader.getLocater()
		self.locater(x)

	def deleteWidgets(self,o,data):
		for w in data:
			self.viewContainer.remove_widget(w)

	def on_selected(self, o, v=None):
		print('BoxViewer(): on_selected fired....')

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
		def doit(self,holders,idx,o,w):
			print('showObject()...doit(),w=',w,o)
			w.bind(on_press=self.select_record)
			self.viewContainer.add_widget(w,index=idx)
			holders.append(w)

		def doerr(o,e):
			print_exc()
			print('showObject(),error=',e)
			raise e
		options = self.options['viewer'].copy()
		options['options']['record'] = rec
		options['options']['ancestor'] = self
		options['options']['size_hint'] = None,None
		options['options']['width'] = self.box_width
		options['options']['height'] = self.box_height
		blocks = Factory.Blocks()
		blocks.bind(on_built=partial(doit,self,holders,index))
		blocks.bind(on_failed=doerr)
		blocks.widgetBuild(options, ancestor=self)

	def on_scroll_stop(self,o,v=None):
		if o.scroll_y <= 0.001:
			self.dataloader.loadNextPage()
		if o.scroll_y >= 0.999:
			self.dataloader.loadPreviousPage()

	def select_record(self,o,v=None):
		self.selected_data = o.getRecord()
		self.dispatch('on_selected',o.getRecord())

	def getData(self):
		self.selected_data['__dataloader__'] = self.dataloader
		return self.selected_data
