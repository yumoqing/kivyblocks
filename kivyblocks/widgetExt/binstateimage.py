from kivy.uix.image import Image,AsyncImage
from kivy.uix.button import Button
from kivy.graphics import Color
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty

class BinStateImage(Button):
	binstate = NumericProperty(1)
	def __init__(self,source1='../images/bullet_arrow_right.png',source2='../images/bullet_arrow_down.png',**kv):
		self.bin_state_images = [
			source1,
			source2
		]
		kv.update({'source':source1})
		super(BinStateImage,self).__init__()
		self.myImgWidget = Image(**kv)
		self.size = self.myImgWidget.size
		#self.background_color = Color(1,0,0,1)
		self.bind(on_release=self.changeState)
	
	def changeState(self,instance):
		#print('on_release fired')
		if instance.binstate == 1:
			instance.binstate = 2
		else: instance.binstate = 1
		self.myImgWidget.source = self.bin_state_images[instance.binstate-1]
		self.myImgWidget.reload()

if __name__ == '__main__':
	from kivy.app import App
	class MyApp(App):
		def build(self):
			m = BoxLayout(orientation='vertical')
			img = BinStateImage()
			img.bind(binstate=self.showState)
			m.add_widget(img)
			b = Button(text='GGGG')
			m.add_widget(b)
			return m
		def showState(self,img,v):
			pass #print('cur state=',img.binstate,v)
	
	MyApp().run()
