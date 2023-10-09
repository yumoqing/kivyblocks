
from ..baseWidget import WrapText, StrInput
from ..utils import *
from .factory import UiFactory, get_value

class TextView(WrapText):
	def getValue(self):
		return self.text

	def setValue(self, v):
		self.text = v

	@classmethod
	def builder(self, desc, rec=None):
		txt = get_value(desc, rec=rec)
		return TextView(text=str(txt) if txt else '',
						font_size=CSize(1),
						halign='left',
						valign='middle')

def build_input_text_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = StrInput(**kw)
	if v:
		self.multiline = True
		w.setValue(v)
	return w
	
UiFactory.register('text', build_input_text_widget, TextView.builder)

