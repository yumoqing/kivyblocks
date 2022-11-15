
from kivyblocks import setconfig
from kivy.app import App

from kivy.factory import Factory
from kivyblocks import register 
from kivyblocks.blocks import Blocks

class TestApp(App):
	def build(self):
		desc = {
			"widgettype":"VBox",
			"options":{
				"TouchRippleButtonBehavior":{}
			},
			"subwidgets":[
				{
					"widgettype":"Text",
					"options":{
						"text":"Hello"
					}
				}
			]
		}
		blocks = Blocks()
		x = blocks.widgetBuild(desc)
		x.bind(on_press=self.haha)
		print(dir(x))
		return x

	def haha(self, *args):
		print('eeeeeeeeeeeeeeeeeeee')

if __name__ == '__main__':
	TestApp().run()
