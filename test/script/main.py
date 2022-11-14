from kivyblocks.setconfig import config_set
from kivyblocks.blocksapp import BlocksApp
from kivyblocks.blocks import registerWidget, Blocks
from kivyblocks.i18n import I18n
import kivyblocks.register
from kivyblocks.script import set_script_env

class ScriptApp(BlocksApp):
	pass

if __name__ == '__main__':
	set_script_env('userid', 'testuser')
	i18n = I18n()
	ScriptApp().run()
