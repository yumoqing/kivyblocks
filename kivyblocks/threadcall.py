# -*- coding=utf-8 -*-

import time
from threading import Thread, Lock, BoundedSemaphore
import requests
from functools import wraps

from kivy.event import EventDispatcher
from kivy.clock import Clock
from kivy.app import App
from .login import LoginForm

from appPublic.http_client import Http_Client

class ThreadCall(Thread,EventDispatcher):
	def __init__(self,target, args=(), kwargs={}):
		Thread.__init__(self)
		EventDispatcher.__init__(self)
		self.register_event_type('on_result')
		self.register_event_type('on_error')
		self.rez = None
		self.daemon = False
		self.target = target
		self.args = args
		self.timing = None
		self.kwargs = kwargs
	
	def start(self):
		Thread.start(self)
		self.timing = Clock.schedule_once(self.checkStop,0)

	def run(self):
		try:
			# print('ThreadCall()',self.args,'start...')
			self.rez = self.target(*self.args,**self.kwargs)
			self.dispatch('on_result',self.rez)
			# print('ThreadCall()',*self.args,'finished...')

		except Exception as e:
			# print('ThreadCall()',*self.args,'Error...')
			self.dispatch('on_error',e)

	def on_result(self, v):
		pass # print('ThreadCall():on_result() called,v=',v)

	def on_error(self,e):
		pass

	def checkStop(self,timestamp):
		x = self.join(timeout=0.001)
		if self.is_alive():
			self.timing = Clock.schedule_once(self.checkStop,0)
			return

class Workers(Thread):
	def __init__(self,maxworkers):
		super().__init__()
		self.max_workers = maxworkers
		self.tasks = []
		# task = [callee,callback,kwargs]
		self.lock = Lock()
		self.work_sema = BoundedSemaphore(value=self.max_workers)
		self.running = False
	def run(self):
		self.running = True
		while self.running:
			if len(self.tasks) == 0:
				time.sleep(0.001)
				continue
			task = None
			with self.lock:
				task = self.tasks.pop()
			if task is None:
				continue
			with self.work_sema:
				callee,callback,errback,kwargs = task
				x = ThreadCall(callee,kwargs=kwargs)
				x.bind(on_result=callback)
				"""
				并发的时候，只有一个callback会被调用
				"""
				if errback:
					x.bind(on_error=errback)
				x.start()

	def add(self,callee,callback,errback=None,kwargs={}):
		with self.lock:
			self.tasks.insert(0,[callee,callback,errback,kwargs])

class HttpClient(Http_Client):
	def __init__(self):
		super().__init__()
		self.workers = App.get_running_app().workers
		
	def __call__(self,url,method="GET",
				params={},
				headers={},
				files={},
				stream=False,
				callback=None,
				errback=None):
		method = method.upper()
		def cb(t,resp):
			return resp

		if callback is None:
			try:
				resp = self.webcall(url, method=method,
						params=params, files=files, headers=headers)
				return cb(None,resp)
			except Exception as e:
				raise e
		kwargs = {
			"url":url,
			"method":method,
			"params":params,
			"files":files,
			"stream":stream,
			"headers":headers
		}

		self.workers.add(self.webcall,callback,errback,kwargs=kwargs)

	def get(self, url, params={}, headers={}, stream=False, callback=None, errback=None):
		return self.__call__(url,method='GET',params=params,
				headers=headers, stream=stream, callback=callback,
				errback=errback)
	def post(self, url, params={}, headers={}, files={}, stream=False, callback=None, errback=None):
		return self.__call__(url,method='POST',params=params, files=files,
				headers=headers, stream=stream, callback=callback,
				errback=errback)

	def put(self, url, params={}, headers={}, stream=False, callback=None, errback=None):
		return self.__call__(url,method='PUT',params=params,
				headers=headers, stream=stream, callback=callback,
				errback=errback)

	def delete(self, url, params={}, headers={}, callback=None, errback=None):
		return self.__call__(url,method='DELETE',params=params,
				headers=headers, callback=callback,
				errback=errback)

	def option(self, url, params={}, headers={}, callback=None, errback=None):
		return self.__call__(url,method='OPTION',params=params,
				headers=headers, callback=callback, errback=errback)
	
if __name__ == '__main__':
	from kivy.uix.textinput import TextInput
	from kivy.app import App
	from kivy.uix.boxlayout import BoxLayout
	from kivy.uix.button import Button
	class MyApp(App):
		def build(self):
			self.hc = HttpClient()
			x = BoxLayout(orientation='vertical')
			y = BoxLayout(orientation='horizontal',size_hint_y=0.07)
			self.ti = TextInput(size_hint_x=0.95,multiline=False)
			btn = Button(size_hint_x=0.05,text='go')
			y.add_widget(self.ti)
			y.add_widget(btn)
			btn.bind(on_press=self.getHtml)
			self.texti = TextInput(multiline=True,readonly=True)
			x.add_widget(y)
			x.add_widget(self.texti)
			
			return x
	
		def getHtml(self,v=None):
			url = self.ti.text
			self.hc.get(url,callback=self.showResult)
			self.texti.text = 'loading...'

		def showResult(self,target,resp):
			if resp.status_code==200:
				self.texti.text = resp.text
			else:
				print(reps.status_code,'...............')
	MyApp().run()
