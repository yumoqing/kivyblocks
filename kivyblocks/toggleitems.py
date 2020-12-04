from functools import partial
from kivy.uix.behaviors import TouchRippleButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory

from kivyblocks.ready import WidgetReady
from kivyblocks.bgcolorbehavior import BGColorBehavior
from kivyblocks.utils import CSize

class PressableBox(BGColorBehavior, TouchRippleButtonBehavior, BoxLayout):
	def __init__(self,border_width=1,
				color_level=-1,
				radius=[],
				**kw):
		BoxLayout.__init__(self, padding=[border_width,
			border_width,
			border_width,
			border_width],
			**kw)
		TouchRippleButtonBehavior.__init__(self)
		BGColorBehavior.__init__(self,color_level=color_level,
							radius=radius)
		self.border_width = border_width
		self.user_data = None
		self.unselected()

	def on_press(self,o=None):
		self.selected()

	def set_data(self,d):
		self.user_data = d

	def get_data(self):
		return self.user_data

class ToggleItems(BGColorBehavior, BoxLayout):
	def __init__(self,
				color_level=1,
				radius=[],
				orientation='horizontal',
				unit_size=3,
				items_desc=[],
				border_width=1,
				**kw):
		self.unit_size_pix = CSize(unit_size) 
		kw1 = {
			"orientation":orientation
		}
		kw1.update(kw)
		if orientation=='horizontal':
			kw1['size_hint_y'] = None
			kw1['height'] = self.unit_size_pix
			kw1['size_hint_min_x'] = self.unit_size_pix
		else:
			kw1['size_hint_x'] = None
			kw1['width'] = self.unit_size_pix
			kw1['size_hint_min_y'] = self.unit_size_pix
		
		BoxLayout.__init__(self, **kw1)
		BGColorBehavior.__init__(self,
					color_level=color_level,
					radius=radius)
		self.item_widgets = []
		kw = {
			"border_width":border_width,
			"color_level":color_level,
			"radius":radius
		}
		kw.update(kw1)

		for desc in items_desc:
			c = PressableBox(**kw)
			d = desc.get('data')
			if d:
				c.set_data(d)
			self.item_widgets.append(c)
			self.add_widget(c)
			c.bind(on_press=self.select_item)
			b = Factory.Blocks()
			def cb(c,o,w):
				c.add_widget(w)
			def eb(desc,o,e):
				print(desc,'error',e)
			b.bind(on_built=partial(cb,c))
			b.bind(on_failed=partial(eb,desc))
			b.widgetBuild(desc)

		if len(self.item_widgets) > 0:
			self.item_widgets[0].selected()
		else:
			print('items_desc=',items_desc,'error')
		self.register_event_type('on_press')
	
	def on_press(self,v=None):
		print('Toggle on_changed fired')
		pass

	def select_item(self,o=None):
		[i.unselected() for i in self.item_widgets if i != o]
		self.dispatch('on_press',o.get_data())

	def getValue(self):
		for i in self.item_widgets:
			if i.is_selected():
				return i.get_data()
		return None

	def setValue(self,v):
		for i in self.item_widgets:
			if i.get_data() == v:
				i.selected()
				self.select_iten(i)
				return

Factory.register('PressableBox',PressableBox)
Factory.register('ToggleItems',ToggleItems)
