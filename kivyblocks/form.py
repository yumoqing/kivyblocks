from kivy.factory import Factory
from kivy.logger import Logger
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.graphics import Color
from kivycalendar import DatePicker
from .responsivelayout import VResponsiveLayout
from .widgetExt.inputext import FloatInput,IntegerInput, \
		StrInput,SelectInput, BoolInput, AmountInput, Password
from .baseWidget import *
from .utils import *
from .i18n import I18n
from .toolbar import Toolbar
from .color_definitions import getColors
from .bgcolorbehavior import BGColorBehavior
from .dataloader import DataGraber
from .ready import WidgetReady

"""
form options
{
	"toolbar":
	"dataloader":{
		"dataurl":"first"
		"datatarget":"second",
		"datarfname":"third"
		"params":
		"method"
	}
	"cols":"1"
	"labelwidth":
	"textsize":
	"inputheight":
	"inline":True,False
	"fields":[
		{
			"name":
			"label":
			"datatype",
			"uitype",
			"uiparams",
			"default",
			"readonly",
			"required"
		},
	]
	"binds":[
	]
}
"""

uitypes = {
	"str":{
		"orientation":"horizontal",
		"wclass":StrInput,
	},
	"string":{
		"orientation":"horizontal",
		"wclass":StrInput,
	},
	"password":{
		"orientation":"horizontal",
		"wclass":Password,
	},
	"int":{
		"orientation":"horizontal",
		"wclass":IntegerInput,
	},
	"number":{
		"orientation":"horizontal",
		"wclass":IntegerInput,
	},
	"float":{
		"orientation":"horizontal",
		"wclass":FloatInput,
	},
	"amount":{
		"orientation":"horizontal",
		"wclass":AmountInput,
	},
	"date":{
		"orientation":"horizontal",
		"wclass":DatePicker,
	},
	"time":{
		"orientation":"horizontal",
		"wclass":StrInput,
	},
	"bool":{
		"orientation":"horizontal",
		"wclass":BoolInput,
	},
	"code":{
		"orientation":"horizontal",
		"wclass":SelectInput,
	},
	"text":{
		"orientation":"horizontal",
		"wclass":StrInput,
		"options":{
			"multiline":True,
			"height":4,
		}
	},
	"teleno":{
		"orientation":"horizontal",
		"wclass":StrInput,
	},
	"email":{
		"orientation":"horizontal",
		"wclass":StrInput,
	},
}
class InputBox(BoxLayout):
	def __init__(self, form, **options):
		self.form = form
		self.options = options
		self.uitype = options.get('uitype',options.get('datatype','string'))
		self.uidef = uitypes[self.uitype]
		orientation = self.uidef['orientation']
		width = self.form.inputwidth
		height = self.form.inputheight
		if self.uitype == 'text':
			if not options.get('height'):
				self.options['height'] = 4
			height = self.options.get('height',4)

		self.labelwidth = self.form.options['labelwidth']
		kwargs = {
			"orientation":orientation,
		}
		if height<=1:
			kwargs['size_hint_y'] = height
		else:
			kwargs['size_hint_y'] = None
			kwargs['height'] = CSize(height)
		if width <= 1:
			kwargs['size_hint_x'] = width
		else:
			kwargs['size_hint_x'] = None
			kwargs['width'] = CSize(width)
		super().__init__(**kwargs)
		self.initflag = False
		self.bind(size=self.setSize,
					pos=self.setSize)
		self.register_event_type("on_datainput")

	def on_datainput(self,o,v=None):
		print('on_datainput fired ...',o,v)

	def init(self):
		if self.initflag:
			return
		i18n = I18n()
		opts = {
			"orientation":"horizontal",
			"size_hint_y":None,
			"height":CSize(2)
		}
		if self.labelwidth<=1:
			opts['size_hint_x'] = self.labelwidth
		else:
			opts['size_hint_x'] = None
			opts['width'] = self.labelwidth
		bl = BoxLayout(**opts)
		Logger.info('kivyblock:labelwidth=%f,opts=%s', self.labelwidth,str(opts))
		Logger.info('kivyblock:bl.widht=%f,bl.height=%f',bl.width,bl.height)
		self.add_widget(bl)
		label = self.options.get('label',self.options.get('name'))
		kwargs = {
			"i18n":True,
			"text":label,
			"font_size":CSize(1),
		}
		self.labeltext = Text(**kwargs)
		bl.add_widget(self.labeltext)
		Logger.info('kivyblock:label.widht=%f,label.height=%f',
						self.labeltext.width,self.labeltext.height)
		if self.options.get('required',False):
			star = Label(text='*',
						color=(1,0,0,1),
						size_hint_x=None,
						width=CSize(1))
			bl.add_widget(star)
		options = self.uidef.get('options',{}).copy()
		options.update(self.options.get('uiparams',{}))
		options['allow_copy'] = True
		options['width'] = options.get('width',1)
		options['height'] = options.get('height',1)
		if self.options.get('hint_text'):
			options['hint_text'] = i18n(self.options.get('hint_text'))

		Logger.info('Form: uitype=%s', self.uitype)
		self.input_widget = self.uidef['wclass'](**options)
		if self.options.get('readonly'):
			self.input_widget.disabled = True
		if self.options.get('value'):
			self.input_widget.setValue(self.options.get('value'))
		elif self.options.get('default_value'):
			self.input_widget.setValue(self.options.get('default_value'))

		self.input_widget.widget_id = self.options['name']
		self.add_widget(self.input_widget)
		self.initflag = True
		self.input_widget.bind(on_focus=self.on_focus)

	def check(self):
		d = self.getValue()
		v = d.get(self.options.get('name'))
		Logger.info('InputWidget() getValue=%s, name=%s',
						v,self.options.get('name'))
		if self.options.get('required',False) and \
				(v == '' or v is None):
			return False

		return True

	def clear(self):
		self.input_widget.setValue('')

	def on_focus(self,o,v):
		if v:
			self.old_value = o.text
		else:
			if self.old_value != o.text:
				self.dispatch('on_datainput',o.text)
		
	def setSize(self,o,v=None):
		self.init()
	
	def setValue(self,v):
		self.input_widget.setValue(v)
	
	def getValue(self):
		return {self.options.get('name'):self.input_widget.getValue()}
	
	def disable(self,*args,**kwargs):
		self.input_widget.disabled = True

	def enable(self,*args,**kwargs):
		self.input_widget.disabled = False

