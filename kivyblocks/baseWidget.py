import sys
import math
from traceback import print_exc

from kivy.properties import ObjectProperty, StringProperty, \
			NumericProperty, BooleanProperty, OptionProperty
from kivy.properties import DictProperty
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
from kivy.properties import ListProperty, DictProperty
from kivy.factory import Factory

from appPublic.dictObject import DictObject
from appPublic.jsonConfig import getConfig
from appPublic.folderUtils import listFile

from .widgetExt.scrollwidget import ScrollWidget
from .widgetExt.binstateimage import BinStateImage
from .widgetExt.jsoncodeinput import JsonCodeInput
from .widgetExt.inputext import FloatInput,IntegerInput, \
		StrInput,SelectInput, BoolInput, Password
from .widgetExt.messager import Messager
from .bgcolorbehavior import BGColorBehavior
from .utils import NeedLogin, InsufficientPrivilege, HTTPError, blockImage
from .login import LoginForm
from .tab import TabsPanel
from .threadcall import HttpClient
from .i18n import I18n
from .widget_css import WidgetCSS
from .ready import WidgetReady
from .utils import CSize, SUPER
from .swipebehavior import SwipeBehavior
from .widgetExt.inputext import MyDropDown

if platform == 'android':
	from .widgetExt.phonebutton import PhoneButton
	from .widgetExt.androidwebview import AWebView

class WrapText(Label):
	def __init__(self, **kw):
		Label.__init__(self, **kw)
		self.bind(width=lambda *x: self.setter('text_size')(self, (self.width, None)),
				texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))

class StackBox(WidgetCSS, WidgetReady, StackLayout):
	def __init__(self, **kw):
		super().__init__(**kw)

class AnchorBox(WidgetCSS, WidgetReady, AnchorLayout):
	def __init__(self, **kw):
		super().__init__(**kw)

def FloatBox(WidgetCSS, WidgetReady, FloatLayout):
	def __init__(self, **kw):
		super().__init__(**kw)

def RelativeBox(WidgetCSS, WidgetReady, RelativeLayout):
	def __init__(self, **kw):
		super().__init__(**kw)

def GridBox(WidgetCSS, WidgetReady, GridLayout):
	def __init__(self, **kw):
		super().__init__(**kw)

def PageBox(WidgetCSS, WidgetReady, PageLayout):
	def __init__(self, **kw):
		super().__init__(**kw)

def ScatterBox(WidgetCSS, WidgetReady, ScatterLayout):
	def __init__(self, **kw):
		super().__init__(**kw)

class Box(WidgetCSS, WidgetReady, BoxLayout):
	def __init__(self, **kw):
		try:
			SUPER(Box, self, kw)
		except Exception as e:
			print('Box(',kw,') Error')
			raise e

class HBox(Box):
	def __init__(self,**kw):
		kw.update({'orientation':'horizontal'})
		Box.__init__(self, **kw)


class VBox(Box):
	def __init__(self,**kw):
		kw.update({'orientation':'vertical'})
		Box.__init__(self, **kw)

class SwipeBox(SwipeBehavior, Box):
	def __init__(self, **kw):
		SUPER(SwipeBox, self, kw)


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
		if not kwargs.get('text'):
			kwargs['text'] = kwargs.get('otext','')
		
		SUPER(Text, self, kwargs)
		if self._i18n:
			self.i18n.addI18nWidget(self)
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
			if self.width > 0:
				self.set_widget_height()

	def set_widget_height(self, *args):
		if self.width == 0:
			return
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
			self.text = self.i18n(self.otext)
		else:
			self.text = self.otext
	
	def changeLang(self,lang):
		self.lang = lang

	def on_lang(self,o,lang):
		if self._i18n and self.otext:
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

