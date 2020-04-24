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
		self.page_rows = options.get('page_rows',60)
		self.total_cnt = 0
		self.total_page = 0
		self.curpage = 0
		self.dir = 'down'
		self.register_event_type('on_newbegin')
		self.register_event_type('on_pageloaded')
	
	def getLocater(self):
		x = 1 / self.MaxbufferPage
		if self.dir != 'down':
			x = 1 - x
		print('getLocater(),x=%f,dir=%s,self.curpage=%d' % (x,self.dir,self.curpage))
		return x

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
		pass

	def do_search(self,o,params):
		print('PageLoader().do_search(), on_submit handle....',params)
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
		self.reload()
	
	def reload(self):
		if self.curpage == 0:
			self.curpage = 1
		self.loadPage(self.curpage)
	
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
		
	def httperror(self,o,e):
		traceback.print_exc()
		alert(str(e),title='alert')

	def loadPage(self,p):
		if not self.url:
			raise Exception('dataurl must be present:options=%s' % str(options))
		if self.curpage > p:
			self.dir = 'up'
		elif self.curpage == p:
			self.dir = 'reload'
		else:
			self.dir = 'down'
		self.curpage = p
		self.loading = True
		params = self.params.copy()
		params.update({
			"page":self.curpage,
			"rows":self.page_rows
		})
		realurl = absurl(self.url,self.target.parenturl)
		loader = HTTPDataHandler(realurl,params=params)
		loader.bind(on_success=self.show_page)
		loader.bind(on_failed=self.httperror)
		loader.handle()
	
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
'on_bufferraise': erase

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

	def on_deletepage(self,d):
		pass

	def setPageRows(self,row_cnt):
		if self.total_cnt != 0:
			self.calculateTotalPage()
		self.reload()
	
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
	
	def bufferObjects(self,objects):
		self.objectPages[self.curpage] = objects

	def show_page(self,o,data):
		if self.objectPages.get(self.curpage):
			self.deleteBuffer(self.curpage)
		else:
			self.doBufferMaintain()
		self.totalObj += len(data['rows'])
		super().show_page(o,data)
		self.loading = False
		print('buffer pages=',len(self.objectPages.keys()),'pages=',self.objectPages.keys())
	
	def loadPreviousPage(self):
		if self.loading:
			return

		pages = self.objectPages.keys()
		if len(pages) < 1:
			return

		page = min(pages)
		if page <= 1:
			return

		page -= 1
		self.loadPage(page)
	
	def loadNextPage(self):
		if self.loading:
			return
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
		self.adder = options.get('adder')
		self.clearer = options.get('clearer')
		self.target = options.get('target')
		self.init()

	def init(self):
		kwargs = {}
		kwargs['size_hint_y'] = None
		kwargs['height'] = CSize(2)
		kwargs['orientation'] = 'horizontal'
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

	def show_page(self,o,d):
		super().show_page(o,data)
		d = DictObject(**d)
		self.total_cnt = d.total
		self.calculateTotalPage()
		self.clearer()
		for r in d.rows:
			self.adder(r)
		self.loading = False

	def loadFirstPage(self,o=None):
		if self.curpage == 1:
			print('return not loading')
			return
		self.loadPage(1)
	
	def loadPreviousPage(self,o=None):
		if self.curpage < 2:
			print('return not loading')
			return
		self.loadPage(self.curpage-1)
	
	def loadNextPage(self,o=None):
		if self.curpage >= self.total_page:
			print('return not loading')
			return
		self.loadPage(self.curpage+1)
	
	def loadLastPage(self,o=None):
		if self.curpage >= self.total_page:
			print('return not loading')
			return
		self.loadPage(self.total_page)

class OneRecordLoader(PageLoader):
	def __init__(self,**options):
		PageLoader.__init__(self,**options)
		self.adder = options.get('adder')
		self.page_rows = 1

	def calculateTotalPage(self):
		self.total_page = self.total_cnt

	def show_page(self,o,d):
		self.adder(d['rows'][0])

