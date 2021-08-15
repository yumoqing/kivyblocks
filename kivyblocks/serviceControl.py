from jnius import autoclass

def startService(className):
	# service = autoclass('your.service.name.ClassName')
	service = autoclass(className)
	mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
	service.start(mActivity)

def stopService(className):
	service = autoclass(className)
	mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
	service.stop(mActivity)
