import traceback
import math

from kivy.logger import Logger
from kivy.event import EventDispatcher
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.app import App
from kivy.properties import BooleanProperty
from functools import partial
from appPublic.dictObject import DictObject
from appPublic.jsonConfig import getConfig
from .baseWidget import Text, HTTPDataHandler
from .utils import CSize, absurl, alert
from .form import StrSearchForm
from .dataloader import HttpDataLoader
from .dataloader import ListDataLoader
from .dataloader import RegisterFunctionDataLoader

class PagingButton(Button):
	def __init__(self, **kw):
		super().__init__(**kw)
		self.size_hint = (None,None)
		self.size = CSize(2,1.8)
		self.font_size = CSize(1)

"""
{
	dataurl
	params
	method
	locater
	filter
}

PageLoader load data in a page size once.
it fires two type of event
'on_newbegin':fire when start a new parameters loading series
'on_pageloaded':fire when a page data loads success
"""

class PageLoader(EventDispatcher):
	loading = BooleanProperty(False)
	def __init__(self,target=None, **options):
		self.target = target
		self.options = options
		self.filter = None
		if options.get('filter'):
			self.filter = StrSearchForm(**options['filter'])
			self.filter.bind(on_submit=self.do_search)
		self.params = options.get('params',{})
		self.method = options.get('method','GET')
		self.url = options.get('dataurl')
		self.rfname = options.get('rfname')
		self.data = options.get('data')
		self.page_rows = options.get('page_rows',60)
		self.total_cnt = 0
		self.total_page = 0
		self.curpage = 0
		self.dir = 'down'
		self.register_event_type('on_newbegin')
		self.register_event_type('on_pageloaded')
		self.newbegin = True
		if self.url:
			self.loader = HttpDataLoader(self)
		elif self.rfname:
			self.loader = RegisterFunctionDataLoader(self)
		elif self.data:
			self.loader = ListDataLoader(self)
		else:
			raise Exception('need a url or rfname or data')
		self.loader.bind(on_success=self.show_page)
		self.loader.bind(on_error=self.onerror)
	
	def on_loading(self, *args):
		if self.loading:
			self.running = Running(self.target)
		else:
			self.running.dismiss()

	def on_newbegin(self):
		pass

	def on_pageloaded(self,d):
		"""
		d={
			page:
			data:[]
			dir:'up' or 'down'
		}
		"""

	def do_search(self,o,params):
		self.newbegin = True
		self.total_cnt = 0
		self.total_page = 0
		self.curpage = 0
		self.dir = 'down'
		self.dispatch('on_newbegin')
		self.params.update(params)
		self.loadPage(1)

	def calculateTotalPage(self):
		self.total_page = math.floor(self.total_cnt / self.page_rows)
		if self.total_cnt % self.page_rows != 0:
			self.total_page += 1

	def setPageRows(self,row_cnt):
		if row_cnt == 0:
			return 
		self.page_rows = row_cnt
		if self.total_cnt != 0:
			self.calculateTotalPage()
	
	def show_page(self,o,d):
		p = (self.curpage - 1) * self.page_rows + 1
		for r in d['rows']:
			r['__posInSet__'] = p
			p += 1
		self.total_cnt = d['total']
		self.calculateTotalPage()
		d = {
			"page":self.curpage,
			"dir":self.dir,
			"data":d['rows']
		}
		self.dispatch('on_pageloaded',d)
		self.loading = False
		
	def onerror(self,o,e):
		traceback.print_exc()
		alert(str(e),title='alert')
		self.loading = False

	def loadNextPage(self):
		if self.loading:
			print('is loading, return')
			return

		if self.total_page > 0 and self.curpage >=self.total_page:
			return
		p = self.curpage + 1
		self.loadPage(p)

	def loadPreviousPage(self):
		if self.loading:
			print('is loading, return')
			return

		if self.curpage <= 1:
			return
		p = self.curpage - 1
		self.loadPage(p)

	def loadPage(self,p):
		if p == self.curpage:
			return

		if self.loading:
			print('is loading, return')
			return

		self.loading = True
		print(f'loading {p} page, {self.curpage}')
		if self.curpage > p:
			self.dir = 'up'
		else:
			self.dir = 'down'
		self.curpage = p
		self.loader.load()
	
