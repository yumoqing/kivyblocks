from kivy.uix.button import Button
from jnius import autoclass
from jnius import cast
from .messager import Messager

class PhoneButton(Button):
	def __init__(self,**kw):
		self.options = kw
		self.phone_number = kw.get('phone_number')
		if self.phone_number is None:
			raise Exception('PhoneButton,miss phone_number')

		del self.options['phone_number']
		self.options.update({'text':'call'})
		super(PhoneButton,self).__init__(**self.options)
		self.bind(on_release=self.makecall)

	def makecall(self,inst):
		try:
			self.disabled = True
			Intent = autoclass('android.content.Intent') 
			Uri = autoclass('android.net.Uri')
			PythonActivity = autoclass('org.kivy.android.PythonActivity')
			intent = Intent(Intent.ACTION_CALL)
			intent.setData(Uri.parse("tel:" + self.phone_number))
			currentActivity = cast('android.app.Activity',
				PythonActivity.mActivity)
			currentActivity.startActivity(intent)
		except Exception as e:
			msger = Messager()
			msger.show_error(e)
