
from kivy.uix.scrollview import ScrollView
from kivy.effects.scroll import ScrollEffect
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory

class ScrollPanel(ScrollView):
	def __init__(self,inner=None, **kw):
		print('ScrollPanel(): kw=', kw)
		super(ScrollPanel,self).__init__()
		self.effect_cls = ScrollEffect
		if not inner:
			kw.update({
				'size_hint':(None,None),
				'orientation':'vertical'
			})
			self._inner = BoxLayout(**kw)
		elif isinstance(inner, Widget):
			self._inner = inner
		else:
			self._inner = Factory.Blocks().widgetBuild(inner)

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
