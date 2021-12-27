from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.stacklayout import StackLayout
from kivy.properties import BooleanProperty, StringProperty,\
		ListProperty, DictProperty, OptionProperty, \
		NumericProperty

from kivyblocks.baseWidget import VBox 
from kivyblocks.clickable import ToggleText, ToggleImage
from kivyblocks.utils import SUPER, CSize
from kivyblocks.widget_css import WidgetCSS
from kivyblocks.ready import WidgetReady

class MultiSelect(WidgetCSS, WidgetReady, StackLayout):
	"""
	{
		"widgettype":"MultiSelect",
		"options":{
			"valueField"
			"textField"
			"items"
			"item_css"
			"item_selected_css"
			"all_position"
			"need_others"
			"default_selected"
		}
	}
	"""
	valueField = StringProperty('value')
	textField = StringProperty('text')
	x_spacing_c = NumericProperty(1)
	y_spacing_c = NumericProperty(0.5)
	items = ListProperty([])
	item_css = StringProperty({})
	item_selected_css = StringProperty({})
	all_position = OptionProperty(None, \
					options=[None, 'begin', 'end'])
	need_others = BooleanProperty(False)
	default_selected=ListProperty([])
	result = ListProperty([])
	def __init__(self, **kw):
		SUPER(MultiSelect, self, kw)
		self.spacing = CSize(self.x_spacing_c, self.y_spacing_c)
		self.orientation = 'lr-tb'
		self.build_all_items()
		self.old_result = []
		self.register_event_type('on_changed')
		self.button_dic = {}
		self.value_b = {}
		self.buildWidgets()
	
	def build_all_items(self):
		items = [i for i in self.items ]
		if self.need_others:
			dic = {
				self.valueField:'_other_',
				self.textField:'others'
			}
			items.append(dic)

		if self.all_position is not None:
			dic = {
				self.textField:'all',
				self.valueField:'_all_',
			}
			if self.all_position == 'begin':
				items.insert(0, dic)
			else:
				items.append(dic)
		self.all_items = items

	def on_changed(self, d):
		pass

	def build_item_widget(self, dic):
		keys = dic.keys()
		ToggleText = Factory.ToggleText
		ToggleImage = Factory.ToggleImage
		ToggleIconText = Factory.ToggleIconText
		if self.textField in keys and 'source_on' in keys and \
					'source_off' in keys:
			desc['text'] = dic[self.textField]
			desc['css_off'] = self.item_css
			desc['css_on'] = self.item_selected_css
			desc["source_on"] = dic['source_on'],
			desc["source_off"] = dic['source_off']
			print('ToggleIconText', desc)
			return ToggleIconText(**desc)
			
		if self.textField in keys:
			desc = {}
			desc['text'] = dic[self.textField]
			desc['css_off'] = self.item_css
			desc['css_on'] = self.item_selected_css
			print('ToggleText', desc)
			return ToggleText(**desc)
		if 'source_on' in keys and 'source_off' in keys:
			desc = {
				"source_on":dic['source_on'],
				"source_off":dic['source_off']
			}
			print('ToggleImage', desc)
			return ToggleImage(**desc)

	def buildWidgets(self):
		self.clear_widgets()
		for item in self.all_items:
			b = self.build_item_widget(item)
			b.bind(on_press=self.button_pressed)
			self.button_dic.update({b:item})
			self.add_widget(b)

	def button_pressed(self, o):
		o.toggle()
		if self.button_dic[o][self.valueField] == '_all_' and o.state():
			for b, dic in self.button_dic.items():
				if b == o:
					continue
				b.select(False)
		if self.button_dic[o][self.valueField] == '_other_' and o.state():
			for b, dic in self.button_dic.items():
				if b == o:
					continue
				b.select(False)
		if self.button_dic[o][self.valueField] not in ['_all_', '_other_'] \
						and o.state():
			for b, dic in self.button_dic.items():
				if dic[self.valueField] in ['_all_', '_other_']:
					b.select(False)
		Clock.schedule_once(self.set_result, 0.1)

	def set_result(self, t=None):
		self.result = [ d[self.valueField] for b, d in \
							self.button_dic.items() if b.state() ]
		if self.result != self.old_result:
			self.dispatch('on_changed', self.result)
		self.old_result = self.result
		
	def getValue(self):
		self.set_result()
		return self.result

	def setValue(self, value):
		self.result = value
		self.old_result = value
		for v in value:
			b = self.value_b[v]
			b.select(True)


