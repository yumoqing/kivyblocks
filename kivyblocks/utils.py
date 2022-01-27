import os
from traceback import print_exc
from traceback import print_exc
from kivy.app import App
from kivy.logger import Logger
from appPublic.jsonConfig import getConfig
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.image import AsyncImage
from appPublic.dictObject import DictObject

from .kivysize import KivySizes

class NeedLogin(Exception):
	pass

class InsufficientPrivilege(Exception):
	pass

class HTTPError(Exception):
	def __init__(self,resp_code):
		self.resp_code = resp_code
		Exception.__init__(self)

	def __expr__(self):
		return f'Exception:return code={self.resp_code}'

	def __str__(self):
		return f'Exception:return code={self.resp_code}'

alert_widget= None

def kwarg_pop(obj, kw):
	keys = [k for k in kw.keys()]
	for k in keys:
		if hasattr(obj, k):
			setattr(obj, k, kw.pop(k))

def SUPER(klass, obj, kw):
	keys = [ k for k in kw.keys() ]
	dic = { k:kw.pop(k) for k in keys if hasattr(obj, k) }
	super(klass, obj).__init__(**kw)
	for k,v in dic.items():
		try:
			setattr(obj, k, v)
		except Exception as e:
			print(f'obj={obj}, setattr(obj, "{k}","{v}") error')
			print_exc()
			raise e

def blockImage(name):
	p = os.path.dirname(os.path.abspath(__file__))
	return os.path.join(p,'imgs',name)

def loaded(widget):
	widget.loadingwidget.dismiss()
	# widget.remove_widget(widget.loadingwidget)
	del widget.loadingwidget
	widget.loadingwidget = None

def loading(parent):
	fp = os.path.join(os.path.dirname(__file__),'imgs','loading1.gif')
	image = AsyncImage(source=blockImage('loading1.gif'), \
					width=CSize(2), height=CSize(2),
					size_hint=(None,None))
	view = ModalView(auto_dismiss=False)
	view.add_widget(image)
	view.center = parent.center
	parent.loadingwidget = view
	# parent.add_widget(view)
	view.open()
	return view

def set_widget_width(self, width):
	if width <= 1:
		self.size_hint_x = width
	else:
		self.size_hint_x = None
		self.width = width

def set_widget_height(self, height):
	if height <= 1:
		self.size_hint_y = height
	else:
		self.size_hint_y = None
		self.height = height

def setSizeOptions(desc,kw):
	"""
	desc's width, and height to setup a widget's size options 
	if width or height is not set, kw add not thing 
	if width or height <= 1, using present rate of size
	else use CSize to tims width or height
	"""
	if not isinstance(kw, DictObject):
		kw = DictObject(**kw)
	
	width = desc.get('width',0)
	if width > 1.01:
		kw.width = CSize(width)
		kw.size_hint_x = None
	elif width > 0.00:
		kw.size_hint_x = width

	height = desc.get('height',0)
	if height > 1.01:
		kw.height = CSize(height)
		kw.size_hint_y = None
	elif height > 0.00:
		kw.size_hint_y = height
	return kw
	
def alert(text,title='alert'):
	global alert_widget
	def close_alert(obj):
		alert_widget.dismiss()

	charsize = CSize(1)
	if alert_widget is None:
		bl = BoxLayout(orientation='horizontal')
		msg = Label(font_size=charsize)
		bl.add_widget(msg)
		button = Button(size_hint_y=None,height=1.4*charsize,font_size=charsize,text='OK')
		button.bind(on_press=close_alert)
		bl.add_widget(button)
		alert_widget = Popup(content=bl, size_hint=(0.9,0.6))
		alert_widget.msg_widget = msg
	alert_widget.msg_widget.text = str(text)
	alert_widget.title = str(title)
	alert_widget.open()

def StrConvert(s):
	if not s.startswith('py::'):
		return s
	s = s[4:]
	try:
		ns = {}
		exec('_n_=' + s,globals(),ns)
		return ns['_n_']
	except Exception as e:
		print('----e=',e,'------------s=',s)
		return s

def ArrayConvert(a):
	s = []
	for i in a:
		s.append(JDConvert(i))
	return s

def DictConvert(dic):
	d = {}
	for k,v in dic.items():
		if k == 'widgettype':
			d[k] = v
		else:
			d[k] = JDConvert(v)
	return d

def JDConvert(dic):
	nd = {}
	if type(dic) == type(''):
		return StrConvert(dic)
	if type(dic) == type([]):
		return ArrayConvert(dic)
	if type(dic) == type({}):
		return DictConvert(dic)
	return dic
				
def getWidgetById(w,id):
	if id[0] == '/':
		app = App.get_running_ap()
		if not hasattr('ids'):
			return None
		return app.ids.get(id[1:])
	if id in ['self', '.' ]:
		return w
	if not hasattr(w,'ids'):
		return None
	return w.ids.get(id)
		
def CSize(x,y=None,name=None):
	ks = KivySizes()
	return ks.CSize(x,y=y,name=name)

def screenSize():
	ks = KivySizes()
	return ks.getScreenSize()

def screenPhysicalSize():
	ks = KivySizes()
	return ks.getScreenPhysicalSize()

def isHandHold():
	ks = KivySizes()
	return ks.isHandHold()

def absurl(url,parent):
	if parent is None:
		parent = ''
	config = getConfig()
	if url.startswith('http://'):
		return url
	if url.startswith('https://'):
		return url
	if url.startswith('file:///'):
		return url
	if url.startswith('/'):
		return config.uihome + url
	if url.startswith(config.uihome):
		return url
	if parent == '':
		print('url=',url)
		raise Exception('related url(%s) need a parent url' % url)

	if parent.startswith(config.uihome):
		parent = parent[len(config.uihome):]
	paths = parent.split('/')
	paths.pop()
	for i in url.split('/'):
		if i in [ '.', '' ]:
			continue
		if i == '..':
			if len(paths) > 1:
				paths.pop()
			continue
		paths.append(i)
	return config.uihome + '/'.join(paths)

def show_widget_info(w, tag='DEBUG'):
	id = getattr(w, 'widget_id', 'null')
	msg=f"""{tag}:size_hint={w.size_hint},size={w.size},pos={w.pos},widget_id={id},{w}"""
	Logger.info(msg)
