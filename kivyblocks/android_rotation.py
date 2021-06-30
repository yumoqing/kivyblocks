from kivy.utils import platform
import plyer
try:
	from android import activity
	# from plyer.platforms.android import activity
	# return rotation is 0 forever 
except:
	print('android_rotation.py:from android import activity ERROR')
	activity = None

def get_rotation():
	try:
		r = activity.getWindowManager().getDefaultDisplay().getRotation()
		print('get_rotation(): rotation=', r, type(r))
		return r
	except Exception as e:
		print('get_rotation() failed',e)
		return None
