import sys
from traceback import print_exc
from kivy.app import App
from kivy.utils import platform
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.accordion import Accordion,AccordionItem
from kivy.uix.label import Label
from kivy.event import EventDispatcher

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
from kivy.uix.camera import Camera
from kivy.uix.bubble import Bubble
from kivy.uix.codeinput import CodeInput
from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty
from kivycalendar import DatePicker
from kivy.factory import Factory

from appPublic.dictObject import DictObject

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
if platform == 'android':
	from .widgetExt.phonebutton import PhoneButton
	from .widgetExt.androidwebview import AWebView

class Text(BGColorBehavior, Label):
	def __init__(self,bgcolor=[],fgcolor=[],color_level=-1,**kw):
		self.options = DictObject(**kw)
		kwargs = kw.copy()
		Label.__init__(self,**kwargs)
		BGColorBehavior.__init__(self,bgcolor=bgcolor,
					fgcolor=fgcolor,
					color_level=color_level)

class PressableImage(ButtonBehavior,AsyncImage):
	def on_press(self):
		pass

class PressableLabel(ButtonBehavior, Text):
	def on_press(self):
		pass

class HTTPDataHandler(EventDispatcher):
	def __init__(self, url,method='GET',params={},
				headers={},
				files={}
				):
		EventDispatcher.__init__(self)
		self.url = url
		self.method = method
		self.params = params
		self.headers = headers
		self.files=files
		self.hc = App.get_running_app().hc
		self.register_event_type('on_success')
		self.register_event_type('on_error')

	def on_success(self,v):
		pass

	def on_error(self,e):
		pass

	def onSuccess(self,o,v):
		print(__file__,'onSuccess():v=',v)
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
						callback=self.onSuccess,
						errback=self.onError)

