from kivy.uix.scrollview import ScrollView
from kivy.effects.scroll import ScrollEffect
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse,Rectangle

class ScrollWidget(ScrollView):
	def __init__(self,**kw):
		super(ScrollWidget,self).__init__()
		self.effect_cls = ScrollEffect
		self.sized_widgets = []
		kw.update({
			'size_hint':(None,None),
			'orientation':'vertical'
		})
		self._inner = BoxLayout(**kw)
		self._inner.bind(
				minimum_height=self._inner.setter('height'))
		self._inner.bind(
				minimum_width=self._inner.setter('width'))
		super(ScrollWidget,self).add_widget(self._inner)
		self.bind(size=self.change_all_sized_widgets)

	def change_all_sized_widgets(self, *args):
		for w in self.sized_widgets:
			self.change_widget_width(w)
		self._inner.do_layout()

	def change_widget_width(self, w):
		w.size_hint_x = None
		w.width = self.width * w.org_size_hint_x

	def add_widget(self,widget,**kw):
		if widget.size_hint_x:
			widget.org_size_hint_x = widget.size_hint_x
			self.change_widget_width(widget)
			self.sized_widgets.append(widget)
		a = self._inner.add_widget(widget,**kw)
		return a

	def clear_widgets(self,**kw):
		self.sized_widgets = []
		a = self._inner.clear_widgets(**kw)

	def remove_widget(self,widget,**kw):
		self.sized_widgets = [i for i in self.sized_widgets if i != widget]
		a = self._inner.remove_widget(widget,**kw)
		return a

if __name__ == '__main__':
	from kivy.app import App
	from kivy.uix.label import Label
	from kivy.uix.button import Button
	import codecs
	
	class MyApp(App):
		def build(self):
			root = ScrollWidget(size=(400,400),
					pos_hint={'center_x': .5, 'center_y': .5}
			)
			with codecs.open(__file__,'r','utf-8') as f:
				txt = f.read()
				lines = txt.split('\n')
				for l in lines:
					root.add_widget(Label(text=l,color=(1,1,1,1),size_hint=(None,None),size=(1200,40)))
			return root

	MyApp().run()
