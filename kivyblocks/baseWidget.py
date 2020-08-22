import sys
from traceback import print_exc

from kivy import platform
from kivy.app import App
from kivy.utils import platform
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.accordion import Accordion,AccordionItem
from kivy.uix.label import Label
from kivy.event import EventDispatcher
from kivy.metrics import dp
from kivy.core.window import Window

from kivy.uix.actionbar import ActionBar,ActionView,ActionPrevious,ActionItem,ActionButton
from kivy.uix.actionbar import ActionToggleButton, ActionCheck,ActionSeparator,ActionGroup

from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout

from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.tabbedpanel import TabbedPanel,TabbedPanelContent,TabbedPanelHeader,TabbedPanelItem
from kivy.uix.treeview import TreeView
from kivy.uix.image import AsyncImage,Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.splitter import Splitter
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider

from kivy.uix.screenmanager import ScreenManager
from kivy.uix.sandbox import Sandbox
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.filechooser import FileChooser
from kivy.uix.effectwidget import EffectWidget
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.carousel import Carousel
from kivy.uix.bubble import Bubble
from kivy.uix.codeinput import CodeInput
from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty
from kivycalendar import DatePicker
from kivy.factory import Factory

from appPublic.dictObject import DictObject
from appPublic.folderUtils import listFile

from .widgetExt.scrollwidget import ScrollWidget
from .widgetExt.binstateimage import BinStateImage
from .widgetExt.jsoncodeinput import JsonCodeInput
from .widgetExt.inputext import FloatInput,IntegerInput, \
		StrInput,SelectInput, BoolInput, AmountInput
from .widgetExt.messager import Messager
from .charts.bar import Bar
from .bgcolorbehavior import BGColorBehavior
from .utils import NeedLogin, InsufficientPrivilege, HTTPError
from .login import LoginForm
from .tab import TabsPanel
from .qrdata import QRCodeWidget

if platform == 'android':
	from .widgetExt.phonebutton import PhoneButton
	from .widgetExt.androidwebview import AWebView

class WrapText(Label):
	def __init__(self, **kw):
		Label.__init__(self, **kw)
		self.bind(width=lambda *x: self.setter('text_size')(self, (self.width, None)),
				texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))


class Text(Label):
	pass

class PressableImage(ButtonBehavior,AsyncImage):
	def on_press(self):
		pass

class PressableLabel(ButtonBehavior, Text):
	def on_press(self):
		pass

class FILEDataHandler(EventDispatcher):
	def __init__(self, url, suffixs=[],params={}):
		self.url = url
		self.subfixes=subfixes
		self.params = params
		self.page_rows = self.params.get('page_rows',60)
		self.page = self.params.get('page',1)
		if not url.startswith('file://'):
			raise Exception('%s is not a file url' % url)
		self.files = [i for i in listFile(url[7:],suffixs=suffixs, \
					rescursive=self.params.get('rescursive',False)) ]
		self.total_files = len(self.files)
		x = 0 if self.total_files % self.page_rows == 0 else 1
		self.total_pages = self.total_files / self.page_rows + x
		self.register_event_type('on_success')
		self.register_event_type('on_error')

	def on_success(self,d):
		return

	def on_error(self,e):
		return

	def handle(self,params={}):
		d = {}
		d['total'] = self.total_files
		d['rows'] = []
		p = self.params.copy()
		p.update(params)
		page = p.get('page')
		for i in range(self.page_rows):
			try:
				r = self.files[page * self.page_rows + i]
				d['rows'].append({'filename':r,
					'id':r,
					'url':r
				})
			except:
				break
		self.dispatch('on_success',d)

class HTTPDataHandler(EventDispatcher):
	def __init__(self, url,method='GET',params={},
				headers={},
				files={},
				stream=False
				):
		EventDispatcher.__init__(self)
		self.url = url
		self.method = method
		self.params = params
		self.headers = headers
		self.files=files
		self.stream=stream
		self.hc = App.get_running_app().hc
		self.register_event_type('on_success')
		self.register_event_type('on_error')

	def on_success(self,v):
		pass

	def on_error(self,e):
		pass

	def onSuccess(self,o,v):
		# print(__file__,'onSuccess():v=',v)
		self.dispatch('on_success',v)

	def onError(self,o,e):
		if isinstance(e,NeedLogin):
			lf = LoginForm()
			lf.bind(on_setupuser=self.redo)
			lf.open()
			return
		self.dispatch('on_error',e)
		print_exc()
		print('[****][*********] onError Called',e)

	def redo(self,o,v=None):
		self.handle()

	def handle(self,params={},headers={}):
		p = self.params
		p.update(params)
		h = self.headers
		h.update(headers)
		self.hc(self.url,method=self.method,
						params=p,
						headers=h,
						files=self.files,
						stream=self.stream,
						callback=self.onSuccess,
						errback=self.onError)


def getDataHandler(url,**kwargs):
	if url.startswith('file://'):
		return FILEDataHandler(url,**kwargs)
	return HTTPDataHandler(url, **kwaegs)

def device_type():
	if platform != "android" and platform != "ios":
		return "desktop"
	elif Window.width >= dp(600) and Window.height >= dp(600):
		return "tablet"
	else:
		return "mobile"

