import kivy
from kivy.utils import platform
from kivy.uix.textinput import TextInput

from appPublic.registerfunction import RegisterFunction

import kivyblocks.clickable
import kivyblocks.multi_select

from .baseWidget import *
from .tree import Tree, TextTree, MenuTree, PopupMenu
from .toolbar import ToolPage, Toolbar
from .dg import DataGrid
from .vplayer import VPlayer
from .aplayer import APlayer
from .form import Form, StrSearchForm
from .boxViewer import BoxViewer
from .pagescontainer import PageContainer
from .hostimage import HostImage
from .toggleitems import PressableBox, ToggleItems
from .twosides import TwoSides
from .tab import TabsPanel
from .qrdata import QRCodeWidget
# from .kivycamera import KivyCamera
from .filebrowser import FileLoaderBrowser
from .mapview import MapView
from .message import Conform
from .pagepanel import PagePanel
from .markdown import Markdown
# from .custom_camera import CustomCamera, QrReader
from .defaultimage import *
from .price import *

#if kivy.platform in ['win','linux', 'macosx']:
#	from .camerawithmic import ScreenWithMic
#from .camerawithmic import CameraWithMic
from .scrollpanel import ScrollPanel
from .udp_widget import UdpWidget
from .paging import PageLoader
from .dateinput import DateInput
from .block_test import BlockTest
from .hierarchy import Hierarchy
from .price import PriceView
from .ffpyplayer_video import FFVideo

r = Factory.register
# if kivy.platform in ['win','linux', 'macosx']:
#	r('ScreenWithMic', ScreenWithMic)
r('AnchorBox', AnchorBox)
r('FloatBox', FloatBox)
r('RelativeBox', RelativeBox)
r('GridBox', GridBox)
r('PageBox', PageBox)
r('ScatterBox', ScatterBox)
r('StackBox', StackBox)
r('DateInput', DateInput)
r('HTTPSeriesData', HTTPSeriesData)
r('HTTPDataHandler', HTTPDataHandler)
r('PageLoader', PageLoader)
r('UdpWidget', UdpWidget)
r('ScrollPanel', ScrollPanel)
r('TextInput', TextInput)
# r('CameraWithMic', CameraWithMic)
# r('CustomCamera', CustomCamera)
# r('QrReader', QrReader)
r('Markdown', Markdown)
r('PagePanel', PagePanel)
r('Conform', Conform)
r('Popup', Popup)
r('MapView', MapView)
r('DataGrid',DataGrid)
r('FileLoaderBrowser',FileLoaderBrowser)
# r('KivyCamera',KivyCamera)
r('QRCodeWidget',QRCodeWidget)
r('TabsPanel',TabsPanel)
r('TwoSides',TwoSides)
r('PageContainer', PageContainer)
r('BoxViewer', BoxViewer)
r('Form', Form)
r('StrSearchForm', StrSearchForm)
r('VPlayer', VPlayer)
r('DataGrid', DataGrid)
r('Toolbar', Toolbar)
r('ToolPage',ToolPage)
r('HTTPDataHandler',HTTPDataHandler)
r('Text',Text)
r('ScrollWidget',ScrollWidget)
r('BinStateImage',BinStateImage)
r('JsonCodeInput',JsonCodeInput)
r('FloatInput',FloatInput)
r('IntegerInput',IntegerInput)
r('StrInput',StrInput)
r('SelectInput',SelectInput)
r('BoolInput',BoolInput)
r('Messager',Messager)
r('LoginForm',LoginForm)
r('PressableImage', PressableImage)
r('PressableLabel', PressableLabel)
r('Tree',Tree)
r('TextTree',TextTree)
r('MenuTree',MenuTree)
r('PopupMenu',PopupMenu)
r('HostImage',HostImage)
r('APlayer',APlayer)
r('WrapText',WrapText)
r('PressableBox',PressableBox)
r('Title1',Title1)
r('Title2',Title2)
r('Title3',Title3)
r('Title4',Title4)
r('Title5',Title5)
r('Title6',Title6)
r('Modal',Modal)
r('TimedModal',TimedModal)
r('HBox',HBox)
r('VBox',VBox)
r('SwipeBox',SwipeBox)
r('ToggleItems',ToggleItems)
r('ExAccordion', ExAccordion)
r('Slider', Slider)
if platform == 'android':
	r('PhoneButton',PhoneButton)
	r('AWebView',AWebView)


def register_widget(name, klass):
	try:
		Factory.regiter(name, klass)
	except:
		Logger.info(f'Plugin : register_widget():{name} register error')

def register_registerfunction(name, func):
	rf = RegisterFunction()
	try:
		rf.register(name, func)
	except Exception as e:
		Logger.info(f'Plugin : register_registerfunction():{name} register error({e})')
		print_exc()

def register_blocks(name, value):
	b = Factory.Blocks()
	try:
		b.register_widget(name, value)
	except:
		Logger.info(f'plugin : register_blocks():{name} register error')


