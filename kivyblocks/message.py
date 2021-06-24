
from kivy.factory import Factory
from kivy.uix.image import AsyncImage
from .utils import *
from .baseWidget import Modal, Text, HBox,VBox
from .toggleitems import PressableBox

class Conform(Modal):
	def __init__(self, title_icon=None, 
						title = None,
						message = None,
						conform_icon=None,
						cancel_icon=None, 
						**kw):
		Modal.__init__(self, **kw)
		self.register_event_type('on_cancel')
		self.register_event_type('on_conform')
		self.auto_dismiss = False
		b = VBox()
		b1 = HBox(size_hint_y=None, height=CSize(1.4))
		b1.add_widget(AsyncImage(source=title_icon or \
									blockImage('question.png'),
									size_hint=[None,None],
									height=CSize(1.2),
									width=CSize(1.2)))
		b1.add_widget(Text(text=title or 'Conform',
									font_size=CSize(1.2),
									i18n=True,
									wrap=True,
									halign='left',
									valign='center',
									))
		b.add_widget(b1)
		b2 = HBox()
		
		b2.add_widget(Text(text=message or 'Please conform',
									wrap=True,
									halign='left',
									size_hint=(1,1),
									font_size=CSize(1)))
		b.add_widget(b2)
		b3 = HBox(size_hint_y=None, height=CSize(2))
		w_cancel = PressableBox()
		blocks = Factory.Blocks()
		w_cancel.add_widget(blocks.widgetBuild({
			"widgettype":"HBox",
			"options":{},
			"subwidgets":[
				{
					"widgettype":"AsyncImage",
					"options":{
						"source":cancel_icon or blockImage('cancel.png'),
									"size_hint":[None,None],
									"height":CSize(1),
									"width":CSize(1)
					}
				},
				{
					"widgettype":"Text",
					"options":{
						"text":'Cancel',
						"wrap":True,
						"font_size":CSize(1),
						"halign":'left',
						"i18n":True
					}
				}
			]
		}))
		w_conform = PressableBox()
		blocks = Factory.Blocks()
		w_conform.add_widget(blocks.widgetBuild({
			"widgettype":"HBox",
			"options":{},
			"subwidgets":[
				{
					"widgettype":"AsyncImage",
					"options":{
						"source":conform_icon or blockImage('conform.png'),
									"size_hint":[None,None],
									"height":CSize(1),
									"width":CSize(1)
					}
				},
				{
					"widgettype":"Text",
					"options":{
						"text":'Conform',
						"wrap":True,
						"font_size":CSize(1),
						"halign":'left',
						"i18n":True
					}
				}
			]
		}))

		w_cancel.bind(on_press=self.cancel_press)
		w_conform.bind(on_press=self.conform_press)

		b3.add_widget(w_cancel)
		b3.add_widget(w_conform)
		b.add_widget(b3)
		self.add_widget(b)

	def cancel_press(self,o, v=None):
		self.dispatch('on_cancel')

	def conform_press(self, o, v=None):
		self.dispatch('on_conform')

	def on_cancel(self):
		self.dismiss()

	def on_conform(self):
		self.dismiss()


