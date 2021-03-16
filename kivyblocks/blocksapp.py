
import os
import sys
import signal
import codecs
import json

from appPublic.jsonConfig import getConfig
from appPublic.folderUtils import ProgramPath
from appPublic.uniqueID import getID

from kivy.factory import Factory
from kivy.config import Config
from kivy.metrics import sp,dp,mm
from kivy.core.window import WindowBase, Window
from kivy.clock import Clock
from kivy.logger import Logger

import kivy
import plyer

from kivy.resources import resource_add_path
resource_add_path(os.path.join(os.path.dirname(__file__),'./ttf'))
Config.set('kivy', 'default_font', [
	'msgothic',
	'DroidSansFallback.ttf'])

from kivy.app import App
from kivy.utils import platform
from .threadcall import HttpClient,Workers
from .utils import *
from .pagescontainer import PageContainer
from .blocks import Blocks
from .theming import ThemeManager
from appPublic.rsa import RSA
if platform == 'android':
	from jnius import autoclass

class ServerInfo:
	def __init__(self):
		self.rsaEngine = RSA()
		self.publickey = None
		self.authCode = None
	
	def getServerPK(self):
		config = getConfig()
		url = '%s%s' % (config.uihome, config.publickey_url)
		hc = App.get_running_app().hc
		d = hc.get(url)
		self.publickey = self.rsaEngine. publickeyFromText(d)
	
	def encode(self,uinfo):
		if self.publickey is None:
			self.getServerPK()

		if uinfo['authmethod'] == 'password':
			authinfo = '%s::%s::%s' % (uinfo['authmethod'], uinfo['userid'], uinfo['passwd'])
			x = self.rsaEngine.encode(self.publickey, authinfo)
			self.authCode = x
			return x
		return None


def  signal_handler(signal, frame):
	app = App.get_running_app()
	app.workers.running = False
	app.stop()
	print('Singal handled .........')

signal.signal(signal.SIGINT, signal_handler)

def getAuthHeader():
	app = App.get_running_app()
	if not hasattr(app,'serverinfo'):
		print('app serverinfo not found')
		return {}
	serverinfo = app.serverinfo
	if hasattr(serverinfo,'authCode'):
		return {
			'authorization':serverinfo.authCode
		}
	print('serverinfo authCode not found')
	return {}

class BlocksApp(App):
	def build(self):
		config = getConfig()
		self.public_headers = {}
		Window.bind(on_request_close=self.on_close)
		Window.bind(size=self.device_info)
		self.workers = Workers(maxworkers=config.maxworkers or 80)
		self.workers.start()
		self.running = True
		if config.root:
			blocks = Blocks()
			x = blocks.widgetBuild(config.root)
			if x is None:
				alert('buildError,Exit', title='Error')
				return Label(text='error')
			return x
		return None

	def realurl(self, url):
		if url.startswith('https://') or url.startswith('http://'):
			return url
		config = getConfig()
		return '%s%s' % (config.uihome, url)

	def get_user_data_path(self):
		if platform == 'android':
			Environment = autoclass('android.os.Environment')
			sdpath = Environment.getExternalStorageDirectory()
			return str(sdpath)
		sdpath = App.get_running_app().user_data_dir
		return str(sdpath)

	def get_profile_name(self):
		fname = os.path.join(self.user_data_dir,'.profile.json')
		print('profile_path=', fname)
		return fname

	def write_profile(self, dic):
		fname = self.get_profile_name()
		with codecs.open(fname,'w','utf-8') as f:
			json.dump(dic,f)

	def write_default_profile(self):
		device_id = getID()
		try:
			device_id = plyer.uniqueid.id
		except:
			pass
		if isinstance(device_id,bytes):
			device_id = device_id.decode('utf-8')

		d = {
			'device_id': device_id
		}
		self.write_profile(d)

	def read_profile(self):
		fname = self.get_profile_name()
		if not os.path.isfile(fname):
			self.write_default_profile()
		with codecs.open(fname, 'r', 'utf-8') as f:
			d = json.load(f)
			return d

	def device_info(self, *args):
		d = {
				"platform":platform,
				"width":Window.width,
				"height":Window.height
			}
		device = {
			"device_info":";".join([f'{k}={v}' for k,v in d.items()])
		}
		self.public_headers.update(device)

	def on_close(self, *args):
		self.workers.running = False
		return False

