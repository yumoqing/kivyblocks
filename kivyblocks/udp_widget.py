try:
	import ujson as json
except:
	import json

import time
import zlib
from kivy.logger import Logger
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
			setattr(self, evt_name, self.my_event_handler)
			self.register_event_type(evt_name)
			# print('udp_widget.py:register', evt_name, self.my_event_handler)

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
		# print('get_peer_pubkey(), called..')
		d = {
			'c':'get_pubkey',
			'd':{
				'pubkey':self.dataencoder.my_text_publickey()
			}
		}
		bd = self.dataencoder.pack('none', d, uncrypt=True)
		self.udp_transport.broadcast(bd)
		if peer_id is None:
			# print('get_peer_pubkey():return')
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
		# print('comm_callback():', data, 'addr=', addr)
		d = self.dataencoder.unpack(addr[0], data)
		if d is None:
			# print('comm_callback(): d is None')
			return
		if not isinstance(d, dict):
			# print('comm_callback(): d is not a dict data')
			return
		# print('received: data=', d)
		cmd = d['c']
		f = self.inner_handlers.get(cmd)
		if f:
			f(d, addr)
			# print('comm_callback():inner callback called(),', cmd)
			return
		if cmd in self.block_commands:
			# print('comm_callback():', cmd, 'is blocked')
			return
		evt_name = 'on_%s' % cmd
		evt_data = {
			'd': d,
			'addr': addr
		}
		# print('udp_widget.py dispatch', evt_name, evt_data)
		self.dispatch(evt_name, evt_data)

	def my_event_handler(self, *args):
		pass

	def set_pubkey(self, data, addr):
		pk = data['d']['pubkey']
		id = addr[0]
		# print('set_pubkey(): ', id, pk)
		self.dataencoder.set_peer_text_pubkey(id, pk)

	def resp_pubkey(self, data, addr):
		self.set_pubkey(data, addr)
		# print('resp_pubkey():', addr[0])
		data = {
			'c':'set_pubkey',
			'd':{
				'pubkey':self.dataencoder.my_text_publickey()
			}
		}
		self.send(addr[0], data, uncrypt=True)

	def broadcast(self, data):
		for peer in self.dataencoder.public_keys.keys():
			self.send(peer, data)

	def send(self, peer_id, data, uncrypt=False):
		# print('send():', peer_id, data)
		d = self.dataencoder.pack(peer_id, data, uncrypt=uncrypt)
		addr = (peer_id, self.udp_port)
		self.udp_transport.send(d, addr)

	def stop(self):
		self.udp_transport.stop()
