from kivy.app import App
from kivy.core.window import Window
from kivy.uix.popup import Popup
from appPublic.Singleton import SingletonDecorator
from appPublic.registerfunction import RegisterFunction
from appPublic.rsa import RSA
# from .form import Form

class ServerInfo:
	def __init__(self):
		self.rsaEngine = RSA()
		config = getConfig()
		url = '%s%s' % (config.uihome, config.publickey_url)
		hc = App.get_running_app().hc
		d = hc.get(url)
		self.publickey = self.rsaEngine. publickeyFromText(d)
	
	def encode(self,uinfo):
		if uinfo['authmethod'] == 'password':
			authinfo = '%s::%s::%s' % (uinfo['authmethod'], uinfo['userid'], uinfo['password'])
			txt = self.serverinfo.encode(authinfo)
			x = self.rsaEngine.encode(self.publickey, txt)
			return x
		return None

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
		super().__init__(size_hint=(0.8,0.8))
		
		app = App.get_running_app()
		print('here ..1............')
		self.content = app.blocks.widgetBuild(logformdesc)
		# self.content.bind(on_submit=setipUserInfo)
		print('here ..2............',self.content)
		self.title = 'login'
		self.blockCalls = []
		self.open_status = False
		print('here ..3............')
		self.content.bind(on_submit=self.on_submit)
		self.content.bind(on_cancel=self.on_submit)
		print('here ..4............')
		self.open()
		
	def close(self):
		self.open_status = False
		self.dismiss()

	def on_submit(self,o,v):
		self.dismiss()
	
	def on_cancel(self,o,v):
		self.dismiss()

def setupUserInfo(obj, userinfo):
	app = App.get_running_app()
	if not hasattr(app, 'serverinfo'):
		app.serverinfo = ServerInfo()

	if userinfo.get('password',False):
		userinfo['authmethod'] = 'password'
	authinfo = app.serverinfo.encode(userinfo)
	headers = {
		"authorization":authinfo
	}
	login_url = '%s%s' % (app.config.uihome, app.config.login_url)
	app.hc.get(login_url,headers=headers)

rf = RegisterFunction()
rf.register('setupUserInfo',setupUserInfo)

