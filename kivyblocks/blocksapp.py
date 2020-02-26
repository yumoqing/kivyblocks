
import os
import sys
import signal

from appPublic.jsonConfig import getConfig
from appPublic.folderUtils import ProgramPath

from kivy.config import Config
from kivy.metrics import sp,dp,mm
from kivy.core.window import WindowBase, Window
from kivy.clock import Clock

import kivy
from kivy.resources import resource_add_path
resource_add_path(os.path.join(os.path.dirname(__file__),'./ttf'))
Config.set('kivy', 'default_font', [
	'msgothic',
	'DroidSansFallback.ttf'])

from kivy.app import App
# from .baseWidget import baseWidgets
# from .widgetExt import Messager
# from .externalwidgetmanager import ExternalWidgetManager
from .threadcall import HttpClient,Workers
# from .derivedWidget import buildWidget, loadUserDefinedWidget
from .utils import *
from .pagescontainer import PageContainer
from .widgetExt.messager import Messager
from .blocks import Blocks
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


class BlocksApp(App):
	def build(self):
		config = getConfig()
		self.config = config
		self.serverinfo = ServerInfo()
		self.title = 'Test Title'
		self.blocks = Blocks()
		self.workers = Workers(maxworkers=config.maxworkers or 80)
		Window.bind(on_request_close=self.on_close)
		self.workers.start()
		self.hc = HttpClient()
		WindowBase.softinput_mode='below_target'
		x = PageContainer()
		Clock.schedule_once(self.build1)
		print('build() called......')
		return x

	def getAuthHeader(self):
		if not hasattr(self,'serverinfo'):
			print('app serverinfo not found')
			return {}
		serverinfo = self.serverinfo
		if hasattr(serverinfo,'authCode'):
			return {
				'authorization':serverinfo.authCode
			}
		print('serverinfo authCode not found')
		return {}

	def on_start(self):
		print('on_start() called ...')

	def build1(self,t):
		x = None
		x = self.blocks.widgetBuild(self.config.root)
		if x is None:
			alert(str(self.config.root)+': cannt build widget')
			return
		self.root.add_widget(x)
		return
			
	def on_close(self,o,v=None):
		"""
		catch the "x" button's event of window
		"""
		self.workers.running = False
		
	def on_pause(self,o,v=None):
		"""
		to avoid app start from beginening when user exit and reenter this app
		"""
		return True

	def __del__(self):
		self.workers.running = False
