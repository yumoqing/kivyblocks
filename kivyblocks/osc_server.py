from functools import partial
from kivy.event import EventDispatcher
from kivy.clock import Clock
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient

class OSCServer(EventDispatcher):
	def __init__(self,addr='0.0.0.0', 
					port=60405,
					apis=[]):
		self.port = port
		self.addr = addr
		self.clients = []
		self.osc_server = OSCThreadServer()
		self.osc_server.listen(self.addr,port=self.port,default=True)
		EventDispatcher.__init__(self)
		apis.append('broadcast')
		for api in apis:
			event_name = 'on_%s' % api
			f = partial(self.handle, api)
			setattr(self, event_name, f)
			self.register_event_type(event_name)
			api_f = partial(self.apihandle,api)
			bstr = '/%s' % api
			bstr.encode('utf-8')
			self.osc_server.bind(bstr, api_f)

	def info(self):
		return {
			"address":self.osc_server.getaddress()
		}

	def __del__(self):
		self.osc_server.stop_all()
		self.osc_server.terminate_server()
		self.osc_server.join_server()

	def handle(self,api,o,*args):
		print(api, *args)
		
	def apihandle(self, api, *args):
		data = json.loads(args[0])
		sock, ip_address, response_port = self.osc_server.get_sender()
		self.dispatch('on_%s' % api, api, data)
		if api == 'broadcast':
			return
		if not address in self.clients:
			self.clients.append([ip_address, response_port])

	def send_message(self,api, data, addr, port):
		data = json.dumps(data)
		bstr = '/%s' % api
		bstr = bstr.encode('utf-8')
		self.osc_server.send_message(b'/broadcast', [data], addr, port)
	
	def broadcast(self, data):
		for address in self.clients:
			self.osc_server.send_message('broadcast', data, *address)
		
