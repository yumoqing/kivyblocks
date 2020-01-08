import traceback
import math

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.app import App
from functools import partial
from appPublic.dictObject import DictObject
from appPublic.jsonConfig import getConfig
from .baseWidget import Text
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
"""

class HttpLoader:
	def __init__(self, url, method, params):
		self.page_rows = page_rows
		self.url = url
		self.method = method,
		self.params = params
	
	def setParams(self,params):
		self.params = params

	def load(self, callback, errback):
		hc = App.get_running_app().hc
		x = hc(self.url,
				method=self.method,
				params=self.params,
				callback=callback,
				errback=errback)
		
class PageLoader:
	def __init__(self, **options):
		self.loading = False
		self.filter = None
		if options.get('filter'):
			self.filter = StrSearchForm(**options['filter'])
			self.filter.bind(on_submit=self.do_search)

		self.params = options.get('params',{})
		self.method = options.get('method','GET')
		self.url = options.get('dataurl')
		self.total_cnt = 0
		self.total_page = 0
		self.page_rows = options.get('page_rows',0)
		self.curpage = 0
	
	def do_search(self,o,params):
		print('PageLoader().do_search(), on_submit handle....',params)
		self.clearer()
		self.params.update(params)
		print('do_search():,params=',self.params)
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
	
	def setDir(self):
		pages = self.objectPages.keys()
		if len(pages)==0:
			self.dir = 'down'
			return
		if self.curpage >= max(self.objectPages.keys()):
			self.dir = 'down'
		else:
			self.dir = 'up'

	def show_page(self,o,d):
		p = (self.curpage - 1) * self.page_rows + 1
		for r in d['rows']:
			r['__posInSet__'] = p
			p += 1

	def loadPage(self,p):
		if not self.url:
			raise Exception('dataurl must be present:options=%s' % str(options))
		self.curpage = p
		self.loading = True
		params = self.params.copy()
		params.update({
			"page":self.curpage,
			"rows":self.page_rows
		})
		hc = App.get_running_app().hc
		url = absurl(self.url,self.target.parenturl)
		# print('loadPage():url=',url,'params=',params)
		x = hc(url,method=self.method,
				params=params,callback=self.show_page,
				errback=self.httperror)
	
	def httperror(self,o,e):
		traceback.print_exc()
		alert(str(e),title='alert')

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
"""
class RelatedLoader(PageLoader):
	def __init__(self, **options):
		super().__init__(**options)
		self.adder = options.get('adder')
		self.locater = options.get('locater',None)
		self.remover = options.get('remover')
		self.clearer = options.get('clearer')
		self.target = options.get('target')
		self.objectPages = {}
		self.totalObj = 0
		self.MaxbufferPage = 3
		if self.filter:
			self.widget = self.filter
		else:
			self.widget = None

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
		for w in self.objectPages[page]:
			self.remover(w)
		self.totalObj -= len(self.objectPages[page])
		del self.objectPages[page]
			
	def show_page(self,o,data):
		super().show_page(o,data)
		if self.objectPages.get(self.curpage):
			self.deleteBuffer(self.curpage)
		else:
			self.setDir()
			self.doBufferMaintain()
		self.total_cnt = data['total']
		self.calculateTotalPage()
		widgets = []
		rows = data['rows']
		if self.dir == 'up':
			rows.reverse()
		for r in rows:
			if self.dir == 'up':
				w = self.adder(r,index=self.totalObj)
			else:
				w = self.adder(r)
			widgets.append(w)
			self.totalObj += 1
		self.objectPages[self.curpage] = widgets
		pages = len(self.objectPages.keys())
		loc = 1.0 / float(pages)
		if self.locater:
			if pages == 1:
				self.locater(1)
			elif self.dir == 'up':
				self.locater(1 - loc)
			else:
				self.locater(loc)

		self.loading = False
		print('buffer pages=',len(self.objectPages.keys()),'pages=',self.objectPages.keys())
	
	def loadPreviousPage(self):
		if self.loading:
			return

		pages = self.objectPages.keys()
		if len(pages) < 1:
			return

		self.curpage = min(pages)
		if self.curpage <= 1:
			return

		self.curpage -= 1
		self.loadPage(self.curpage)
	
	def loadNextPage(self):
		if self.loading:
			return
		pages = self.objectPages.keys()
		if len(pages) == 0:
			return
		self.curpage = max(pages)
		if self.curpage>=self.total_page:
			return
		self.curpage += 1
		self.loadPage(self.curpage)

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

