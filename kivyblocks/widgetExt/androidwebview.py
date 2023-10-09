from kivy.uix.widget import Widget
from kivy.clock import Clock
from jnius import autoclass
from android.runnable import run_on_ui_thread


WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
activity = autoclass('org.kivy.android.PythonActivity').mActivity


class AWebView(Widget):
	def __init__(self, url=None):
		super(AWebView, self).__init__()
		self.baseUrl = url
		self.create_webview()
		# Clock.schedule_once(self.create_webview, 0)

	@run_on_ui_thread
	def create_webview(self, *args):
		print('create_webview() begining')
		self.webview = WebView(activity)
		settings = self.webview.getSettings()
		settings.setJavaScriptEnabled(True)
		settings.setUseWideViewPort(True) # enables viewport html meta tags
		settings.setLoadWithOverviewMode(True) # uses viewport
		settings.setSupportZoom(True) # enables zoom
		settings.setBuiltInZoomControls(True) # enables zoom controls
		wvc = WebViewClient()
		self.webview.setWebViewClient(wvc)
		activity.setContentView(self.webview)
		if self.baseUrl is not None:
			self.webview.loadUrl(self.baseUrl)
			print('go to the url=',self.baseUrl)
		print('create_webview() finished')
	
	def open(self,url):
		self.webview.loadUrl(url)
