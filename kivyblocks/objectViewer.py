from kivy.utils import platform
from .responsivelayout import VResponsiveLayout
from .utils import isHandHold
from .paging import RelatedLoader

"""
options format
{
	box_width:optional, if set, the child width
	dataurl: url to get data
	page_rows:records per read 
	viewer:{
		widgettype:an class name to show the object
		options:{
		}
	},
	binds:[
		bind info
	]
}
	
"""

class ObjectViewer(VResponsiveLayout):
	def __init__(self, dataurl=None, viewer={}, 
					page_rows=25,params={},**options):
		super().__init__(**options)
		self.options = options
		self.dataUrl = dataurl
		self.params = params
		self.viewer = viewer
		self.page_rows = page_rows
		self.initflag = False
	

	def setScrollPos(self,pos):
		print('setScrollPos(),pos=',pos)
		self.scroll_y = pos

	def sizeChangedWork(self,v=None):
		super().sizeChangedWork()
		if not self.initflag:
			self.initflag = True
			self.loader = RelatedLoader(
							adder=self.showObject,
							remover=self.remove_widget,
							locater=self.setScrollPos,
							page_rows=self.page_rows,
							dataurl=self.dataUrl,
							target=self,
							params=self.params,
							method=self.options.get('method','GET')
			)
			self.loader.loadPage(1)
			print('ObjectViewer:::::::::::::self.size=',self.size)
	
	def on_scroll_stop(self,o,v=None):
		return 
		print('on_scroll_stop(), self.scroll_y=', self.scroll_y,
				self._inner.pos,
				self._inner.size,
				self.size)
		if self.scroll_y >=0.999:
			print('on_scroll_stop(), move_up')
			self.loader.loadPreviousPage()
		if self.scroll_y <= 0.001:
			print('on_scroll_stop(), move_down')
			self.loader.loadNextPage()

	def showObject(self,rec,**kw):
		pass
