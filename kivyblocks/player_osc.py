
import json
from pythonosc import dispatcher, osc_server, udp_client
from appPublic.sockPackage import get_free_local_addr
from appPublic.background import Background
from kivy.event import EventDispatcher


class PlayerOSCServer(EventDispatcher):
	def __init__(self,playerid):
		EventDispatcher.__init__(self)
		self.playerid = playerid
		dispatch = dispatcher.Dispatcher()
		self.ip,self.port = get_free_local_addr()
		# self.server = osc_server.ThreadingOSCUDPServer( (self.ip, self.port), dispatch)
		self.server = osc_server.BlockingOSCUDPServer( (self.ip, self.port), dispatch)
		self.osc_dispatch = dispatch
		self.commands = []
		self.register_event_type('on_osc_event')
		
	def on_osc_event(self,*args):
		print('PlayerOSCServer():on_osc_event():args=',args)

	def action_event(self,*args):
		self.dispatch('on_osc_event',*args)

	def start(self):
		self.thread = Background(self.server.serve_forever)
		self.thread.daemon_threads = True
		self.thread.start()

	def info(self):
		return {
			"playerid":self.playerid,
			"ip":self.ip,
			"port":self.port,
			"commands": self.commands
		}

	def map(self,cmd):
		self.commands.append(cmd)
		self.osc_dispatch.map(cmd,self.action_event)
			
	def stop(self):
		self.server.shutdown()
		self.server.server_close()
		self.thread.join(5)

class PlayerOSCClient:
	def __init__(self, ip,port):
		self.client = udp_client.SimpleUDPClient(ip, port)  # Create client

	def play(self, mrec):
		t = json.dumps(mrec)
		self.client.send_message("/play", t)

	def mute(self):
		self.client.send_message('/mute')

	def menu(self):
		self.client.send_message('/menu')

	def pause(self):
		self.client.send_message('/pause')

	def up(self):
		self.client.send_message('/up')

