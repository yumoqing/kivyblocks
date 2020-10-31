from functools import partial
from kivy.uix.button import Button, ButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory

from kivyblocks.ready import WidgetReady

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

class ToggleItems(BoxLayout):
	def __init__(self,
				items_desc=[],
				border_width=1,
				bgcolor=[1,0,0,1],
				selected_color=[1,0,0,1],
				**kw):
		BoxLayout.__init__(self, **kw)
		self.item_widgets = []
		for desc in items_desc:
			c = PressableBox(border_width=border_width,
					bgcolor=bgcolor,
					selected_color=selected_color
				)
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
			if desc.get('data'):
				c.set_data(desc.get('data'))

		self.selected = None
	
	def select_item(self,o=None):
		[i.unselected() for i in self.item_widgets if i != o]

	def getValue(self):
		for i in self.item_widgets:
			if i.is_selected():
				return i.getValue()
		return None

Factory.register('PressableBox',PressableBox)
Factory.register('ToggleItems',ToggleItems)
