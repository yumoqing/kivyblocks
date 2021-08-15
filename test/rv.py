from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivyblocks.utils import CSize
from kivyblocks.widgetExt.scrollwidget import ScrollWidget
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivyblocks.responsivelayout import VResponsiveLayout

class VGridLayout(GridLayout):
	def __init__(self,**kw):
		kwargs = kw.copy()
		if kwargs.get('box_width'):
			del kwargs['box_width']
		if not kwargs.get('cols'):
			kwargs['cols'] = 1
		self.box_width = CSize(kw.get('box_width',0))
		self.options = kw
		super().__init__(**kwargs)
		self.setColsTask = None
	
	def on_size(self,o,s):
		if self.setColsTask is not None:
			self.setColsTask.cancel()
		self.setColsTask = Clock.schedule_once(self.setCols,0.2)

	def setCols(self,t):
		if self.box_width == 0:
			self.box_width = self.width / self.options.get('cols',1)
		else:
			self.cols = int(self.width / self.box_width)

	def setBoxWidth(self,w):
		self.box_width = w

class ResponsiveLayout(ScrollView):
	def __init__(self, cols=2, box_width=15, **options):
		self.options = options
		super().__init__(**options)
		self._inner = VGridLayout(cols=cols,box_width=box_width)

class Box(BoxLayout):
	def __init__(self,**kw):
		super().__init__(**kw)
		self.size_hint = (None, None)
		self.height = CSize(kw.get('height',6))
		self.width = CSize(kw.get('width',8))

class MyApp(App):
	def build(self):
		r = BoxLayout(orientation='vertical')
		s = ResponsiveLayout(box_width=15,size_hint=(1,1))
		b = Button(text='add box', font_size=CSize(2),
					size_hint_y=None,
					height=CSize(2.8)
		)
		r.add_widget(b)
		r.add_widget(s)
		self.l = s
		self.box_cnt = 0
		b.bind(on_press=self.add_box)
		return r

	def add_box(self,o):
		box = Box(width=15)
		t = Label(text='box ' + str(self.box_cnt))
		box.add_widget(t)
		self.l.add_widget(box)
		self.box_cnt += 1

if __name__ == '__main__':
	MyApp().run()