class Modal(VBox):
	content = DictProperty(None)
	auto_open = BooleanProperty(True)
	auto_dismiss = BooleanProperty(True)
	target = StringProperty(None)
	position = OptionProperty('cc',options=['tl', 'tc', 'tr',
											'cl', 'cc', 'cr',
											'bl', 'bc', 'br'])
	def __init__(self, **kw):
		self._target = None
		super(Modal, self).__init__(**kw)
		self.set_size_position()
		self._target.bind(size=self.set_size_position)
		self.register_event_type('on_open')
		self.register_event_type('on_pre_open')
		self.register_event_type('on_pre_dismiss')
		self.register_event_type('on_dismiss')
		if self.content:
			blocks = Factory.Blocks()
			self.content_w = blocks.widgetBuild(self.content)
			if self.content_w:
				self.add_widget(self.content_w)
			else:
				print(content,':cannot build widget')

	def on_touch_down(self, touch):
		if 	not self.collide_point(touch.x, touch.y):
			if self.auto_dismiss:
				self.dispatch('on_pre_dismiss')
				self.dismiss()
				return True
				
		return super().on_touch_down(touch)

	def on_target(self):
		w = Window
		if self.target is not None:
			w = Factory.Blocks.getWidgetById(self.target)
		if w is None:
			w = Window
		if w != self._target:
			self._target = w
		
	def set_target(self):
		if self._target is None:
			if self.target is None:
				w = Window
			else:
				w = Factory.Blocks.getWidgetById(self.target)
				if w is None:
					w = Window
			self._target = w

	def set_size_position(self, *args):
		self.set_target()
		if self.size_hint_x:
			self.width = self.size_hint_x * self._target.width
		if self.size_hint_y:
			self.height = self.size_hint_y * self._target.height
		print(self.width, self.height, 
					self.size_hint_x, self.size_hint_y,
					self._target.size
					)
		self.set_modal_position()

	def set_modal_position(self):
		self.set_target()
		xn = self.position[1]
		yn = self.position[0]
		x, y = 0, 0
		if xn == 'c':
			x = (self._target.width - self.width) / 2
		elif xn == 'r':
			x = self._target.width - self.width
		if x < 0:
			x = 0
		if yn == 'c':
			y = (self._target.height - self.height) / 2
		elif yn == 't':
			y = self._target.height - self.height
		if y < 0:
			y = 0
		if self._target == Window:
			self.pos = x, y
		else:
			self.pos = self._target.pos[0] + x, self._target.pos[1] + y

	def open(self):
		if self.parent:
			self.parent.remove_widget(self)
		self.dispatch('on_pre_open')
		Window.add_widget(self)
		self.dispatch('on_open')
		if self._target != Window:
			self._target.disabled = True

	def dismiss(self, *args):
		self.dispatch('on_pre_dismiss')
		self.dispatch('on_dismiss')
		Window.remove_widget(self)
		if self._target != Window:
			self._target.enabled = False
			
	def on_open(self, *args):
		pass

	def on_dismiss(self, *args):
		pass
			
	def on_pre_open(self, *args):
		pass

	def on_pre_dismiss(self, *args):
		pass

	def add_widget(self, w, *args, **kw):
		super().add_widget(w, *args, **kw)
		if self.auto_open:
			self.open()

class TimedModal(Modal):
	show_time = NumericProperty(0)
	def __init__(self, **kw):
		self.time_task = None
		SUPER(TimedModal, self, kw)

	def open(self, *args, **kw):
		if self.time_task is not None:
			self.time_task.cancel()
			self.time_task = None
		if self.show_time > 0:
			self.time_task = \
				Clock.schedule_once(self.dismiss, self.show_time)
		super().open(*args, **kw)

	def dismiss(self, *args, **kw):
		if self.time_task:
			self.time_task.cancel()
			self.time_task = None
		super().dismiss()

