
from kivy.event import EventDispatcher
from kivy.app import App
from kivy.factory import Factory
from .threadcall import HttpClient
from .utils import absurl
from appPublic.registerfunction import RegisterFunction

class DataGraber(EventDispatcher):
	"""
	Graber format
	{
		"widgettype":"DataGraber",
		"options":{
			"dataurl":"first",
			"datarfname":"second",
			"target":"third",
			"params":
			"method":
			"pagging":"default false"
		}
	}
	if dataurl present, the DataGraber using this dataurl to get and 
		return data
	else if datarfname present, it find a registered function named 
		by 'datarfname' to return data
	else if datatarget present, it find the widget and uses target
		method(default is 'getValue') to return data
	else it return None
	"""
	def __init__(self, **kw):
		super().__init__()
		self.options = kw
		self.register_event_type('on_success')
		self.register_event_type('on_error')

	def load(self, *args, **kw):
		ret = None
		while True:
			try:
				dataurl = self.options.get('dataurl')
				if dataurl:
					ret = self.loadUrlData(*args, **kw)
					break

				rfname = self.options.get('datarfname')
				if rfname:
					ret = self.loadRFData(*args, **kw)
					break
				target = self.options.get('datatarget')
				if target:
					ret = self.loadTargetData(*args, **kw)
					break
			except Exception as e:
				self.dispatch('on_error', e)
				return
		if ret:
			self.dispatch('on_success',ret)
		else:
			e = Exception('Not method to do load')
			self.dispatch('on_error', e)

	def loadUrlData(self, *args, **kw):
		dataurl = self.options.get('dataurl')
		hc = HttpClient()
		params = self.options.get('params',{}).copy()
		params.update(kw)
		method = self.options.get('method','GET')
		d = hc(dataurl, params=params,method=method)
		return d

	def loadRFData(self, *args, **kw):
		rfname = self.options.get('datarfname')
		rf = RegisterFunction()
		f = rf.get(rfname)
		if not f:
			return None
		params = self.options.get('params',{}).copy()
		params.update(kw)
		try:
			d = f(**params)
			return d
		except Exception as e:
			Logger.info('blocks : Exception:%s',e)
			print_exc()
		return None

	def loadTargetData(self, *args, **kw):
		target = self.options.get('datatarget')
		w = Factory.Blocks.getWidgetById(target)
		if not w:
			return None
		params = self.options.get('params',{}).copy()
		params.update(kw)
		method = params.get('method', 'getValue')
		if not has(w, method):
			return None
		try:
			f = getattr(w, method)
			d = f()
			return d
		except Exception as e:
			Logger.info('blocks : Exception %s', e)
			print_exc()
		return None

	def on_success(self,d):
		pass

	def on_error(self,e):
		pass
	
class DataLoader(EventDispatcher):
	def __init__(self,data_user):
		self.data_user = data_user
		EventDispatcher.__init__(self)
		self.register_event_type('on_success')
		self.register_event_type('on_error')

	def on_success(self,d):
		pass

	def on_error(self,e):
		pass
	
	def load(self):
		pass

class HttpDataLoader(DataLoader):
	def load(self, *args, **kw):
		app = App.get_running_app()
		url = app.realurl(self.data_user.url)
		method = self.data_user.method
		params = self.data_user.params.copy()
		params.update({
			"page":self.data_user.curpage,
			"rows":self.data_user.page_rows
		})
		hc = HttpClient()
		try:
			r = hc(url, method=method, params=params)
			self.dispatch('on_success', r)
			return r
		except Exception as e:
			self.dispatch('on_error', e)


class ListDataLoader(DataLoader):
	def load(self, *args, **kw):
		p = self.data_user.curpage
		r = self.data_user.page_rows
		try:
			s = self.data_user.data[(p-1)*r:p*r]
			d = {
				"total":len(self.data_user.data),
				"rows":s
			}
			self.dispatch('on_success', d)
			return d
		except Exception as e:
			self.dispatch('on_error', e)

class RegisterFunctionDataLoader(DataLoader):
	def load(self, *args, **kw):
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
			self.dispatch('on_success', s)
			return s
		except Exception as e:
			self.dispatch('on_error', e)


