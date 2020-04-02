
import os
import sys
import signal

from appPublic.jsonConfig import getConfig
from appPublic.folderUtils import ProgramPath

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

def on_close(*args,**kwargs):
	"""
	catch the "x" button's event of window
	"""
	Logger.info('kivyblocks: on_close(), args=%s, kwargs=%s',str(args),str(kwargs))
	app = App.get_running_app()
	if len(app.root.pageWidgets) <= 1:
		app.workers.running = False
		Logger.info('kivyblocks: on_close(), return False')
		return False
	app.root.previous()
	Logger.info('kivyblocks: on_close(), return True')
	return True

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

def closeWorkers():
	app = App.get_running_app()
	app.workers.running = False

def appBlocksHack(app):
		config = getConfig()
		# app.on_close = on_close
		app.getAuthHeader = getAuthHeader
		app.__del__ = closeWorkers
		Window.bind(on_request_close=app.on_close)
		app.serverinfo = ServerInfo()
		app.title = 'Test Title'
		app.blocks = Blocks()
		app.workers = Workers(maxworkers=config.maxworkers or 80)
		app.workers.start()
		app.hc = HttpClient()
		WindowBase.softinput_mode='below_target'
	
class BlocksApp(App):
	def build(self):
		root = PageContainer()
		x = None
		config = getConfig()
		x = self.blocks.widgetBuild(config.root)
		if x is None:
			alert(str(self.config.root)+': cannt build widget')
			return root
		root.add_widget(x)
		return root
			
