from kivy.uix.label import Label
from kivyblocks.widgetExt.inputext import StrInput
from ..utils import *

view_widget_builders = {
}

input_widget_builders = {
}

def get_value(desc, rec=None):
	if rec:
		return rec.get(desc['name'])
	return desc.get('value', desc.get('defaultvalue', ''))

class UiFactory:
	@classmethod
	def register(self, ut, inpf, viewf):
		view_widget_builders.update({ut:viewf})
		input_widget_builders.update({ut:inpf})

	@classmethod
	def build_view_widget(self, desc, rec=None):
		ut = desc.get('uitype', 'str')
		f = view_widget_builders.get(ut)
		if f is None:
			print(desc, 'view builder not defined')
			return None
		return f(desc, rec=rec)

	@classmethod
	def build_input_widget(self, desc, rec=None):
		ut = desc.get('uitype', 'str')
		f = input_widget_builders.get(ut)
		if f is None:
			print(desc, 'input builder not defined')
			return None
		return f(desc, rec=rec)

class StringView(Label):
	@classmethod 
	def builder(self, desc, rec):
		txt = get_value(desc, rec=rec)
		return StringView(text=str(txt) if txt else '',
						font_size=CSize(1),
						halign='left',
						valign='middle')

	def __init__(self, **kw):
		super(StringView, self).__init__(**kw)
		self.wrap = True
		self.halign = 'left'
		self.valign = 'middle'

	def getValue(self):
		return self.text

	def setValue(self, v):
		self.text = str(v)

class StringInput(StrInput):
	@classmethod
	def builder(self, desc, rec):
		v = get_value(desc, rec=rec)
		kw = desc.get('uiparams', {})
		kw['multiline'] = False
		w = StringInput(**kw)
		if v:
			w.setValue(v)
		return w

UiFactory.register('str', StringInput.builder, StringView.builder)

