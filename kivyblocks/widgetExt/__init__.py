from kivy.utils import platform
from .binstateimage import BinStateImage
from .jsoncodeinput import JsonCodeInput
from .inputext import FloatInput,IntegerInput,StrInput,SelectInput, BoolInput, Password
from .scrollwidget import ScrollWidget
from .messager import Messager
__all__ = [
BinStateImage,
JsonCodeInput,
FloatInput,
Password,
BoolInput,
IntegerInput,
StrInput,
SelectInput,
ScrollWidget,
Messager,
]

if platform == 'android':
	print('***********************************8')
	from .phonebutton import PhoneButton
	from .androidwebview import AWebView
	__all__ = __all__ + [PhoneButton, AWebView]
