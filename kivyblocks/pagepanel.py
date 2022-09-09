
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.utils import platform
from .baseWidget import VBox, HBox
from .toggleitems import PressableBox
from .utils import *
from .swipebehavior import SwipeBehavior

class PageContent(SwipeBehavior, VBox):
	def __init__(self, **kw):
		VBox.__init__(self, **kw)
		SwipeBehavior.__init__(self)

class MenuContainer(VBox):
	def __init__(self, **kw):
		VBox.__init__(self, **kw)
		self.bind(on_touch_down=self.check_press)
		self.register_event_type('on_dismiss')

	def on_dismiss(self, *args):
		print('on_dismiss fire')

	def open(self):
		if self in Window.children:
			Window.remove_widget(self)
		Window.add_widget(self)

	def dismiss(self, *args):
		self.clear_widgets()
		Window.remove_widget(self)
		self.dispatch('on_dismiss')

	def check_press(self, o, touch):
		if touch.is_mouse_scrolling:
			return False
		if not self.collide_point(touch.x, touch.y):
			self.dismiss()
			return True
		return False

class PagePanel(VBox):
	"""
# PagePanel widget
PagePanel widget provide a control bar and a subwidget container, control bar and content layout using vertical layout.

in control bar, there is a optional left menu icon, page title, right menu icon, and if there is more than one subwidgets add in the PagePanel, it will show the sub-widget last added. and a backward icon will show in the leftest control bar.

* backward icon uses to show the previous page in the PagePanel.
* left menu icon uses to show the system wide's menu
* right menu icon uses to show the current page's menu, the widget is identified by "menu_widget" in sub-widget description file
* title to show current page title, the widget is identified by "title_widget" in sub-widget description file.

## Description file format
PagePanel description file format
```
	{
		"bar_autohide": true when page is idle
		"bar_size": bar size in CSize unit
		"bar_at": "top" or "bottom"
		"bar_css":
		"panel_css":
		"left_menu": if defined, it must be a widget instance or a dict 
					recognized by Blocks

		other VBox initial options
	}
	usage examples:
	{
		"widgettype":"PagePanel",
		"options":{
			"bar_size":2,
			"enable_on_close":true,
			"left_menu":{
				"widgettype":"Text",
				"options":{
					"text":"Text"
				}
			},
			"radius":[10,10,10,10]
		},
		"subwidgets":[
			{
				"widgettype":"urlwidget",
				"options":{
					"url":"{{entire_url('page.ui')}}"
				}
			}
		]
	}
```

sub-widget's description file format
```
	and page.ui is:
	{
		"widgettype":"Button",
		"options":{
			"text":"button {{cnt or 0}}"
		},

		"title_widget":{
			"widgettype":"Text",
			"options":{
				"text":"test title"
			}
		},
		"menu_widget":{
			"widgettype":"Text",
			"options":{
				"text":"TTTT"
			}
		},
		"binds":[
			{
				"wid":"self",
				"target":"root",
				"actiontype":"urlwidget",
				"event":"on_press",
				"options":{
					"params":{
						"cnt":{{int(cnt or 0) + 1}}
					},
					"url":"{{entire_url('page.ui')}}"
				}
			}
		]
	}
```

## 

	"""
	def __init__(self, bar_size=2, 
					bar_css='default',
					csscls='default',
					singlepage=False,
					fixed_before=None,
					bar_autohide=False,
					fixed_after=None,
					bar_at='top', 
					enable_on_close=False, 
					left_menu=None, **kw):
		self.bar_size = bar_size
		self.bar_autohide = bar_autohide
		self.bar_at = bar_at
		self.singlepage = singlepage
		self.idle_status = False
		self.idle_threshold = 10
		self.bar_show = True
		self.idle_task = None
		self.swipe_buffer = []
		self.swipe_right = False
		self.fixed_before = None
		if fixed_before:
			self.fixed_before = Factory.Blocks().widgetBuild(fixed_before)
		self.fixed_after = None
		if fixed_after:
			self.fixed_after = Factory.Blocks().widgetBuild(fixed_after)
		
		self.enable_on_close = enable_on_close
		if self.enable_on_close:
			app = App.get_running_app()
			app.bind(on_close=self.on_close_handle)

		if not left_menu:
			self.left_menu = None
		elif isinstance(left_menu, Widget):
			self.left_menu = left_menu
		else:
			self.left_menu = Factory.Blocks().widgetBuild(left_menu)
		self.sub_widgets = []
		VBox.__init__(self, **kw)
		self.bar = HBox(size_hint_y=None,
						csscls=bar_css,
						spacing=CSize(bar_size/6),
						height=CSize(bar_size))
		bcsize = bar_size * 0.85
		self.content = PageContent()
		self.content.bind(on_swipe_left=self.on_swipe_next_page)
		self.content.bind(on_swipe_right=self.pop)
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
		self.bar_title = HBox(csscls=bar_css)
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
		self.construct()
		if self.bar_autohide:
			Window.bind(on_touch_down=self.set_normal_bar)
			self.idle_task = Clock.schedule_once(self.set_idle_bar, \
													self.idle_threshold)

	def set_idle_bar(self, *args):
		if not self.bar_show:
			return
		try:
			self.bar_pos = self.children.index(self.bar)
			print('self.bar_pos=', self.bar_pos, '......................')
			super().remove_widget(self.bar)
			if platform in ['win', 'macosx','linux']:
				Window.borderless = True
		except:
			pass
		self.bar_show = False

	def set_normal_bar(self, *args):
		if self.idle_task:
			self.idle_task.cancel()
		self.idle_task = Clock.schedule_once(self.set_idle_bar, \
													self.idle_threshold)
		if self.bar_show:
			return
		super().add_widget(self.bar, index=self.bar_pos)
		if platform in ['win', 'macosx','linux']:
			Window.borderless = False
		self.bar_show = True

	def construct(self):
		self.clear_widgets()
		if self.bar_show and self.bar_at == 'top':
			super().add_widget(self.bar)
		if self.fixed_before:
			super().add_widget(self.fixed_before)
		super().add_widget(self.content)
		if self.fixed_after:
			super().add_widget(self.fixed_after)
		if self.bar_show and self.bar_at != 'top':
			super().add_widget(self.bar)
		self.left_menu_showed = False
		self.right_menu_showed = False

	def get_subwidgets(self):
		children = [self.bar]
		if self.fixed_before:
			children.append(self.fixed_before)
		if self.fixed_after:
			children.append(self.fixed_after)
		return children + self.sub_widgets

	def on_close_handle(self, o, *args):
		print('app.on_close fired, ...')
		if not self.enable_on_close:
			return True
		self.pop(None)
		if len(self.sub_widgets) > 1:
			return False
		return True

	def pop(self, o, *args):
		if len(self.sub_widgets) < 2:
			return
		self.clear_widgets()
		diss_w = self.sub_widgets[-1]
		self.swipe_buffer.insert(0,diss_w)
		self.sub_widgets = self.sub_widgets[:-1]
		self.show_currentpage()

	def set_title(self, w):
		self.bar_title.clear_widgets()
		self.bar_title.add_widget(w)

	def set_right_menu(self, w):
		self.bar_right_menu.clear_widgets()
		self.bar_right_menu.add_widget(w)

	def show_currentpage(self):
		w = self.sub_widgets[-1]
		if len(self.sub_widgets) > 1:
			self.bar_back.add_widget(self.bar_back_w)
		self.content.add_widget(w)
		if hasattr(w, 'title_widget'):
			self.set_title(w.title_widget)
		if hasattr(w, 'menu_widget'):
			self.set_right_menu(self.bar_right_menu_w)

	def on_swipe_next_page(self, o, *args):
		if len(self.swipe_buffer) < 1:
			return True
		self.swipe_right = True
		w = self.swipe_buffer[0]
		del self.swipe_buffer[0]
		self.add_widget(w)
		return True

	def clear_widgets(self):
		self.bar_back.clear_widgets()
		self.content.clear_widgets()
		self.bar_right_menu.clear_widgets()

	def add_widget(self, w, *args):
		print('here ....')
		if not self.swipe_right:
			self.swipe_buffer = []
		self.swipe_right = False
		self.clear_widgets()
		if self.singlepage:
			self.sub_widgets = []
		self.sub_widgets.append(w)
		self.show_currentpage()

	def show_left_menu(self, o):
		def x(*args):
			self.left_menu_showed = False
			print('dismiss fired, left_menu_showed=',self.left_menu_showed)

		print('left_menu fired')
		if len(self.sub_widgets) < 1:
			return
		if self.left_menu_showed:
			return
		mc = MenuContainer()
		mc.add_widget(self.left_menu)
		self.left_menu.bind(on_press=mc.dismiss)
		mc.size_hint = (None, None)
		mc.width = self.width * 0.4
		mc.height = self.content.height
		mc.x = self.x
		mc.y = self.y if self.bar_at=='top' else self.content.y
		self.left_menu_showed = True
		mc.bind(on_dismiss=x)
		mc.open()

	def show_right_menu(self, o):
		def x(*args):
			self.right_menu_showed = False
			print('dismiss fired, right_menu_showed=',self.right_menu_showed)

		print('right menu fired')
		if len(self.sub_widgets) < 1:
			print('no sub_widgets')
			return
		if self.right_menu_showed:
			print('right menu showed, not thing done')
			return

		w = self.sub_widgets[-1]
		if not hasattr(w, 'menu_widget'):
			print('this sub widget has not menu_widget')
			return True
		mc = MenuContainer()
		mc.add_widget(w.menu_widget)
		w.menu_widget.bind(on_press=mc.dismiss)
		mc.size_hint = (None,None)
		mc.height = self.content.height
		mc.width = self.width * 0.4
		mc.x = self.x + self.width * 0.6
		mc.y = self.y if self.bar_at == 'top' else self.content.y
		self.right_menu_showed = True
		mc.bind(on_dismiss=x)
		mc.open()
		
