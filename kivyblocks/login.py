from kivy.app import App
from kivy.uix.popup import Popup
from appPublic.Singleton import SingletonDecorator
from appPublic.registerfunction import RegisterFunction

logformdesc = {
	"widgettype":"Form",
	"options":{
		"cols":1,
		"labelwidth":0.3,
		"textsize":1,
		"inputheight":3,
		"fields":[
			{
				"name":"userid",
				"label":"user name",
				"datatype":"str",
				"uitype":"string"
			},
			{
				"name":"passwd",
				"label":"Password",
				"datatype":"str",
				"uitype":"password"
			}
		]
	},
	"binds":[
		{
			"wid":"self",
			"event":"on_submit",
			"datawidegt":"self",
			"actiontype":"registedfunction",
			"rfname":"setupUserInfo"
		}
	]
}

@SingletonDecorator
class LoginForm(Popup):
	def __init__(self):
		super().__init__()
		app = App.get_running_app()
		self.content = app.blocks.widgetBuild(logformdesc)
		self.title = 'login'
		self.blockCalls = []
		self.open_status = False
		self.content.bind(on_submit=self.on_submit)
		
	def needlogin(self, url,method,params,headers,callback=None,errback=None):
		self.blockCalls.append([url, method, params,headers,callback,errback])
		if self.open_status:
			return
		self.open_status = True
		self.open()
	
	def recall(self):
		app = App.get_running_app()
		for url, method, params, headers,callback, errback in self.blockCalls:
			app.hc(url, method=pethod,params=params,headers=headers,
						callback=callback,errback=errback)

	def close(self):
		self.open_status = False
		self.dismiss()

	def on_submit(self,o,v):
		self.dismiss()

def setupUserInfo(userinfo):
	app = App.get_running_app()
	app.setUserInfo(userinfo)
	lf = LoginForm()
	lf.recall()

rf = RegisterFunction()
rf.register('setupUserInfo',setupUserInfo)