def defaultToolbar():
	return {
		"img_size":1.5,
		"text_size":0.7,
		"tools":[
			{
				"name":"__submit",
				"img_src":"/imgs/submit.png",
				"label":"submit"
			},
			{
				"name":"__clear",
				"img_src":"/imgs/clear.png",
				"label":"clear"
			}
		]

	}

class Form(BGColorBehavior, WidgetReady, BoxLayout):
	def __init__(self, **options):
		self.options = options
		BoxLayout.__init__(self, orientation='vertical')
		self.color_level = self.options.get('color_level', 0)
		BGColorBehavior.__init__(self,
			color_level=self.options.get('color_level',-1),
			radius=self.options.get('radius',[]))
		WidgetReady.__init__(self)
		self.readiedInput = 0
		self.cols = self.options_cols = self.options.get('cols',1)
		if isHandHold() and Window.width < Window.height:
			self.cols = 1
		self.inputwidth = Window.width / self.cols
		self.inputheight = self.options.get('inputheight',3)
		self.init()
		self.register_event_type('on_submit')

	def on_size(self, *args):
		pass

	def init(self):
		desc = defaultToolbar()
		desc1 = self.options.get('toolbar')
		if desc1:
			tools = desc['tools'] + desc1['tools']
			desc1['tools'] = tools
			desc = desc1
		if self.options.get('submit'):
			kw = self.options.get('submit').copy()
			if kw.get('name'):
				del kw['name']
			for t in desc['tools']:
				if t['name'] == '__submit':
					t.update(kw)
		if self.options.get('clear'):
			kw = self.options.get('clear').copy()
			if kw.get('name'):
				del kw['name']
			for t in desc['tools']:
				if t['name'] == '__clear':
					t.update(kw)
			
		self.toolbar = Toolbar(**desc)
		self.fsc = VResponsiveLayout(
						self.inputwidth,
						self.cols 
		)
		self.add_widget(self.toolbar)
		self.add_widget(self.fsc)
		self.fieldWidgets=[]
		for f in self.options['fields']:
			w = InputBox(self, **f)
			self.fsc.add_widget(w)
			self.fieldWidgets.append(w)
			w.bind(on_ready=self.makeInputLink)
		wid = Factory.Blocks.getWidgetById('__submit',from_widget=self)
		wid.bind(on_press=self.on_submit_button)
		wid = Factory.Blocks.getWidgetById('__clear',from_widget=self)
		wid.bind(on_press=self.on_clear_button)
		if self.options.get('dataloader'):
			self.dataloader = DataGraber(**self.options['dataloader'])
			d = self.dataloader.load()
			if d:
				self.setValue(d)
			
	def makeInputLink(self,o,v=None):
		self.readiedInput += 1
		if self.readiedInput >= len(self.options['fields']):
			p = self.fieldWidgets[0]
			for w in self.fieldWidgets[1:]:
				p.input_widget.focus_next = w.input_widget
				w.input_widget.focus_previous = p.input_widget
				p = w

	def setValue(self,d):
		for f in self.fieldWidgets:
			v = f.getValue()
			for k in v.keys():
				f.setValue({k:d[k]})

	def getValue(self):
		d = {}
		for f in self.fieldWidgets:
			v = f.getValue()
			d.update(v)
		return d

	def checkData(self):
		for w in self.fieldWidgets:
			if not w.check():
				w.input_widget.focus = True
				Logger.info('kivyblcks: input check false')
				return False
		Logger.info('kivyblcks: input check success')
		return True

	def on_submit(self,v=None):
		print('Form():on_submit fired ...',v)
		return False

	def on_submit_button(self,o,v=None):
		Logger.info('kivyblcks: submit button press')
		if not self.checkData():
			Logger.info('kivyblocks: CheckData False')
			return
		d = self.getValue()
		Logger.info('kivyblocks: fire on_submit')
		self.dispatch('on_submit',d)

	def on_clear_button(self,o,v=None):
		for fw in self.fieldWidgets:
			fw.clear()

class StrSearchForm(BoxLayout):
	def __init__(self,img_url=None,**options):
		self.name = options.get('name','search_string')
		BoxLayout.__init__(self,orientation='horizontal',size_hint_y=None,height=CSize(3))
		self.input_widget = StrInput(
				text='',
				multiline=False,
				allow_copy=True,
				halign='middle',
				font_size=1,
				size_hint_y=None,
				size_hint_x=1,
				height=2)
		self.add_widget(self.input_widget)
		self.register_event_type('on_submit')
		v = options.get('value',options.get('default_value',''))
		self.input_widget.setValue(v)
		self.input_widget.bind(on_text_validate=self.submit_input)

	def getValue(self):
		d = {
			self.name:self.input_widget.text
		}
		return d

	def setValue(self, d):
		if isinstance(d,str):
			self.input_widget.text = d
		if isinstance(d,{}):
			self.input_widget.text = d.get(self.name,'')

	def submit_input(self,o,v=None):
		text = self.input_widget.text
		if text != '':
			d = {
				self.name:text
			}
			self.dispatch('on_submit',d)

	def on_submit(self,v=None):
		print('StrSearchForm():on_submit fired ..........')

