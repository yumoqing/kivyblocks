try:
	import ujson as json
except:
	import json

import time
from kivy.event import EventDispatcher
from kivy.clock import Clock
from appPublic.udp_comm import UdpComm
from appPublic.dataencoder import DataEncoder


class UdpWidget(EventDispatcher):
	def __init__(self, udp_port=55000, cert_file=None, commands=[],
					**kw):
		super(UdpWidget, self).__init__(**kw)
		self.udp_port = udp_port
		self.commands = commands
		self.block_commands = []
		self.udp_transport = UdpComm(udp_port, self.comm_callback)
		host = self.udp_transport.host
		self.dataencoder = DataEncoder(host, self.get_peer_pubkey)
		self.inner_handlers = {
			'get_pubkey':self.resp_pubkey,
			'set_pubkey':self.set_pubkey
		}
		for cmd in self.commands:
			evt_name = 'on_%s' % cmd
			setattr(self, evt_name, self.event_handler)
			self.register_event_type(evt_name)
		self.get_peer_pubkey()
		Clock.schedule_once(self.get_peer_pubkey_loop, 2)

	def block_command(self, cmd):
		if cmd not in self.command:
			return
		if cmd in self.block_command:
			return
		self.block_commands.append(cmd)

	def unblock_command(self, cmd):
		if cmd not in self.block_command:
			return
		self.block_commands = [ c for c in self.block_command if c!=cmd ]

	def get_peer_pubkey_loop(self, t):
		self.get_peer_pubkey()

	def get_peer_pubkey(self, peer_id=None, timeout=1):
		d = {
			'c':'get_pubkey',
			'd':{
				'pubkey':self.dataencoder.my_text_publickey()
			}
		}
		b = json.dumps(d).encode('utf-8')
		self.udp_transport.broadcast(b)
		if peer_id is None:
			return
		t = t1 = time.time()
		t1 += timeout
		while t1 > t:
			time.sleep(0.1)
			t = time.time()
			if self.dataencoder.exist_peer_publickeys(peer_id):
				return self.dataencder.public_keys[peer_id]
		raise Exception('timeout')

	def comm_callback(self, data, addr):
		print('received:', data, 'addr=', addr)
		d = None
		if data[:18] == b'0x00' * 18:
			data = data[18:]
			try:
				d = json.loads(data.decode('utf-8'))
			except Exception as e:
				print(e, addr, data)
				print_exc()
				return
		else:
			d = self.dataencoder.unpack(addr[0], data)
		if d is None:
			return
		if not isinstance(d, dict):
			return
		print('received: data=', d)
		cmd = d['c']
		f = self.inner_handler(cmd)
		if f:
			f(d, addr)
			return
		if cmd in self.block_commands:
			return
		evt_name = 'on_%s' % cmd
		evt_data = {
			'data': d,
			'addr': addr
		}
		self.dispatch(evt_name, evt_data)

	def event_handler(self, o, d):
		Logger.info('UdpWidget: received data=%s', d)

	def set_pubkey(self, data, addr):
		pk = data['d']['pubkey']
		id = addr[0]
		self.dataencoder.set_peer_text_pubkey(id, pk)

	def resp_pubkey(self, data, addr):
		set_pubkey(data, addr)
		data = {
			'c':'set_pubkey',
			'd':{
				'pubkey':self.dataencoder.my_text_publickey()
			}
		}
		self.send(addr[0], data)

	def broadcast(self, data):
		for peer in self.dataencoder.public_keys.keys():
			self.send(peer, data)

	def send(self, peer_id, data):
		d = self.dataencoder.pack(peer_id, data)
		addr = (peer_id, self.udp_port)
		print('send():', peer_id, data)
		self.udp_transport.send(d, addr)

	def stop(self):
		self.udp_transport.stop()