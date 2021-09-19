from kivy.properties import NumericProperty, StringProperty
from kivy.uix.scrollview import ScrollView
from kivy.effects.scroll import ScrollEffect
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory

from kivyblocks.utils import *

class ScrollPanel(ScrollView):
	x_padding_c = NumericProperty(0)
	y_padding_c = NumericProperty(0)
	bg_color = ListProperty(0.2, 0.2, 0.2, 1)
	orient = StringProperty('H')

	def __init__(self,inner=None, **kw):
		super(ScrollPanel,self).__init__()
		self.effect_cls = ScrollEffect
		if not inner:
			kw.update({
				'size_hint':(None,None),
				'bg_color':self.bg_color,
				'orientation':'vertical'
			})
			desc = {
				"widgettype":"Box",
				"options":kw
			}
			self._inner = Factory.Blocks().widgetBuild(desc)
		elif isinstance(inner, Widget):
			self._inner = inner
		else:
			self._inner = Factory.Blocks().widgetBuild(inner)

		if isinstance(self._inner, BoxLayout):
			if self.orient.upper() == 'H':
				self._inner.orientation = 'horizontal'
			else:
				self._inner.orientation = 'vertical'
		self.padding = self.spacing = \
						[CSize(self.x_padding_c), CSize(self.y_padding_c)]

		self._inner.bind(
				minimum_height=self._inner.setter('height'))
		self._inner.bind(
				minimum_width=self._inner.setter('width'))
		super(ScrollPanel,self).add_widget(self._inner)

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
