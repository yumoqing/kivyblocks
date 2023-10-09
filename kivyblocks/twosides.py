from kivy.clock import Clock
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.image import AsyncImage

from kivyblocks.utils import CSize
from kivyblocks.ready import WidgetReady

class TwoSides(WidgetReady, BoxLayout):
	panel_shape = StringProperty('landscape')
	cannt_rotation = BooleanProperty(True)
	def __init__(self,switch_image=None, 
						landscape={},
						portrait={},
						**kw):
		BoxLayout.__init__(self,**kw)
		WidgetReady.__init__(self)
		blocks = Factory.Blocks()
		self.switch_image = switch_image
		self.portrait_modal = None

		self.landscape_widget = blocks.widgetBuild(landscape)
		blocks = Factory.Blocks()
		self.portrait_widget = blocks.widgetBuild(portrait)
		self.switch_button = None
		self.switch_button_showed = False
		if self.switch_image:
			self.build_switch_image()
		self.on_size_task = None
		self.ready_task = None
		self.register_event_type('on_interactive')
		self.register_event_type('on_beforeswitch_landscape')
		self.register_event_type('on_afterswitch_landscape')
		self.register_event_type('on_beforeswitch_portrait')
		self.register_event_type('on_afterswitch_portrait')
		self.bind(fullscreen=self.show_switch_image)
		self.app = App.get_running_app()

	def set_switch_button_pos(self):
		h = self.switch_button.height
		self.switch_button.pos = (4, self.height - h - 4)

	def show_switch_image(self, o, v=None):
		def show(*args):
			if self.switch_image and self.width > self.height:
				if self.switch_button in Window.children:
					Window.remove_widget(self.switch_button)
				self.set_switch_button_pos()
				Window.add_widget(self.switch_button)
				self.switch_button_showed = True

		print('show switch_buuton ....')
		if self.fullscreen:
			Clock.schedule_once(show, 2)

	def build_switch_image(self):
		button = Factory.Blocks().widgetBuild({
			"widgettype":"PressableBox",
			"options":{
				"size_hint":(None, None),
				"size":CSize(4,4)
			},
			"subwidgets":[
				{
					"widgettype":"AsyncImage",
					"options":{
						"source":self.switch_image
					}
				}
			]
		})
		button.bind(on_press=self.switch_portrait_widget)
		self.switch_button = button

	def switch_portrait_widget(self, *args):
		def clear_modal(o, *args):
			o.clear_widgets()

		if not self.fullscreen:
			self.fullscreen = True
			return

		if not self.portrait_modal:
			y = self.height - CSize(4)
			x = self.height * y / self.width
			w = Factory.Blocks().widgetBuild({
					"widgettype":"Modal",
					"options":{
						"auto_open":False,
						"auto_dismiss":True,
						"size_hint":[None,None],
						"size":(x,y),
						"pos":((self.width - x) / 2, 0)
					}
				})
			w.bind(on_dismiss=clear_modal)
			self.portrait_modal = w
		
		if self.portrait_widget.parent:
			self.portrait_widget.parent.remove_widget(self.portrait_widget)
		self.portrait_modal.clear_widgets()
		self.portrait_modal.add_widget(self.portrait_widget)
		self.portrait_modal.open()

	def on_size(self,*args):
		if self.width >= self.height:
			if not self.landscape_widget in self.children or \
					self.panel_shape == 'portrait':
				self.dispatch('on_beforeswitch_landscape')
				self.clear_widgets()
				self.add_widget(self.landscape_widget)
				self.dispatch('on_afterswitch_landscape')
			if self.switch_button_showed and self.cannt_rotation:
				if self.switch_button in Window.children:
					Window.remove_widget(self.switch_button)
				self.set_switch_button_pos()
				Window.add_widget(self.switch_button)
			self.panel_shape = 'landscape'
		else:
			if self.portrait_widget in self.children or \
					self.panel_shape == 'landscape':
				self.dispatch('on_beforeswitch_portrait')
				self.clear_widgets()
				self.add_widget(self.portrait_widget)
				self.dispatch('on_afterswitch_portrait')
				self.dispatch('on_interactive')
			if self.switch_button in Window.children:
				Window.remove_widget(self.switch_button)
			self.cannt_rotation = False
			self.panel_shape = 'portrait'

	def on_beforeswitch_landscape(self, *args):
		pass

	def on_afterswitch_landscape(self, *args):
		pass

	def on_beforeswitch_portrait(self, *args):
		pass

	def on_afterswitch_portrait(self, *args):
		pass

	def on_interactive(self, *args):
		pass


