
from kivy.event import EventDispatcher
from .threadcall import HttpClient
from appPublic.registerfunction import RegisterFunction

class DataLoader(EventDispatcher):
	def __init__(self,data_user):
		self.data_user = data_user
		EventDispatcher.__init__(self)
		self.register_event_type('on_success')
		self.register_event_type('on_error')

	def success(self,o,d):
		self.dispatch('on_success',d)
	
	def error(self,o,e):
		self.dispatch('on_error',e)

	def on_success(self,d):
		pass

	def on_error(self,e):
		pass
	
	def load(self):
		pass

class HttpDataLoader(DataLoader):
	def load(self):
		url = absurl(self.data_user.url,self.data_user.target.parenturl)
		self.data_user.curpage = p
		method = self.data_user.method
		params = self.data_user.params.copy()
		params.update({
			"page":self.data_user.curpage,
			"rows":self.data_user.page_rows
		})
		hc = HttpClient()
		hc(self.url,
				method=method,
				params=params,
				callback=self.on_success,
				errback=self.error)

class ListDataLoader(DataLoader):
	def load(self):
		p = self.data_user.curpage
		r = self.data_user.page_rows
		try:
			s = self.data_user.data[(p-1)*r:p*r]
			d = {
				"total":len(self.data_user.data),
				"rows":s
			}
			self.success(self,d)
		except Exception as e:
			self.error(self,e)

class RegisterFunctionDataLoader(DataLoader):
	def load(self):
		rf = RegisterFunction()
		try:
			rfname = self.data_user.rfname
			func = rf.get(rfname)
			if func is None:
				raise Exception('%s is not a registerfunction' % rfname)
			params = {k:v for k,v in self.user_data.params.items()}
			params.update({
				"page":self.data_user.curpage,
				"rows":self.data_user.page_rows
			})
			s = func(**params)
			self.success(self,s)
		except Exception as e:
			self.error(self,e)

