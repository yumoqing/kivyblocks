import sys
import math
from traceback import print_exc

from kivy.properties import ObjectProperty, StringProperty
from kivy.app import App
from kivy.utils import platform
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.accordion import Accordion,AccordionItem
from kivy.uix.label import Label
from kivy.event import EventDispatcher
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock

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
from appPublic.jsonConfig import getConfig
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
from .threadcall import HttpClient
from .i18n import I18n
from .utils import CSize

if platform == 'android':
	from .widgetExt.phonebutton import PhoneButton
	from .widgetExt.androidwebview import AWebView

class WrapText(Label):
	def __init__(self, **kw):
		Label.__init__(self, **kw)
		self.bind(width=lambda *x: self.setter('text_size')(self, (self.width, None)),
				texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))

class Box(BGColorBehavior, BoxLayout):
	def __init__(self,color_level=-1,radius=[],**kw):
		BoxLayout.__init__(self, **kw)
		BGColorBehavior.__init__(self, color_level=color_level,
					radius=radius)

	def add_widget(self, w, *args, **kw):
		super().add_widget(w, *args, **kw)
		self.setWidgetTextColor(w)
		
	def setWidgetTextColor(self,w):
		if isinstance(w,Box):
			return

		if isinstance(w,Text):
			if not w.bgcolor:
				w.color = self.fgcolor
			return
		for c in w.children:
			self.setWidgetTextColor(c)

	def selected(self):
		super().selected()
		if self.fgcolor == self.selected_fgcolor:
			return
		for c in self.children:
			self.setWidgetTextColor(c)

	def unselected(self):
		super().unselected()
		if self.fgcolor == self.normal_fgcolor:
			return
		for c in self.children:
			self.setWidgetTextColor(c)

class HBox(Box):
	def __init__(self,**kw):
		kw.update({'orientation':'horizontal'})
		Box.__init__(self, **kw)


class VBox(Box):
	def __init__(self,color_level=-1,radius=[],**kw):
		kw.update({'orientation':'vertical'})
		Box.__init__(self, **kw)

class Text(Label):
	lang=StringProperty('')
	otext = StringProperty('')
	def __init__(self,i18n=False, texttype='text', wrap=False,
					fgcolor=None, **kw):
		
		fontsize={'font_size':CSize(1)}
		offset={
			'text':0,
			'title1':CSize(0.6),
			'title2':CSize(0.5),
			'title3':CSize(0.4),
			'title4':CSize(0.3),
			'title5':CSize(0.2),
			'title6':CSize(0.1),
		}
		fontsize = {'font_size': CSize(1) + offset.get(texttype,0)}
		self._i18n = i18n
		self.i18n = I18n()
		self.bgcolor = fgcolor
		kwargs = kw.copy()
		config = getConfig()
		self.wrap = wrap
		if kwargs.get('font_size') and texttype=='text':
			pass
		else:
			kwargs.update(fontsize)
		super().__init__(**kwargs)
		if self._i18n:
			self.i18n = I18n()
			self.i18n.addI18nWidget(self)
			self.otext = kw.get('text','')
		if self.wrap:
			self.size_hint_y = None
			self.text_size = self.width, None
			self.bind(width=self.set_widget_height)
		if self.bgcolor:
			self.color = self.bgcolor

	def resize(self, *args):
		if not self.size_hint_y:
			ps = [0,0,0,0]
			if hasattr(self.parent,'padding'):
				ps = self.parent.padding

			self.width = self.parent.width - ps[0] - ps[2]
			self.set_widget_height()

	def set_widget_height(self, *args):
		self.text_size = self.width, None
		rows = len(self.text) * (self.font_size * 0.621) / self.width
		rows = math.ceil(rows)
		self.height = rows * self.font_size * 1.5

	def get_wraped_size(self):
		if self.text:
			self._label.refresh()
			return self._label.size
		return (None,None)

	def on_size(self,o,size):
		# super().on_size(o,size)
		if self.wrap:
			font_size = self.font_size
			self.text_size = self.width, None

	def on_otext(self,o,v=None):
		if self._i18n:
			self.text = self.i18n(v)
		else:
			self.text = v
	
	def changeLang(self,lang):
		self.lang = lang

	def on_lang(self,o,lang):
		self.text = self.i18n(self.otext)

class Title1(Text):
	def __init__(self, **kw):
		kw.update({'texttype':'title1','bold':True})
		Text.__init__(self, **kw)

class Title2(Text):
	def __init__(self, **kw):
		kw.update({'texttype':'title2','bold':True})
		Text.__init__(self, **kw)

class Title3(Text):
	def __init__(self, **kw):
		kw.update({'texttype':'title3','bold':True})
		Text.__init__(self, **kw)

class Title4(Text):
	def __init__(self, **kw):
		kw.update({'texttype':'title4','bold':True})
		Text.__init__(self, **kw)

class Title5(Text):
	def __init__(self, **kw):
		kw.update({'texttype':'title5','bold':True})
		Text.__init__(self, **kw)

class Title6(Text):
	def __init__(self, **kw):
		kw.update({'texttype':'title6','bold':True})
		Text.__init__(self, **kw)

class Modal(BGColorBehavior, ModalView):
	def __init__(self, auto_open=False, color_level=-1, radius=[], **kw):
		ModalView.__init__(self, **kw)
		BGColorBehavior.__init__(self, color_level=color_level,
					radius=radius)
		self.auto_open = auto_open

	def add_widget(self,w, *args, **kw):
		super().add_widget(w, *args, **kw)
		if self.auto_open:
			self.open()

class TimedModal(Modal):
	def __init__(self, show_time=5, **kw):
		self.show_time = show_time
		self.time_task = None
		Modal.__init__(self, **kw)

	def open(self, *args, **kw):
		self.time_task = Clock.schedule_once(self.dismiss, self.show_time)
		super().open(*args, **kw)

	def dismiss(self, *args, **kw):
		if self.time_task:
			self.time_task.cancel()
			self.time_task = None
		super().dismiss(*args, **kw)

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
		self.register_event_type('on_success')
		self.register_event_type('on_error')

	def on_success(self,v):
		print('HTTPDataHandler():',self.url,'finished...')
		pass

	def on_error(self,e):
		pass

	def onSuccess(self,o,v):
		print(self.url,'onSuccess() called')
		self.dispatch('on_success',v)

	def onError(self,o,e):
		print(self.url,'onError():v=',e)
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
		hc = HttpClient()
		print('HTTPDataHandler():',self.url,'handling....')
		hc(self.url,method=self.method,
						params=p,
						headers=h,
						files=self.files,
						stream=self.stream,
						callback=self.onSuccess,
						errback=self.onError)


def getDataHandler(url,**kwargs):
	if url.startswith('file://'):
		return FILEDataHandler(url,**kwargs)
	return HTTPDataHandler(url, **kwargs)

def device_type():
	if platform != "android" and platform != "ios":
		return "desktop"
	elif Window.width >= dp(600) and Window.height >= dp(600):
		return "tablet"
	else:
		return "mobile"

