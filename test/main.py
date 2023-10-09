import sys
import os
from appPublic.folderUtils import ProgramPath
from appPublic.jsonConfig import getConfig

from kivyblocks.blocksapp import BlocksApp
from kivyblocks.blocks import Blocks

class TestApp(BlocksApp):
	def build(self):
		b = super(TestApp, self).build()
		widget_desc = {
			"widgettype":"VBox",
			"options":{},
			"subwidgets":[
				{
					"widgettype":"Title1",
					"options":{
						"text":"Say Hello",
						"i18n":True,
						"size_hint_y":None,
						"height":"py::CSize(2)"
					}
				},
				{
					"widgettype":"Text",
					"options":{
						"text":"Hello KivyBlocks"
					}
				}
			]
		}
		blocks = Blocks()
		x = blocks.widgetBuild(widget_desc)
		return x


if __name__ == '__main__':
	pp = ProgramPath()
	workdir = pp
	if len(sys.argv) > 1:
		workdir = sys.argv[1]
	print('ProgramPath=',pp,'workdir=',workdir)

	config = getConfig(workdir,NS={'workdir':workdir,'ProgramPath':pp})
	myapp = TestApp()
	myapp.run()
	
