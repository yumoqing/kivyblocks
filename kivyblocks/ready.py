from kivy.event import EventDispatcher

class WidgetReady(EventDispatcher):
	def __init__(self):
		self.register_event_type('on_ready')
		self._ready = False

	def on_ready(self):
		pass

	def ready(self):
		if self._ready:
			return
		self.dispatch('on_ready')
		self._ready = True

	def reready(self):
		self._ready = False
		self.ready()