"""
{
	adder,
	remover
	target,
	locater,
	dataurl,
	params,
	method,
	filter
}
events:
'on_deletepage': erase

"""
class RelatedLoader(PageLoader):
	def __init__(self, **options):
		super().__init__(**options)
		self.objectPages = {}
		self.totalObj = 0
		self.MaxbufferPage = 3
		self.locater = 1/self.MaxbufferPage
		if self.filter:
			self.widget = self.filter
		else:
			self.widget = None
		self.register_event_type('on_deletepage')

	def do_search(self,o,params):
		self.objectPages = {}
		self.totalObj = 0
		self.MaxbufferPage = 3
		self.locater = 1/self.MaxbufferPage
		super().do_search(o, params)
		
	def getLocater(self):
		if self.newbegin:
			self.newbegin = False
			return 1

		x = 1 / self.MaxbufferPage
		if self.dir != 'down':
			x = 1 - x
		return x

	def on_deletepage(self,d):
		pass

	def setPageRows(self,row_cnt):
		if self.total_cnt != 0:
			self.calculateTotalPage()
	
	def doBufferMaintain(self):
		siz = len(self.objectPages.keys())
		if siz >= self.MaxbufferPage:
			if self.dir == 'up':
				p = max(self.objectPages.keys())
			else:
				p = min(self.objectPages.keys())
			self.deleteBuffer(p)

	def deleteBuffer(self,page):
		d = self.objectPages[page]
		self.dispatch('on_deletepage',d)
		self.totalObj -= len(self.objectPages[page])
		del self.objectPages[page]
	
	def bufferObjects(self,page,objects):
		self.objectPages[page] = objects


	def show_page(self,o,data):
		if self.objectPages.get(self.curpage):
			self.deleteBuffer(self.curpage)
		else:
			self.doBufferMaintain()
		self.totalObj += len(data['rows'])
		super().show_page(o,data)
	
	def loadPreviousPage(self):
		pages = self.objectPages.keys()
		if len(pages) < 1:
			return

		page = min(pages)
		if page <= 1:
			return

		page -= 1
		self.loadPage(page)
	
	def loadNextPage(self):
		pages = self.objectPages.keys()
		if len(pages) == 0:
			return
		page = max(pages)
		if page>=self.total_page:
			return
		page += 1
		self.loadPage(page)

"""
{
	adder,
	clearer
	target,
	dataurl
	params,
	method
}
"""
class Paging(PageLoader):
	def __init__(self,**options):
		PageLoader.__init__(self,**options)
		self.target = options.get('target')
		self.init()

	def init(self):
		kwargs = {}
		kwargs['size_hint_y'] = None
		kwargs['height'] = CSize(2)
		kwargs['orientation'] = 'horizontal'
		kwargs['spacing'] = CSize(1)
		self.widget = BoxLayout(**kwargs)
		self.b_f = PagingButton(text="|<")
		self.b_p = PagingButton(text="<")
		self.b_n = PagingButton(text=">")
		self.b_l = PagingButton(text=">|")
		self.b_f.bind(on_press=self.loadFirstPage)
		self.b_p.bind(on_press=self.loadPreviousPage)
		self.b_n.bind(on_press=self.loadNextPage)
		self.b_l.bind(on_press=self.loadLastPage)
		self.widget.add_widget(self.b_f)
		self.widget.add_widget(self.b_p)
		self.widget.add_widget(self.b_n)
		self.widget.add_widget(self.b_l)
		if self.filter:
			self.widget.add_widget(self.filter)

	def loadFirstPage(self,o=None):
		if self.curpage == 1:
			return
		self.loadPage(1)
	
	def loadPreviousPage(self,o=None):
		if self.curpage < 2:
			return
		self.loadPage(self.curpage-1)
	
	def loadNextPage(self,o=None):
		if self.curpage >= self.total_page:
			return
		self.loadPage(self.curpage+1)
	
	def loadLastPage(self,o=None):
		if self.curpage >= self.total_page:
			return
		self.loadPage(self.total_page)

