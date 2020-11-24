import os
import sys
from functools import partial
from kivyblocks.dg import DataGrid
from kivy.app import App
from kivy.clock import Clock
from appPublic.folderUtils import ProgramPath
from appPublic.jsonConfig import getConfig
from appPublic.timecost import TimeCost
from kivyblocks.blocksapp import appBlocksHack

if __name__ == '__main__':
	pp = ProgramPath()
	workdir = pp
	if len(sys.argv) > 1:
		workdir = sys.argv[1]
	print('ProgramPath=',pp,'workdir=',workdir)

	config = getConfig(workdir,NS={'workdir':workdir,'ProgramPath':pp})

	desc = {
        "id":"playlist_grid",
        "widgettype":"DataGrid",
        "options":{
                "dataloader":{
                        "dataurl":"http://ktv.bsppo.com:10081/ktvplayer/playlist.dspy",
                        "params":{}
                },
                "fields":[
                        {
                                "name":"plid",
                                "label":"plid",
                                "uitype":"str"
                        },
                        {
                                "name":"userid",
                                "label":"Userid",
                                "uitype":"str"
                        },
                        {
                                "name":"plname",
                                "label":"plname",
                                "uitype":"str"
                        },
                        {
                                "name":"max_position",
                                "label":"max_position",
                                "uitype":"long"
                        }
                ]
        }
	}

	class MyApp(App):
		def build(self):
			with TimeCost('create widget') as tc:
				dg = DataGrid(**desc['options'])
				dg.loadData()
				return dg

		def on_close(self,*args,**kwargs):
			return True

	myapp = MyApp()
	appBlocksHack(myapp)
	myapp.run()
	tc = TimeCost('show')
	tc.show()

