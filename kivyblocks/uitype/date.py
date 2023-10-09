
from ..utils import *
from ..dateinput import DateInput
from .factory import UiFactory, StringView, get_value

def build_input_date_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = DateInput(**kw)
	if v:
		w.setValue(v)
	return w

UiFactory.register('date', build_input_date_widget, StringView.builder)

