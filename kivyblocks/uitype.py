#uitype.py
"""
each ui type need to provides a view widget and a input widget
to auto construct the form widget and record show widget.

we use a register machinans to maintian the ui type information to build the view widget and input widget
"""

import ujson as json
from kivy.factory import Factory
from kivy.properties import NumericProperty, StringProperty, \
		BooleanProperty
from kivy.uix.label import Label

from appPublic.myTE import string_template_render

from kivyblocks.utils import CSize
from .baseWidget import WrapText, Text
from .dateinput import DateInput
from .widgetExt.inputext import FloatInput,IntegerInput, \
		StrInput,SelectInput, BoolInput, AmountInput, Password

class StringView(Label):
	def __init__(self, **kw):
		super(StringView, self).__init__(**kw)
		self.wrap = True
		self.halign = 'left'
		self.valign = 'middle'

	def getValue(self):
		return self.text

	def setValue(self, v):
		self.text = str(v)

class PasswordView(StringView):
	def __init__(self, text='*', **kw):
		super(PasswordView, self).__init__(text=text, **kw)

	def getValue(self):
		return None

	def setValue(self, v):
		pass

class TextView(WrapText):
	def getValue(self):
		return self.text

	def setValue(self, v):
		self.text = v

view_widget_builders = {
}

input_widget_builders = {}

def view_register(uitype, f):
	view_widget_builders.update({uitype:f})

def input_register(uitype, f):
	input_widget_builders.update({uitype:f})

def get_input_builder(uitype):
	return input_widget_builders.get(uitype, \
			input_widget_builders.get('str', None))

def get_view_builder(uitype):
	return view_widget_builders.get(uitype, \
			view_widget_builders.get('str', None))

def build_view_widget(desc, rec = None):
	viewer = desc.get('viewer')
	if viewer:
		if isinstance(viewer,dict):
			viewer = json.dumps(viewer)
		rendered = string_template_render(viewer, rec)
		dic = json.loads(rendered)
		if dic is None:
			return None
		w = Factory.Blocks().widgetBuild(dic)
		return w
		
	f = get_view_builder(desc.get('uitype'))
	return f(desc, rec)

def build_input_widget(desc, rec=None):
	f = get_input_builder(desc.get('uitype'))
	return f(desc, rec)

def get_value(desc, rec=None):
	if rec:
		return rec.get(desc['name'])
	return desc.get('value', desc.get('defaultvalue', ''))
	
def build_view_str_widget(desc, rec=None):
	txt = get_value(desc, rec=rec)
	return StringView(text=str(txt) if txt else '',
						font_size=CSize(1),
						halign='left',
						valign='middle')

view_register('str', build_view_str_widget)
view_register('date', build_view_str_widget)
view_register('time', build_view_str_widget)
view_register('timestamp', build_view_str_widget)

def build_view_text_widget(desc, rec=None):
	txt = get_value(desc, rec=rec)
	return TextView(text=str(txt) if txt else '',
						font_size=CSize(1),
						halign='left',
						valign='middle')

view_register('text', build_view_text_widget)

def build_view_passwd_widget(desc, rec=None):
	return PasswordView(text='*',
						font_size=CSize(1),
						halign='left',
						valign='middle')

view_register('password', build_view_passwd_widget)

class BoolView(Label):
	value = BooleanProperty(False)
	def __init__(self, text='', **kw):
		super(BoolView, self).__init__(text='', **kw)
		self.wrap = True
		self.halign = 'center'
		self.valign = 'middle'
	
	def on_value(self, *args):
		if self.value:
			self.text = 'true'
		else:
			self.text = 'false'

	def getValue(self):
		return self.value

	def setValue(self, v):
		self.value = v

def build_view_bool_widget(desc, rec=None):
	v = get_value(desc, rec)
	if v is not None:
		return BoolView(value=v,
						font_size=CSize(1),
						halign='left',
						valign='middle')
	
	default_value = desc.get('nullvalue',False)
	return BoolView(value=default_Value,
						font_size=CSize(1),
						halign='left',
						valign='middle')

view_register('bool', build_view_bool_widget)

