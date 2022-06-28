from traceback import print_exc
import json
from kivy.properties import StringProperty
from kivy.factory import Factory
from .toolbar import Toolbar
from .baseWidget import VBox, StrInput
from .utils import SUPER, blockImage, CSize
from .clickable import ClickableText

class BlockTest(VBox):
	source_code = StringProperty(None)
	def __init__(self, **kw):
		SUPER(BlockTest, self, kw)
		tb_desc = {
			"img_size_c":2,
			"toolbar_orient":"H",
			"tool_orient":"horizontal",
			"css_on":"default",
			"css_off":"default",
			"tools":[
				{
					"name":"source",
					"source_on":blockImage('source_on.png'),
					"source_off":blockImage('source_off.png'),
					"label":"source code"
				},
				{
					"name":"widget",
					"source_on":blockImage('widget_on.png'),
					"source_off":blockImage('widget_off.png'),
					"label":"Result widget"
				}
			]
		}
		self.toolbar = Toolbar(**tb_desc)
		self.toolbar.bind(on_press=self.tool_pressed)
		self.content = VBox()
		self.source_w = StrInput(multiline=True)
		self.content.add_widget(self.source_w)
		if self.source_code:
			self.source_w.text = self.source_code
		self.add_widget(self.toolbar)
		self.add_widget(self.content)

	def tool_pressed(self, o, v):
		self.content.clear_widgets()
		if v['name'] == 'source':
			print('switch to source code')
			self.content.add_widget(self.source_w)
		else:
			try:
				dic = json.loads(self.source_w.text)
				print(dic, type(dic))
				w = Factory.Blocks().widgetBuild(dic)
				self.content.add_widget(w)
			except Exception as e:
				print_exc()
				print('BlockTest:Exception:',e)

Factory.register('BlockTest', BlockTest)
