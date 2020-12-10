from kivy.utils import platform
from .baseWidget import *
from .tree import Tree, TextTree, PopupMenu
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
from .kivycamera import KivyCamera
from .filebrowser import FileLoaderBrowser

r = Factory.register
r('DataGrid',DataGrid)
r('FileLoaderBrowser',FileLoaderBrowser)
r('KivyCamera',KivyCamera)
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
r('AmountInput',AmountInput)
r('Messager',Messager)
r('Bar',Bar)
r('LoginForm',LoginForm)
r('PressableImage', PressableImage)
r('PressableLabel', PressableLabel)
r('Tree',Tree)
r('TextTree',TextTree)
r('PopupMenu',PopupMenu)
r('HostImage',HostImage)
r('APlayer',APlayer)
r('WrapText',WrapText)
r('PressableBox',PressableBox)
r('ToggleItems',ToggleItems)
if platform == 'android':
	r('PhoneButton',PhoneButton)
	r('AWebView',AWebView)
	r('AndroidCamera',AndroidCamera)
