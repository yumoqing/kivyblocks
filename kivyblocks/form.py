from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivycalendar import DatePicker
from .responsivelayout import VResponsiveLayout
from .widgetExt.inputext import FloatInput,IntegerInput, \
		StrInput,SelectInput, BoolInput, AmountInput, Password
from .baseWidget import *
from .utils import *
from .i18n import I18nText, I18n
from .toolbar import Toolbar
"""
form options
{
	"toolbar":
	"dataloader":{
		"dataurl":
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
	"string":{
		"orientation":"horizontal",
		"wclass":StrInput,
	},
	"password":{
		"orientation":"horizontal",
		"wclass":Password,
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
		"orientation":"vertical",
		"wclass":StrInput,
		"options":{
			"multiline":True,
			"height":CSize(6),
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
		self.uitype = options.get('uitype','string')
		self.uidef = uitypes[self.uitype]
		orientation = self.uidef['orientation']
		width = self.form.inputwidth
		height = self.form.inputheight
		self.labelwidth = self.form.options['labelwidth']
		kwargs = {
			"orientation":orientation,
			"size_hint_y":None,
			"height":height
		}
		if width <= 1:
			kwargs['size_hint_x'] = width
		else:
			kwargs['size_hint_x'] = None
			kwargs['width'] = CSize(width)
		super().__init__(**kwargs)
		self.initflag = False
		self.bind(on_size=self.setSize,
					pos=self.setSize)
		self.register_event_type("on_datainput")

	def on_datainput(self,o,v=None):
		print('on_datainput fired ...',o,v)

	def init(self):
		i18n = I18n()
		if self.initflag:
			return
		label = self.options.get('label',self.options.get('name'))
		if self.options.get('required'):
			label = label + '*'
		kwargs = {
			"otext":label,
			"font_size":CSize(1),
			"size_hint_y":None,
			"height":CSize(2)
		}
		if self.labelwidth<=1:
			kwargs['size_hint_x'] = self.labelwidth
		else:
			kwargs['size_hint_x'] = None
			kwargs['width'] = self.labelwidth

		self.labeltext = I18nText(**kwargs)
		self.add_widget(self.labeltext)
		options = self.uidef.get('options',{}).copy()
		options.update(self.options.get('uiparams',{}))
		options['allow_copy'] = True
		if self.options.get('tip'):
			options['hint_text'] = i18n(self.options.get('tip'))

		print('uitype=',self.options['uitype'], self.uitype, 'uidef=',self.uidef)
		self.input_widget = self.uidef['wclass'](**options)
		if self.options.get('readonly'):
			self.input_widget.disabled = True
		self.form.widget_ids[self.options['name']] = self.input_widget
		self.add_widget(self.input_widget)
		self.initflag = True
		self.input_widget.bind(on_focus=self.on_focus)
		if self.options.get('default'):
			self.input_widget.setValue(self.options.get('default'))
			
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

class Form(BoxLayout):
	def __init__(self, **options):
		self.options = options
		BoxLayout.__init__(self, orientation='vertical')
		self.widget_ids = {}
		self.cols = self.options_cols = self.options.get('cols',1)
		if isHandHold() and Window.width < Window.height:
			self.cols = 1
		self.inputwidth = Window.width / self.cols
		self.inputheight = CSize(self.options.get('inputheight',3))
		self.initflag = False
		self.register_event_type('on_submit')
		self.bind(size=self.on_size,
					pos=self.on_size)

	def init(self):
		if self.initflag:
			return
		self.toolbar = Toolbar(ancestor=self,**self.options.get('toolbar',defaultToolbar()))
		self.fsc = VResponsiveLayout(
						self.inputwidth,
						self.cols 
		)
		print('box_width=%d,cols=%d' % (self.inputwidth, self.cols))
		self.add_widget(self.toolbar)
		self.add_widget(self.fsc)
		self.fieldWidgets=[]
		for f in self.options['fields']:
			w = InputBox(self, **f)
			# print('w size=',w.size)
			self.fsc.add_widget(w)
			self.fieldWidgets.append(w)
		blocks = App.get_running_app().blocks
		# wid = self.widget_ids['__submit']
		wid = blocks.getWidgetByIdPath(self,'__submit')
		wid.bind(on_press=self.on_submit_button)
		wid = blocks.getWidgetByIdPath(self,'__clear')
		# wid = self.widget_ids['__clear']
		wid.bind(on_press=self.on_clear_button)
		self.initflag = True

	def getData(self):
		d = {}
		for f in self.fieldWidgets:
			v = f.getValue()
			d.update(v)
		return d

	def on_submit(self,v=None):
		print('Form():on_submit fired ...',v)
		return False

	def on_submit_button(self,o,v=None):
		d = self.getData()
		self.dispatch('on_submit',d)

	def on_clear_button(self,o,v=None):
		for fw in self.fieldWidgets:
			fw.clear()

	def on_size(self,o, v=None):
		self.init()
	
class StrSearchForm(BoxLayout):
	def __init__(self,img_url=None,**options):
		self.name = options.get('name','search_string')
		BoxLayout.__init__(self,orientation='horizontal',size_hint_y=None,height=CSize(3))
		self.inputwidget = TextInput(
				text='',
				multiline=False,
				font_size=CSize(1),
				size_hint_y=None,
				height=CSize(3))
		self.add_widget(self.inputwidget)
		imgsrc = img_url if img_url else blockImage('search.png')
		self.search = PressableImage(source=imgsrc,
					size_hint=(None,None),
					size=CSize(3,3)
		)
		self.add_widget(self.search)
		self.register_event_type('on_submit')
		self.search.bind(on_press=self.submit_input)
		self.inputwidget.bind(on_text_validate=self.submit_input)

	def getData(self):
		d = {
			self.name:self.inputwidget.text
		}
		return d

	def submit_input(self,o,v=None):
		text = self.inputwidget.text
		if text != '':
			d = {
				self.name:text
			}
			self.dispatch('on_submit',d)

	def on_submit(self,v=None):
		print('StrSearchForm():on_submit fired ..........')

