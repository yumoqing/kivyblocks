from functools import partial
from kivy.event import EventDispatcher
from kivy.clock import Clock
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient

class OSCServer(EventDispatcher):
	def __init__(self,addr='0.0.0.0', port=60405,apis=[]):
		self.port = port
		self.addr = addr
		self.osc_server = OSCThreadServer()
		self.osc_server.listen(self.addr,port=self.port,default=True)
		EventDispatcher.__init__(self)
		for api in apis:
			self.register_event_type(api)
			f = partial(self.handle, api)
			setattr(self, api, f)
			api_f = partial(self.apihandle,api)
			bstr = '/%s' % api
			bstr.encode('utf-8')
			self.osc_server.bind(bstr, api_f)

	def handle(self,api,o,*args):
		print(api, *args)
		
	def apihandle(self, api, *args):
		self.dispatch(api,*args)

	def sendMessage(self,api='', addr=None, port=None, *args):
		try:
			bstr = '/%s' % api
			bstr = bstr.encode('utf-8')
			client = OSCClient(addr, port)
			client.sendMessage(bstr, args)
		except:
			print('sendMessage error:',api, addr,port,args)
	
