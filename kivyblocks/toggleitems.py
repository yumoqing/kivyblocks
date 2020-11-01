from functools import partial
from kivy.uix.button import Button, ButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory

from kivyblocks.ready import WidgetReady
from kivyblocks.bgcolorbehavior import BGColorBehavior

class PressableBox(ButtonBehavior, BoxLayout):
	def __init__(self,border_width=1,
				bgcolor=[0,1,0,1],
				selected_color=[1,0,0,1],
				**kw):
		BoxLayout.__init__(self, padding=[border_width,
			border_width,
			border_width,
			border_width],
			**kw)
		ButtonBehavior.__init__(self)
		self.b_bgcolor = bgcolor
		self.border_width = border_width
		self.b_selected_color = selected_color
		self.user_data = None
		self.unselected()

	def on_size(self,o,s):
		if self._selected:
			self.selected()
		else:
			self.unselected()

	def on_press(self,o=None):
		self.selected()

	def set_data(self,d):
		self.user_data = d

	def get_data(self):
		return self.user_data

	def is_selected(self):
		return self._selected

	def selected(self):
		self._selected = True
		with self.canvas.before:
			Color(*self.b_selected_color)
			Rectangle(pos=self.pos,size=self.size)
			Color(*self.b_bgcolor)
			Rectangle(size=(self.width - 2*self.border_width, self.height - 2*self.border_width),
					pos=(int(self.center_x - (self.width - 2*self.border_width)/2.0), int(self.center_y - (self.height - 2*self.border_width)/2.0)))

	def unselected(self):
		self._selected = False
		with self.canvas.before:
			Color(*self.b_bgcolor)
			Rectangle(pos=self.pos,size=self.size)

class ToggleItems(BGColorBehavior, BoxLayout):
	def __init__(self,
				color_level=1,
				items_desc=[],
				border_width=1,
				**kw):
		BoxLayout.__init__(self, **kw)
		BGColorBehavior.__init__(self,color_level=color_level)
		self.item_widgets = []
		for desc in items_desc:
			c = PressableBox(border_width=border_width,
					bgcolor=self.normal_bgcolor,
					selected_color=self.selected_bgcolor
				)
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
			b.widgetBuild(desc,ancestor=self)

		if len(self.item_widgets) > 0:
			self.item_widgets[0].selected()
		else:
			print('items_desc=',items_desc,'error')
		self.register_event_type('on_changed')
	
	def on_changed(self,v=None):
		pass

	def select_item(self,o=None):
		[i.unselected() for i in self.item_widgets if i != o]
		self.dispatch('on_changed',o.get_data())

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