class IntView(Text):
	value = NumericProperty(None)
	nullstr = StringProperty('')
	def __init__(self, **kw):
		super(IntView, self).__init__(text='', **kw)
		self.wrap = True
		self.halign = 'right'
		self.valign = 'middle'

	def on_value(self, *args):
		if self.value is not None:
			self.text = str(v)
		else:
			self.text = self.nullstr

	def setValue(self, v):
		self.value = v

	def getValue(self):
		return self.value

def build_view_int_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	return IntValue(value=v,
			nullstr=desc.get('nullstr',''),
			font_size=CSize(1), 
			halign='right', 
			valign='middle'
	)

view_register('int', build_view_int_widget)

class FloatView(Text):
	value = NumericProperty(None)
	nullstr = StringProperty('')
	dec = NumericProperty(2)
	def __init__(self, **kw):
		super(FloatView, self).__init__(text=self.nullstr, **kw)
		self.wrap = True
		self.halign = 'right'
		self.valign = 'middle'

	def on_value(self, *args):
		if self.value is None:
			self.text = self.bullstr
		f = '%%.0%df' % self.dec
		self.text = f % self.value
		
	def getValue(self):
		return self.value

	def setValue(self, v):
		self.value = v

def build_view_float_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	return FloatView(value=v,
					dec=desc.get('dec', 2),
					nullstr=desc.get('nullstr',''),
					font_size=CSize(1), 
					halign='right', 
					valign='middle'
			)

view_register('float', build_view_float_widget)

def build_view_code_widget(desc, rec=None):
		tf = desc.get('textField','text')
		vf = desc.get('valueField','value')
		v = rec.get(tf,rec.get(vf, ' '))
		return Text(text=v, 
					i18n=True,
					font_size = CSize(1), 
					wrap=True,
					halign='center', 
					valign='middle'
		)

view_register('code', build_view_code_widget)

class AmountView(FloatView):
	def on_value(self, *args):
		if self.value is None:
			self.text = self.nullstr
		else:
			self.text = self.amount_str()
	
	def amount_str(self):
		f = '%%.0%df' % self.dec
		s = f % self.value
		parts = s.split('.')
		p_int = parts[0]
		subs = []
		if p_int[0] == '-':
			subs.append('-')
			p_int = p_int[1:]
		l = [i for i in p_int]
		l.reverse()
		k = []
		for i,c in enumerate(l):
			if i and (i) % 3 == 0:
				k.append(',')
			k.append(c)
		k.reverse()
		subs.append(''.join(k))
		if len(parts) > 1:
			subs.append(f'.{parts[1]}')
		return ''.join(subs)

def build_view_amount_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	defaultvalue = desc.get('nullstr', '')
	return Amount(value=v,
					dec=desc.get('dec', 2),
					nullstr=defaultvale,
					font_size=CSize(1), 
					halign='right', 
					valign='middle'
	)

view_register('amount', build_view_amount_widget)

def build_input_str_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = StrInput(**kw)
	if v:
		w.setValue(v)
	return w

input_register('str', build_input_str_widget)

def build_input_text_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	kw['multiline'] = True
	w = StrInput(**kw)
	if v:
		w.setValue(v)
	return w
	
input_register('text', build_input_text_widget)

def build_input_int_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = IntegerInput(**kw)
	if v:
		w.setValue(v)
	return w
	
input_register('int', build_input_int_widget)
input_register('time', build_input_int_widget)

def build_input_float_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = FloatInput(**kw)
	if v:
		w.setValue(v)
	return w
	
input_register('float', build_input_float_widget)

def build_input_amount_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = AmountInput(**kw)
	if v:
		w.setValue(v)
	return w
	
input_register('amount', build_input_amount_widget)

def build_input_date_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = DateInput(**kw)
	if v:
		w.setValue(v)
	return w
	
input_register('date', build_input_date_widget)

def build_input_bool_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = BoolInput(**kw)
	if v:
		w.setValue(v)
	return w
	
input_register('bool', build_input_bool_widget)

def build_input_code_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = SelectInput(**kw)
	if v:
		w.setValue(v)
	return w
	
input_register('code', build_input_code_widget)

def build_input_password_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = Password(**kw)
	if v:
		w.setValue(v)
	return w
	
input_register('password', build_input_password_widget)

