from pyler import gps

class GPS:
	def __init__(self):
		gps.configure(on_location=self.on_location, on_status=self.on_status)
		gps.start()

	def on_location(self, **kw):
		pass
	
	def on_status(self,**kw):
		pass
	def __del__(self):
		gps.stop()

