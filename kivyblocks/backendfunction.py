# from appPublic.background import Background
from threading import Thread
from kivy.event import EventDispatcher

class BackendFunction(EventDispatcher, Thread):
	def __init__(self, callee, *args, **kw):
		EventDispatcher.__init__(self)
		Thread.__init__(self)
		self._callee = callee
		self._args = args
		self._kw = kw
		self.register_event_type('on_success')
		self.register_event_type('on_failed')

	def on_success(self, ret):
		print('BackendFunction(), on_success fired')

	def on_failed(self, e):
		print('BackendFunciton(), on_failed fired', e)

	def run(self):
		try:
			x = self._callee(*self._args, **self._kw)
			self.dispatch('on_success', x)
		except Exception as e:
			self.dispatch('on_failed',e)
