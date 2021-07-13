import time
from kivy.event import EventDispatcher
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
		host = self.upd_transport.host
		self.dataencoder = DataEncoder(host, self.get_peer_pubkey)
		self.inner_handlers = {
			'get_pubkey':self.resp_pubkey
		}
		for cmd in self.commands:
			evt_name = 'on_%s' % cmd
			setattr(self, evt_name, self.event_handler)
			self.register_event_type(evt_name)

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

	def get_peer_pubkey(self, peer_id, timeout=2):
		d = {
			'c':'get_pubkey',
			'd':{
				'pubkey':self.dataencoder.my_text_publickey()
			}
		}
		b = json.dumps(d).encode('utf-8')
		self.udp_tranport.broadcast(b)
		t1 = time.time()
		t = t1
		t1 += timeout
		while t1 > t:
			time.sleep(0.1)
			t = time.time()
			if self.dataencoder.exist_peer_publickeys():
				return
		raise Exception('timeout')

	def comm_callback(self, data, addr):
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

	def resp_pubkey(self, data, addr):
		pk = data['d']['pubkey']
		id = addr[0]
		self.dataencoder.set_peer_text_pubkey(id, pk)

	def send(self, peer_id, data):
		d = self.dataencoder.pack(peer_id, data)
		addr = (peer_id, self.udp_port)
		self.udp_transport.send(d, addr)

