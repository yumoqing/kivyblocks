from kivy.utils import platform
import plyer
try:
	#
	# from android import activity
	# get_rotation() failed module 'android.activity' has no attribute 'getWindowManager'
	from plyer.platforms.android import activity
except:
	print('android_rotation.py:mport ERROR')
	activity = None

def get_rotation():
	try:
		r = activity.getWindowManager().getDefaultDisplay().getRotation()
		print('get_rotation(): rotation=', r, type(r))
		return r
	except Exception as e:
		print('get_rotation() failed',e)
		return None
