
import os
import sys
from kivy.resources import resource_add_path
import signal
import codecs
import json

from appPublic.jsonConfig import getConfig
from appPublic.folderUtils import ProgramPath
from appPublic.uniqueID import getID
from appPublic.rsawrap import RSA

from kivy.factory import Factory
from kivy.metrics import sp,dp,mm
from kivy.core.window import WindowBase, Window
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform
from kivy.metrics import Metrics
from kivy.app import App

import plyer

from .register import *
from .threadcall import HttpClient,Workers
from .utils import *
from .widget_css import register_css
from .version import __version__

if platform == 'android':
	from android.storage import app_storage_path
	from jnius import autoclass
	from .android_rotation import get_rotation

Logger.info(f'KivyBlocks:version={__version__}')
def  signal_handler(signal, frame):
	app = App.get_running_app()
	if app is None:
		return
	app.workers.running = False
	app.stop()
	print('Singal handled .........')

signal.signal(signal.SIGINT, signal_handler)


class BlocksApp(App):
	def get_rotation(self):
		return get_rotation()

	def load_csses(self):
		config = getConfig()
		if not config.css:
			return

		if config.css.css_filename:
			with codecs.open(config.css.css_filename, 'r', 'utf-8') as f:
				d = json.load(f)
				self.buildCsses(d)
		if config.css.css_url:
			hc = HttpClient()
			d = hc.get(self.realurl(config.css.css_url))
			self.buildCsses(d)

	def on_rotate(self,*largs):
		self.current_rotation = Window.rotation
		Logger.info('BlocksApp:on_rotate(), largs=%s', 
						self.current_rotation)

	def buildCsses(self, dic):
		for k,v in dic.items():
			if isinstance(v,dict):
				register_css(k,v)

	def build(self):
		self.platform = platform
		self.is_desktop = platform in ['win', 'linux', 'macosx']
		config = getConfig()
		self.public_headers = {
			"platform":self.platform
		}
		# Window.borderless = True
		print('Window.dpi=', Window.dpi, 'Metrics.dpi=', Metrics.dpi)
		Window.bind(on_request_close=self.on_close)
		Window.bind(on_rotate=self.on_rotate)
		Window.bind(size=self.device_info)
		self.workers = Workers(maxworkers=config.maxworkers or 80)
		self.workers.start()
		self.load_csses()
		self.running = True
		if config.root:
			blocks = Factory.Blocks()
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
			# Environment = autoclass('android.os.Environment')
			# sdpath = Environment.getExternalStorageDirectory()
			# return str(sdpath)
			return str(app_storage_path())
		sdpath = App.get_running_app().user_data_dir
		return str(sdpath)

	def get_profile_name(self):
		fname = os.path.join(self.get_user_data_path(),'.profile.json')
		print('profile_path=', fname)
		return fname

	def default_profile(self):
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
		return d

	def write_profile(self, dic):
		fname = self.get_profile_name()
		with codecs.open(fname,'w','utf-8') as f:
			json.dump(dic,f)

	def write_default_profile(self):
		d = self.default_profile()
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

