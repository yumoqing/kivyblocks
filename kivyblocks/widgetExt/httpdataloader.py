import sys
sys.path.append('..')
sys.path.append('.')
import time

class HttpDataLoader(DataLoader):
	def __init__(self):
		super(HttpDataLoader,self).__init__()
		self.hc = HttpClient()
		
	async def loadData(self,url,method='GET',params={},headers={}):
		try:
			resp = None
			if method=='GET':
				resp = await self.hc.get(url,params=params,headers=headers)
			else:
				resp = await self.hc.post(url,data=params,headers=headers)
				return resp
		except Exception as e:
			print('loadData(%s) Error ' % url,e)
			self.loadError(e)

if __name__ == '__main__':
	import sys
	from async_app import AsyncApp, wait_coro
	from kivy.uix.boxlayout import BoxLayout
	from kivy.uix.button import Button
	from kivy.uix.textinput import TextInput
	class MyApp(AsyncApp):
		def build(self):
			root = BoxLayout(orientation='vertical')
			btn = Button(text='get Remote data',size_hint_y=None,height=44)
			btn.bind(on_release=self.getData)
			root.add_widget(btn)
			self.txt = TextInput(multiline=True,readonly=True)
			root.add_widget(self.txt)
			return root
		def getData(self,btn):
			url = sys.argv[1] if len(sys.argv)>1 else 'https://www.baidu.com'
			hdl = HttpDataLoader()
			hdl.bind(on_loaded=self.showData)
			wait_coro(hdl.loadData,url)
			self.loop.call_later(0.001,hdl.loadData(url))

		def showData(self,instance,x):
			self.txt.text = x
	MyApp().run()
