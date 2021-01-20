
import os
import sys
import signal

from appPublic.jsonConfig import getConfig
from appPublic.folderUtils import ProgramPath

from kivy.factory import Factory
from kivy.config import Config
from kivy.metrics import sp,dp,mm
from kivy.core.window import WindowBase, Window
from kivy.clock import Clock
from kivy.logger import Logger

import kivy
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
		blocks = Blocks()
		print(config.root)
		x = blocks.widgetBuild(config.root)
		if x is None:
			alert('buildError,Exit', title='Error')
			self.on_close()
		return x

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

