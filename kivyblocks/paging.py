import traceback
import math

from kivy.logger import Logger
from kivy.event import EventDispatcher
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.app import App
from functools import partial
from appPublic.dictObject import DictObject
from appPublic.jsonConfig import getConfig
from .baseWidget import Text, HTTPDataHandler
from .utils import CSize, absurl, alert
from .form import StrSearchForm
from .dataloader import UrlDataLoader
from .dataloader import ListDataLoader
from .dataloader import RegisterFunctionDataLoader

class PageLoader(EventDispatcher):
	def __init__(self,target=None, **options):
		self.loading = False
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
			self.loader = UrlDataLoader(self)
		elif self.rfname:
			self.loader = RegisterFunctionDataLoader(self)
		elif self.data:
			self.loader = ListDataLoader(self)
		else:
			raise Exception('need a url or rfname or data')
		self.loader.bind(on_success=self.show_page)
		self.loader.bind(on_error=self.onerror)
	
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
		d.update( {
			"page":self.curpage,
			"data":d['rows'],
			"dir":self.dir,
		})
		self.dispatch('on_pageloaded',d)
		self.loading = False
		
	def onerror(self,o,e):
		traceback.print_exc()
		alert(str(e),title='alert')
		self.loading = False

	def loadNextPage(self):
		if self.loading:
			print('is loading, return')
			return -1

		if self.total_page > 0 and self.curpage >=self.total_page:
			return -1
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
	
class RelatedLoader(PageLoader):
	def __init__(self, **options):
		super().__init__(**options)
		self.objectPages = {}
		self.totalObj = 0
		self.MaxbufferPage = 3
		self.buffered_pages = 0
		self.register_event_type('on_deletepage')

	def do_search(self,o,params):
		self.objectPages = {}
		self.totalObj = 0
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
		siz = len([k for k in self.objectPages.keys()])
		self.buffered_pages = siz
		if siz > self.MaxbufferPage:
			if self.dir == 'up':
				p = max(self.objectPages.keys())
			else:
				p = min(self.objectPages.keys())
			self.deleteBuffer(p)
			self.buffered_pages = self.MaxbufferPage

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
		self.bufferObjects(self.curpage, data['rows'])
		self.doBufferMaintain()
		self.totalObj += len(data['rows'])
		if self.dir == 'down':
			data['locator'] = 1/self.buffered_pages
		else:
			data['locator'] = 1 - 1/self.buffered_pages

		super().show_page(o,data)
	
	def loadPreviousPage(self):
		pages = self.objectPages.keys()
		if len(pages) < 1:
			print('self.objectPages is null')
			return

		page = min(pages)
		if page <= 1:
			print('page < 1')
			return

		page -= 1
		self.loadPage(page)
	
	def loadNextPage(self):
		pages = self.objectPages.keys()
		if len(pages) == 0:
			print('self.objectPages is null')
			return
		page = max(pages)
		if page>=self.total_page:
			print('page > total page')
			return
		page += 1
		self.loadPage(page)

