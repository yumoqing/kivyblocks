from math import floor
from kivy.factory import Factory
from kivy.properties import NumericProperty, StringProperty, \
		DictProperty, ListProperty, OptionProperty, BooleanProperty
from kivy.logger import Logger
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.core.window import Window
from kivy.graphics import Color
from .responsivelayout import VResponsiveLayout
from .baseWidget import *
from .utils import *
from .i18n import I18n
from .toolbar import Toolbar
from .color_definitions import getColors
from .dataloader import DataGraber
from .ready import WidgetReady
from .widget_css import WidgetCSS
from .dateinput import DateInput
from .uitype.factory import UiFactory      # import get_input_builder

"""
form options
{
	"toolbar":
	"dataloader":{
		"dataurl":"first"
		"datatargment":"second",
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

class InputBox(BoxLayout):
	def __init__(self, form, **options):
		self.input_widget = None
		self.form = form
		self.options = options
		self.uitype = options.get('uitype',options.get('datatype','str'))
		self.size_hint = (None, None)
		height = self.form.inputheight
		if self.uitype == 'text':
			if not options.get('height'):
				self.options['height'] = 4
			height = self.options.get('height',4)

		self.labelwidth = self.form.labelwidth
		kwargs = {
			"orientation":'horizontal',
		}
		if height<=1:
			kwargs['size_hint_y'] = height
		else:
			kwargs['size_hint_y'] = None
			kwargs['height'] = CSize(height)
		if self.form.input_width <= 1:
			kwargs['size_hint_x'] = self.form.input_width
		else:
			kwargs['size_hint_x'] = None
			kwargs['width'] = self.form.input_width
		super().__init__(**kwargs)
		self.initflag = False
		self.register_event_type("on_datainput")
		self.init()
	
	def focus_act(self, *args):
		pass
		

	def on_size(self, *args):
		if self.input_widget is None:
			return
		self.labeltext.size_hint_x = None
		if self.form.labelwidth < 1:
			self.labeltext.width = self.width * self.form.labelwidth - \
									CSize(1)
		else:
			self.labeltext.width = CSize(self.form.labelwidth)

		self.input_widget.size_hint_x = None
		self.input_widget.width = self.width - self.labeltext.width - CSize(1)

	def on_datainput(self,o,v=None):
		pass
		#print('on_datainput fired ...',o,v)

	def init(self):
		if self.initflag:
			return
		i18n = I18n()
		label = self.options.get('label',self.options.get('name'))
		kwargs = {
			"i18n":True,
			"otext":label,
			"font_size":CSize(1),
		}
		if self.form.labelwidth <= 1:
			kwargs['size_hint_x'] = self.form.labelwidth
		else:
			kwargs['size_hint_x'] = None
			kwargs['width'] = CSize(self.form.labelwidth)

		self.labeltext = Text(**kwargs)
		self.add_widget(self.labeltext)
		if self.options.get('required',False):
			star = Label(text='*',
						color=(1,0,0,1),
						size_hint_x=None,
						width=CSize(1))
			self.add_widget(star)
		
		options = self.options.copy()
		options['hint_text'] = i18n(self.options.get('hint_text'))
		options['size_hint_y'] = None
		options['height'] = self.height
		self.input_widget = UiFactory.build_input_widget(options)
		try:
			self.input_widget.bind(focus=self.focus_act)
		except:
			pass
		self.input_widget.height = self.height
		self.input_widget.size_hint_y = None

		if self.form.labelwidth < 1:
			self.input_widget.size_hint_x = 1 - self.form.labelwidth
		else:
			self.input_widget.size_hint_x = None
			self.input_widget.width = self.width - self.labeltext.width - CSize(1)
		if self.options.get('readonly'):
			self.input_widget.disabled = True
		if self.options.get('value'):
			self.input_widget.setValue(self.options.get('value'))
		elif self.options.get('default_value'):
			self.input_widget.setValue(self.options.get('default_value'))

		self.input_widget.widget_id = self.options['name']
		self.add_widget(self.input_widget)
		if self.labelwidth<=1:
			self.labeltext.size_hint_x = self.labelwidth
			self.input_widget.size_hint_x = 1 - self.labelwidth
		else:
			self.labeltext.size_hint_x = None
			self.labeltext.width = CSize(self.labelwidth)
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
		"img_size_c":1,
		"text_size_c":1,
		"toolbar_orient":"H",
		"tool_orient":"horizontal",
		"tools":[
			{
				"name":"__submit",
				"source_on":blockImage("save.png"),
				"source_off":blockImage("save.png"),
				"label":"submit"
			},
			{
				"name":"__clear",
				"source_on":blockImage("clear.png"),
				"source_off":blockImage("clear.png"),
				"label":"clear"
			}
		]

	}

class Form(WidgetCSS, WidgetReady, BoxLayout):
	cols = NumericProperty(None)
	csscls=StringProperty('formcss')
	input_css=StringProperty('formfieldcss')
	inputwidth=NumericProperty(1)
	inputheight=NumericProperty(3)
	labelwidth=NumericProperty(0.3)
	toolbar_at=OptionProperty('top', \
						options=['top','bottom','left','right'])
	dataloader=DictProperty(None)
	fields = ListProperty([])
	toolbar=DictProperty(None)
	submit=DictProperty(None)
	clear=DictProperty(None)
	notoolbar=BooleanProperty(False)
	def __init__(self, **options):
		self.cols = 1
		self.toolbar_w = None
		if self.toolbar_at in ['top','bottom']:
			options['orientation'] = 'vertical'
		else:
			options['orientation'] = 'horizontal'
		SUPER(Form, self, options)
		self.setup_cols_and_inputwidth()
		self.init()
		self.register_event_type('on_submit')

	def setup_cols_and_inputwidth(self):
		if self.inputwidth > 1:
			self.input_width = CSize(self.inputwidth)
			return
		self.input_width = self.inputwidth

	def set_grid_attrs(self):
		self.fsc.box_width = self.input_width

	def on_size(self, *args):
		if not hasattr(self,'fsc'):
			return

		if not self.notoolbar:
			if self.toolbar_at in ['top', 'bottom']:
				self.fsc.height = self.height - self.toolbar_w.height
				self.fsc.width = self.width
			else:
				self.fsc.width = self.width - self.toolbar_w.width
				self.fsc.height = self.height
		else:
			if self.toolbar_at in ['top', 'bottom']:
				self.fsc.height = self.height
				self.fsc.width = self.width
			else:
				self.fsc.width = self.width
				self.fsc.height = self.height
		self.set_grid_attrs()

	def init(self):
		if not self.notoolbar:
			desc = defaultToolbar()
			desc1 = self.toolbar
			tools = desc['tools'].copy()
			if desc1:
				desc.update(desc1)
				tools = tools + desc1['tools']
			if self.submit:
				kw = self.submit.copy()
				if kw.get('name'):
					del kw['name']
				for t in tools:
					if t['name'] == '__submit':
						t.update(kw)
			if self.clear:
				kw = self.clear.copy()
				if kw.get('name'):
					del kw['name']
				for t in tools:
					if t['name'] == '__clear':
						t.update(kw)
				
			desc['tools'] = tools
			if self.toolbar_at in ['top', 'bottom']:
				desc['toolbar_orient'] = 'H'
			else:
				desc['toolbar_orient'] = 'V'
				desc['tool_orient'] = 'veritcal'
			
			self.toolbar_w = Factory.Toolbar(**desc)
		print('box_width=', self.input_width)
		self.fsc = VResponsiveLayout(
						box_width = self.input_width,
						size_hint=(1,1)
		)

		if self.toolbar_at in ['top', 'left'] and self.toolbar_w:
			self.add_widget(self.toolbar_w)
		self.add_widget(self.fsc)
		if self.toolbar_at in ['bottom', 'right'] and self.toolbar_w:
			self.add_widget(self.toolbar_w)
		
		self.fieldWidgets=[]
		for f in self.fields:
			w = InputBox(self, **f)
			self.fsc.add_widget(w)
			self.fieldWidgets.append(w)
			w.bind(on_ready=self.makeInputLink)
		wid = Factory.Blocks.getWidgetById('__submit',from_widget=self)
		if wid:
			wid.bind(on_press=self.on_submit_button)
		wid = Factory.Blocks.getWidgetById('__clear',from_widget=self)
		if wid:
			wid.bind(on_press=self.on_clear_button)
		if self.dataloader:
			self.loader = DataGraber(**self.dataloader)
			d = self.loader.load()
			if d:
				self.setValue(d)
		self.on_size()
			
	def makeInputLink(self,o,v=None):
		self.readiedInput += 1
		if self.readiedInput >= len(self.fields):
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

	def on_submit(self,o, v=None):
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
		self.input_css = options.get('input_css', 'input')
		i18n = I18n()
		self.input_widget = StrInput(
				text='',
				multiline=False,
				csscls=self.input_css,
				hint_text=i18n(options.get('tip',options.get('hint_text',''))),
				allow_copy=True,
				font_size=CSize(1),
				size_hint_y=None,
				size_hint_x=1,
				height=3)
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
		pass
