from functools import partial
from kivy.logger import Logger
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty

from kivyblocks.ready import WidgetReady
from kivyblocks.bgcolorbehavior import BGColorBehavior
from kivyblocks.utils import CSize
from kivyblocks.baseWidget import Box
from kivyblocks.widget_css import WidgetCSS
from kivyblocks.clickable import PressableBox

"""
ToggleItems format:
{
	radius:
	unit_size:
	items_desc:
	border_width:
	orientation:
}
"""
class ToggleItems(BoxLayout, WidgetCSS):
	def __init__(self,
				radius=[],
				orientation='horizontal',
				unit_size=3,
				items_desc=[],
				border_width=1,
				normal_css="default",
				actived_css="default",
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
		self.item_widgets = []
		kw = {
			"border_width":border_width,
			"normal_css":normal_css,
			"actived_css":actived_css,
			"radius":radius
		}
		kw.update(kw1)

		for desc in items_desc:
			c = PressableBox(**kw)
			self.item_widgets.append(c)
			self.add_widget(c)
			c.bind(on_press=self.select_item)
			if desc.get('data'):
				c.setValue(desc['data'])

			b = Factory.Blocks()
			def cb(c,o,w):
				c.add_widget(w)
			def eb(desc,o,e):
				print(desc,'error',e)
			b.bind(on_built=partial(cb,c))
			b.bind(on_failed=partial(eb,desc))
			b.widgetBuild(desc)

		if len(self.item_widgets) > 0:
			self.item_widgets[0].actived = True
		else:
			print('items_desc=',items_desc,'error')
		self.register_event_type('on_press')
	
	def on_press(self,v=None):
		print('Toggle on_press fired')
		pass

	def select_item(self,o=None):
		for i in self.item_widgets:
			if i!=o:
				i.box_actived = False

		self.dispatch('on_press',o.getValue())

	def getValue(self):
		for i in self.item_widgets:
			if i.actived:
				return i.getValue()
		return None

	def setValue(self,v):
		for i in self.item_widgets:
			if i.getValue() == v:
				i.actived = True
				self.select_item(i)
			else:
				i.actived = False

