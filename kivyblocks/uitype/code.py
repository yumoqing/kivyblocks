
from ..baseWidget import Text, SelectInput
from ..utils import *

from .factory import UiFactory, get_value

def build_input_code_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = SelectInput(**kw)
	if v:
		w.setValue(v)
	return w
	
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

UiFactory.register('code', build_input_code_widget, build_view_code_widget)

