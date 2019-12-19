import sys
import os
from appPublic.folderUtils import ProgramPath
from appPublic.jsonConfig import getConfig

from kivyblocks.blocksapp import BlocksApp

if __name__ == '__main__':
	pp = ProgramPath()
	workdir = pp
	if len(sys.argv) > 1:
		workdir = sys.argv[1]
	print('ProgramPath=',pp,'workdir=',workdir)

	config = getConfig(workdir,NS={'workdir':workdir,'ProgramPath':pp})
	myapp = BlocksApp()
	myapp.run()
	myapp.workers.running = False
	
