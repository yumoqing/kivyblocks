from kivy.properties import BooleanProperty, StringProperty,\
		ListProperty, DictProperty
from kivyblocks.baseWidgets import VBox, PressableText

class MultiSelect(VBox):
	items = ListProperty([])
	item_cls = DictProperty({})
	item_selected_cls = DictProperty({})
	all_button_position = StringProperty('begin')
	default_selected=StringProperty([])
	
	def __init__(self, **kw):
		super(MultiSelectBotton, self).__init__(**kw)
		self.button_dic = {}
		self.button_state = {}

	def on_items(self, o, items):
		self.clear_widgets()
		dic = {
			'text':'all',
			'value':None,
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
			self.button_state.update({b:state})

	def button_pressed(self, o):
		if self.button_state[o] == 'selected':
			o.clscss = item_cls
			self.button_state.update({o:'unselected'})
		else:
			o.clscss = item_selected_cls
			self.button_state.update({o:'selected'})
		if self.button_dic[o]['text'] == 'all' \
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

	def setValue(self, v):
		pass

