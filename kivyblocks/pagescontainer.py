from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App
from .utils import CSize

class PageContainer(FloatLayout):
	def __init__(self,**kw):
		super().__init__(**kw)
		self.show_back = True
		self.pageWidgets = []
		self.backButton = Button(text='<',size_hint=(None,None),
							font_size=CSize(1),
							height=CSize(1.8),width=CSize(1.8))
		self.backButton.bind(on_press=self.previous)
		Window.bind(size=self.on_window_size)
		# self.bind(size=self.reshowBackButton,
		#			on_orientation=self.reshowBackButton)

	def on_window_size(self,o,v=None):
		print('on_window_size event fired ....',Window.size)
		self.size = Window.size
		self.reshowBackButton()

	def reshowBackButton(self,o=None,v=None):
		print(self.size)
		self.showBackButton()

	def hideBack(self):
		if not self.show_back:
			return
		super(PageContainer,self).remove_widget(self.backButton)
		self.show_back = False

	def showBack(self):
		if self.show_back:
			return
		super(PageContainer,self).add_widget(self.backButton)
		self.show_back = True

	def showLastPage(self):
		super(PageContainer,self).clear_widgets()
		if len(self.pageWidgets) < 1:
			return 
		w = self.pageWidgets[-1]
		w.pos = 0,0
		w.size = self.size
		super(PageContainer,self).add_widget(w)
		self.showBackButton()

	def previous(self,v=None):
		if len(self.pageWidgets) <= 1:
			return 
		self.pageWidgets = self.pageWidgets[:-1]
		self.showLastPage()

	def add_widget(self,widget):
		self.pageWidgets.append(widget)
		self.showLastPage()

	def showBackButton(self):
		if len(self.pageWidgets) <= 1:
			return
		print('size event fired .....',self.size)
		super(PageContainer,self).remove_widget(self.backButton)
		self.show_back = False
		self.backButton.pos = (4,self.height - 4 - self.backButton.height)
		self.showBack()


if __name__ == '__main__':
	class Page(Button):
		def __init__(self,container,page_cnt = 1):
			self.container = container
			self.page_cnt = page_cnt
			Button.__init__(self,text = 'page' + str(page_cnt))
			self.bind(on_press=self.newpage)

		def newpage(self,v):
			p = Page(self.container,self.page_cnt + 1)
			self.container.add(p)

	class MyApp(App):
		def build(self):
			x = PageContainer()
			p = Page(x)
			x.add(p)
			return x

	MyApp().run()