class Running(AsyncImage):
	def __init__(self, widget, **kw):
		super().__init__(**kw)
		self.host_widget = widget
		self.source = blockImage('running.gif')
		self.host_widget.bind(size=self.set_size)
		self.set_size()
		self.open()

	def open(self):
		if self.parent:
			self.parent.remove_widget(self)
		Window.add_widget(self)
		self.host_widget.disabled = True

	def dismiss(self):
		if self.parent:
			self.parent.remove_widget(self)
		self.host_widget.disabled = False

	def set_size(self, *args):
		self.size_hint = (None, None)
		self.width = CSize(2)
		self.height = CSize(2)
		self.center = self.host_widget.center
		
class PressableImage(ButtonBehavior,AsyncImage):
	def on_press(self):
		pass

class PressableLabel(ButtonBehavior, Text):
	def on_press(self):
		pass

class PressableText(ButtonBehavior, Text):
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

	def on_success(self,*args):
		return

	def on_error(self, *args):
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
	def __init__(self, url='',method='GET',params={},
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

	def on_success(self,*args):
		print('HTTPDataHandler():',self.url,'finished...')
		pass

	def on_error(self,*args):
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


class HTTPSeriesData(HTTPDataHandler):
	def __init__(self, rows=20, page=1, **kw):
		super(HTTPSeriesData, self).__init__(**kw)
		self.rows = rows
		self.page = page
		self.maxpage = 999999

	def load(self, page=1, **params):
		self.params.update(params)
		if page == 1:
			self.maxpage = 999999
		self.page = page
		params = {
			'page': self.page,
			'rows': self.rows
		}
		self.handle(params=params)

	def loadPrevious(self, **params):
		self.params.update(params)
		if self.page > 0:
			self.load(page=self.page - 1)

	def loadNext(self, **params):
		self.params.update(params)
		if self.page < self.maxpage:
			self.load(page=self.page + 1)

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

class ExAccordion(WidgetCSS, WidgetReady, Accordion):
	"""
	{
		"widgettype":"Accordion",
		"options":{
			"csscls",
			"items":[{
				"title":"titl1",
				"active":false,
				"widget":{
				}
			}
			]
		}
	}
	"""
	items = ListProperty(None)
	def __init__(self, **kw):
		print('ExAccordion() init...')
		super().__init__(**kw)
		self.width = self.height = 800
		# Clock.schedule_once(self._build_children, 0.1)
		self._build_children()

	def _build_children(self, *args):
		for i in self.items:
			bk = Factory.Blocks()
			w = bk.widgetBuild(i['widget'])
			if w is None:
				continue
			tw = AccordionItem()
			if isinstance(i['title'], str):
				tw.title = i['title']
			else:
				tw.title = bk.widgetBuild(i['title'])
			tw.add_widget(w)
			if i.get('active'):
				self.collapse = False
			else:
				self.collapse = True
			self.add_widget(tw)

class Slider(Carousel):
	"""
	{
		"widgettype":"Slider",
		"options":{
			"direction":"right",
			"loop":true,
			"items":[
				{
					"widgettype":....
				}
			]
		}
	}
	"""
	items = ListProperty(None)
	def __init__(self, **kw):
		print('Carousel pro=', dir(Carousel))
		super().__init__(**kw)
		bk = Factory.Blocks()
		for desc in self.items:
			w = bk.widgetBuild(desc)
			self.add_widget(w)

class I18nWidget(PressableText):
	lang = StringProperty(None)
	def __init__(self, **kw):
		super().__init__(**kw)
		i18n = I18n()
		self.lang = i18n.lang

	def on_lang(self, *args):
		self.otext = self.lang

	def on_press(self, *args):
		i18n = I18n()
		langs = i18n.get_languages()
		data = [ {'lang':l} for l in langs ]
		mdd = MyDropDown(textField='lang', valueField='lang',
						value=self.lang,
						data=data)
		mdd.bind(on_select=self.selected_lang)
		mdd.showme(self)

	def selected_lang(self, o, v):
		lang = v[0]
		self.lang = lang
		i18n = I18n()
		i18n.changeLang(self.lang)

