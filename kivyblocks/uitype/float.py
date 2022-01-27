

from kivy.uix.label import Label
from kivy.properties import NumericProperty, StringProperty
from ..baseWidget import FloatInput
from ..utils import *
from .factory import UiFactory, get_value

class FloatView(Label):
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

	@classmethod
	def builder(self, desc, rec=None):
		v = get_value(desc, rec=rec)
		return FloatView(value=v,
						dec=desc.get('dec', 2),
						nullstr=desc.get('nullstr',''),
						font_size=CSize(1), 
						halign='right', 
						valign='middle'
				)

def build_input_float_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = FloatInput(**kw)
	if v is not None:
		w.setValue(v)
	return w
	
UiFactory.register('float', build_input_float_widget, FloatView.builder)

