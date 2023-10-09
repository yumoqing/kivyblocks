from traceback import print_exc
from kivy.logger import Logger
from kivy.factory import Factory
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.popup import Popup
from appPublic.Singleton import SingletonDecorator
from appPublic.jsonConfig import getConfig
from appPublic.registerfunction import RegisterFunction
logformdesc = {
	"widgettype":"Form",
	"options":{
		"cols":1,
		"labelwidth":0.4,
		"textsize":1,
		"inputheight":4,
		"fields":[
			{
				"name":"userid",
				"label":"user name",
				"datatype":"str",
				"required":True,
				"uitype":"string"
			},
			{
				"name":"passwd",
				"label":"Password",
				"datatype":"str",
				"uitype":"password"
			}
		]
	}
}

@SingletonDecorator
class LoginForm(Popup):
	def __init__(self):
		super().__init__(size_hint=(0.8,0.8))
		self.title = 'login'
		self.buildContent(None,None)
		self.register_event_type('on_setupuser')
	
	def on_setupuser(self,o=None):
		return

	def buildContent(self,o,size):
		self.content = Factory.Form(**logformdesc['options'])
		self.content.bind(on_submit=self.on_submit)
		
	def on_submit(self,o,userinfo):
		print('login(),on_submit fired ....')
		self.dismiss()
		print('userinfo=',userinfo)
		app = App.get_running_app()

		if userinfo.get('passwd',False):
			userinfo['authmethod'] = 'password'
		authinfo = app.serverinfo.encode(userinfo)
		self.dispatch('on_setupuser')
	
	def on_cancel(self,o,v):
		print('login() on_cancel fired .....')
		self.dismiss()


