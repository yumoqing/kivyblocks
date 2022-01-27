
from kivy.uix.label import Label
from kivy.properties import NumericProperty, StringProperty
from ..baseWidget import IntegerInput
from ..utils import *
from .factory import UiFactory, StringView

class IntView(Label):
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

	@classmethod
	def builder(self,desc, rec=None):
		v = get_value(desc, rec=rec)
		return IntValue(value=v,
				nullstr=desc.get('nullstr',''),
				font_size=CSize(1), 
				halign='right', 
				valign='middle'
		)

def build_input_int_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = IntegerInput(**kw)
	if v is not None:
		w.setValue(v)
	return w
	
UiFactory.register('int',  build_input_int_widget, IntView.builder)

