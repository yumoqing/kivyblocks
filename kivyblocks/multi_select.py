from kivy.properties import BooleanProperty, StringProperty,\
		ListProperty, DictProperty
from kivyblocks.baseWidgets import VBox, PressableText
from kivyblocks.typewriterbox import TypeWriterBox

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
		self.button_state = {}

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
			dic = item.copy()
			if item['name'] in self.default_selected:
				dic['clscss'] = self.item_selected_cls
				state = 'selected'
			else:
				dic['clscss'] = self.item_cls
				state = 'unselected'
			b = PressableText(dic)
			b.bind(on_press=self.button_pressed)
			self.button_dic.update({b:dic})
			self.value_b.update({dic['value']:b})
			self.button_state.update({b:state})

	def button_pressed(self, o):
		if self.button_state[o] == 'selected':
			o.clscss = item_cls
			self.button_state.update({o:'unselected'})
		else:
			o.clscss = item_selected_cls
			self.button_state.update({o:'selected'})
		if self.button_dic[o]['value'] == '_all_' \
				and self.button_state[o] == 'selected':
			for b, state in self.button_state.copy().items():
				if b == o:
					continue
				b.clscss = item_cls
				self.button_state.update({b:'unselected'})
		
	def getValue(self):
		selected_buttons = [ b for b,state in self.button_state.item() \
				if state == 'selected' ]
		r = [ dic['value'] for b, dic in self.button_dic.items() \
				if b in selected_buttons ]
		return r

	def setValue(self, value):
		for v in value:
			b = self.value_b[v]
			self.button_state[b] = 'selected'
			b.clscss = item_selected_cls


