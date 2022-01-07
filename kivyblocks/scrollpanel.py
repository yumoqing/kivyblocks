from kivy.properties import NumericProperty, StringProperty, \
			OptionProperty, ListProperty
from kivy.uix.scrollview import ScrollView
from kivy.effects.scroll import ScrollEffect
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory

from .utils import *
from .widget_css import WidgetCSS

class ScrollPanel(WidgetCSS, ScrollView):
	orientation = OptionProperty('vertical', \
						options=['vertical', 'horizontal'])
	bgcolor = ListProperty([0.2, 0.2, 0.2, 1])
	padding_c = NumericProperty(1)
	def __init__(self,inner=None, **kw):
		SUPER(ScrollPanel, self, kw)
		self.effect_cls = ScrollEffect
		if not inner:
			self.create_default_inner()
		elif isinstance(inner, Widget):
			self._inner = inner
		else:
			self._inner = Factory.Blocks().widgetBuild(inner)

		super(ScrollPanel,self).add_widget(self._inner)
		self._inner.bind(
				minimum_height=self._inner.setter('height'))
		self._inner.bind(
				minimum_width=self._inner.setter('width'))

	def get_subwidgets(self):
		return self._inner.children

	def create_default_inner(self):
		kw = {
			'size_hint':(None,None),
			'orientation':self.orientation
		}
		desc = {
			"widgettype":"Box",
			"options":kw
		}
		self._inner = Factory.Blocks().widgetBuild(desc)
		self._inner.bgcolor = self.bgcolor
		if not self._inner:
			print('desc=', desc)
			raise Exception('widget build failed')
		self._inner.spacing = CSize(self.padding_c)

	def add_widget(self,widget,**kw):
		a = self._inner.add_widget(widget,**kw)
		return a

	def clear_widgets(self,**kw):
		a = self._inner.clear_widgets(**kw)

	def remove_widget(self,widget,**kw):
		a = self._inner.remove_widget(widget,**kw)
		return a

if __name__ == '__main__':
	from kivy.app import App
	from kivy.uix.label import Label
	from kivy.uix.button import Button
	import codecs
	
	class MyApp(App):
		def build(self):
			root = ScrollPanel(size=(400,400),
					pos_hint={'center_x': .5, 'center_y': .5}
			)
			with codecs.open(__file__,'r','utf-8') as f:
				txt = f.read()
				lines = txt.split('\n')
				for l in lines:
					root.add_widget(Label(text=l,color=(1,1,1,1),size_hint=(None,None),size=(1200,40)))
			return root

	MyApp().run()
