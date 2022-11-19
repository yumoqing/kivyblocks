from kivy.event import EventDispatcher

class DataLoader(EventDispatcher):
	def __init__(self,**kw):
		self.register_event_type('on_loaded')
		self.register_event_type('on_loaderror')
		super(DataLoader,self).__init__(**kw)
	
	def loadData(self):
		pass
		
	def dataLoaded(self,d):
		self.dispatch('on_loaded',d)
		
	def loadError(self,e):
		self.dispatch('on_loaderror',e)

	def on_loaded(self,d):
		pass #print('on_loaded,data=',d)

	def on_loaderror(self,a,e):
		pass #print('error:',e)
