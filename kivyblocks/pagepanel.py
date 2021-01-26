
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.factory import Factory
from .baseWidget import VBox, HBox
from .toggleitems import PressableBox
from .utils import *

class MenuContainer(VBox):
	def __init__(self, **kw):
		VBox.__init__(self, **kw)
		self.bind(on_touch_down=self.check_press)

	def open(self):
		if self in Window.children:
			Window.remove_widget(self)
		Window.add_widget(self)

	def dismiss(self, *args):
		self.clear_widgets()
		Window.remove_widget(self)

	def check_press(self, o, touch):
		if touch.is_mouse_scrolling:
			return False
		if not self.collide_point(touch.x, touch.y):
			self.dismiss()
			return True
		return False

class PagePanel(VBox):
	def __init__(self, bar_size=2, bar_at='top', enable_on_close=False, 
					left_menu=False, **kw):
		print('PagePanel().__init__():', bar_size, bar_at, left_menu)
		self.bar_size = bar_size
		self.bar_at = bar_at
		
		self.enable_on_close = enable_on_close
		if self.enable_on_close:
			app = App.get_running_app()
			app.bind(on_close=self.on_close_handle)

		if not left_menu:
			self.left_menu = None
		elif isinstance(left_menu, Widget):
			self.left_menu = left_menu
		else:
			print('left_menu=', left_menu, type(left_menu))
			self.left_menu = Factory.Blocks().widgetBuild(left_menu)
		self.sub_widgets = []
		VBox.__init__(self, **kw)
		self.bar = HBox(size_hint_y=None,
						spacing=CSize(bar_size/6),
						height=CSize(bar_size))
		bcsize = bar_size * 0.85
		self.content = VBox()
		self.bar_back = VBox(size_hint=(None,None),size=CSize(bcsize,bcsize))
		self.bar_back_w = Factory.Blocks().widgetBuild({
			"widgettype":"PressableBox",
			"options":{
				"size":CSize(bcsize,bcsize),
				"size_hint":[None, None]
			},
			"subwidgets":[
				{
					"widgettype":"AsyncImage",
					"options":{
						"source":blockImage('backword.png')
					}
				}
			]
		})
		self.bar_back_w.bind(on_press=self.pop)
		self.bar.add_widget(self.bar_back)
		if self.left_menu:
			self.bar_left_menu = Factory.Blocks().widgetBuild({
				"widgettype":"PressableBox",
				"options":{
					"size_hint":(None,None), 
					"size":CSize(bcsize,bcsize)
				},
				"subwidgets":[
					{
						"widgettype":"AsyncImage",
						"options":{
							"source":blockImage('menu.png')
						}
					}
				]
			})
			self.bar.add_widget(self.bar_left_menu)
			self.bar_left_menu.bind(on_press=self.show_left_menu)
		self.bar_title = HBox()
		self.bar.add_widget(self.bar_title)
		self.bar_right_menu = VBox(size_hint=(None,None),size=CSize(bcsize,bcsize))
		self.bar_right_menu_w = Factory.Blocks().widgetBuild({
			"widgettype":"PressableBox",
			"options":{
				"size_hint":(None,None), 
				"size":CSize(bcsize,bcsize)
			},
			"subwidgets":[
				{
					"widgettype":"AsyncImage",
					"options":{
						"source":blockImage('right_menu.png')
					}
				}
			]
		})
		self.bar.add_widget(self.bar_right_menu)
		self.bar_right_menu_w.bind(on_press=self.show_right_menu)

		if bar_at == 'top':
			super().add_widget(self.bar)
			super().add_widget(self.content)
		else:
			super().add_widget(self.content)
			super().add_widget(self.bar)
		self.menu_container = MenuContainer()

	def on_close_handle(self, o, *args):
		print('app.on_close fired, ...')
		if not self.enable_on_close:
			return True
		self.pop(None)
		if len(self.sub_widgets) > 1:
			return False
		return True

	def pop(self, o, *args):
		self.bar_back.clear_widgets()
		self.content.clear_widgets()
		self.bar_title.clear_widgets()
		self.bar_right_menu.clear_widgets()
		if len(self.sub_widgets) < 1:
			return
		diss_w = self.sub_widgets[-1]
		self.sub_widgets = self.sub_widgets[:-1]
		self.show_currentpage()

	def show_currentpage(self):
		w = self.sub_widgets[-1]
		if len(self.sub_widgets) > 1:
			self.bar_back.add_widget(self.bar_back_w)
		self.content.add_widget(w)
		if hasattr(w, 'title_widget'):
			self.bar_title.add_widget(w.title_widget)
		if hasattr(w, 'menu_widget'):
			self.bar_right_menu.add_widget(self.bar_right_menu_w)

	def clear_widgets(self):
		self.bar_back.clear_widgets()
		self.content.clear_widgets()
		self.bar_title.clear_widgets()
		self.bar_right_menu.clear_widgets()

	def add_widget(self, w,*args):
		if len(self.sub_widgets) > 0:
			pass
		self.sub_widgets.append(w)
		self.show_currentpage()

	def show_left_menu(self, o):
		print('left_menu fired')
		if len(self.sub_widgets) < 1:
			return
		mc = MenuContainer()
		mc.add_widget(self.left_menu)
		mc.size_hint_x = 0.4
		mc.size_hint_y = 1
		mc.x = self.x
		mc.y = self.y
		mc.open()

	def show_right_menu(self, o):
		print('right fired')
		if len(self.sub_widgets) < 1:
			return
		w = self.sub_widgets[-1]
		if not hasattr(w, 'menu_widget'):
			return True
		mc = MenuContainer()
		mc.add_widget(w.menu_widget)
		mc.size_hint_x = 0.4
		mc.size_hint_y = 1
		mc.x = self.x + self.width * 0.6
		mc.y = self.y
		mc.open()
		
