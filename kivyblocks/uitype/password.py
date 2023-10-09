
from ..baseWidget import Password
from ..utils import *
from .factory import UiFactory, get_value, StringView

class PasswordView(StringView):
	def __init__(self, text='*', **kw):
		super(PasswordView, self).__init__(text=text, **kw)

	def getValue(self):
		return None

	def setValue(self, v):
		pass

	def builder(self, desc, rec=None):
		return PasswordView(text='*',
						font_size=CSize(1),
						halign='left',
						valign='middle')

def build_input_password_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	kw = desc.get('uiparams', {})
	w = Password(**kw)
	if v:
		w.setValue(v)
	return w
	
UiFactory.register('password', build_input_password_widget, PasswordView.builder)

