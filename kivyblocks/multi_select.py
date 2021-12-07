from kivy.properties import BooleanProperty, StringProperty,\
		ListProperty, DictProperty
from kivyblocks.baseWidgets import VBox, PressableText
from kivyblocks.typewriterbox import TypeWriterBox
from kivy.factory import Factory

class MultiSelect(TypeWriterBox):
	items = ListProperty([])
	item_cls = DictProperty({})
	item_selected_cls = DictProperty({})
	all_button_position = StringProperty(None)
	default_selected=StringProperty([])
	
	def __init__(self, **kw):
		super(MultiSelectBotton, self).__init__(**kw)
		self.button_dic = {}
		self.value_b = {}

	def buildItem(self, dic):
		keys = dic.keys()
		ToggleText = Factory.ToggleText
		ToggleImage = Factory.ToggleImage
		if 'text' in keys and 'value' in keys:
			desc = dic.copy()
			desc['off_css'] = self.item_css
			desc['on_css'] = self.item_selected_css
			return ToggleText(**desc)
		if 'source' in keys and 'on_source' in keys:
			return ToggleImage(**dic)

	def on_items(self, o, items):
		self.clear_widgets()
		if all_button_position is not None:
			dic = {
				'text':'all',
				'value':'_all_',
			}
			if all_button_position == 'begin':
				items.insert(dic,0)
			else:
				items.append(dic)
		for item in items:
			b = self.buildItem(item)
			b.bind(on_press=self.button_pressed)
			self.button_dic.update({b:dic})
			self.value_b.update({dic['value']:b})

	def button_pressed(self, o):
		o.toggle()
		if self.button_dic[o]['value'] == '_all_' and o.state():
			for b, dic in self.button_dic.copy().items():
				if b == o:
					continue
				b.select(False)
		
	def getValue(self):
		selected_buttons = [ b for b in self.button_dic.item() \
				if b.state() ]
		r = [ dic['value'] for b, dic in self.button_dic.items() \
				if b in selected_buttons ]
		return r

	def setValue(self, value):
		for v in value:
			b = self.value_b[v]
			b.select(True)


