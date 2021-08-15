
from functools import partial
import json
from pythonosc import dispatcher, osc_server, udp_client
from appPublic.sockPackage import get_free_local_addr
from appPublic.background import Background
from kivy.event import EventDispatcher


class PlayerOSCServer(EventDispatcher):
	def __init__(self,playerid, cmds=[]):
		EventDispatcher.__init__(self)
		self.playerid = playerid
		dispatch = dispatcher.Dispatcher()
		self.ip,self.port = get_free_local_addr()
		self.server = osc_server.BlockingOSCUDPServer( (self.ip, self.port), dispatch)
		self.osc_dispatch = dispatch
		self.commands = cmds
		for cmd in self.commands:
			self.map(cmd)
		
	def on_osc_event(self, cmd, *args):
		print('PlayerOSCServer():on_osc_event():cmd=', cmd, 'args=',args)

	def action_event(self,cmd,*args):
		self.dispatch('on_%s' % cmd, cmd, *args)

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
		event_name = 'on_%s' % cmd
		on_f = partial(self.on_osc_event, cmd)
		setattr(self,event_name, on_f)
		self.register_event_type(event_name)
		self.osc_dispatch.map( '/%s' % cmd,partial(self.action_event, cmd))
			
	def stop(self):
		self.server.shutdown()
		self.server.server_close()
		self.thread.join(5)

	def send_message(self, api, data, ip, port):
		client = udp_client.SimpleUDPClient(ip, port)  # Create client
		t = json.dumps(data)
		client.send_message('/%s' % api, t)
		

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

