from kivy.utils import platform
import plyer
try:
	from plyer.platforms.android import activity
except:
	print('android_rotation.py:import ERROR')
	activity = None

ROTATION_0 = 0
ROTATION_90 = 1
ROTATION_180 = 2
ROTATION_270 = 3
def get_rotation():
	try:
		r = activity.getWindowManager().getDefaultDisplay().getRotation()
		print('get_rotation(): rotation=', r, type(r))
		return r
	except Exception as e:
		print('get_rotation() failed',e)
		return None
