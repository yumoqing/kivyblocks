from kivy.app import App
from kivy.metrics import mm
from kivy.core.window import Window

from appPublic.Singleton import SingletonDecorator
from appPublic.jsonConfig import getConfig

@SingletonDecorator
class KivySizes:
	myFontSizes = {
		"smallest":1.5,
		"small":2.0,
		"normal":2.5,
		"large":3.0,
		"huge":3.5,
		"hugest":4.0,
	}
	separatorsize = 2

	def getFontSize(self,name=None):
		config = getConfig()
		if config.font_sizes:
			self.myFontSizes = config.font_sizes
		if name is None:
			name = config.font_name
		x = self.myFontSizes.get(name,None)
		if x == None:
			x = self.myFontSizes.get('normal')
		return x

	def namedSize(self,cnt=1,name=None):
		return mm(cnt * self.getFontSize(name=name))

	def unitedSize(self,x,y=None,name=None):
		xr = self.namedSize(cnt=x,name=name)
		if y is None:
			return xr
		return (xr,self.namedSize(cnt=y,name=name))

	def CSize(self,x,y=None,name=None):
		return self.unitedSize(x,y=y,name=name)

	def getScreenSize(self):
		return Window.width, Window.height

	def getWindowPhysicalSize(self):
		h_phy = float(Window.height) / mm(1)
		w_phy = float(Window.width) / mm(1)
		return w_phy, h_phy
	
	def getScreenPhysicalSize(self):
		return self.getWindowPhysicalSize()

	def isHandHold(self):
		return min(self.getScreenPhysicalSize()) <= 75.0

