
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

def  signal_handler(signal, frame):
	app = App.get_running_app()
	app.workers.running = False
	app.stop()
	print('Singal handled .........')

signal.signal(signal.SIGINT, signal_handler)

class BlocksApp(App):
	def build(self):
		x = PageContainer()
		self.title = 'Test Title'
		self.blocks = Blocks()
		config = getConfig()
		self.config = config
		self.workers = Workers(maxworkers=config.maxworkers or 80)
		Window.bind(on_request_close=self.on_close)
		self.workers.start()
		self.hc = HttpClient()
		WindowBase.softinput_mode='below_target'
		Clock.schedule_once(self.build1)
		return x

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
