
from kivymd.bottomsheet import MDListBottomSheet, MDGridBottomSheet
from kivymd.button import MDIconButton
from kivymd.date_picker import MDDatePicker
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ILeftBodyTouch, \
			IRightBodyTouch, BaseListItem
from kivymd.material_resources import DEVICE_TYPE
from kivymd.navigationdrawer import MDNavigationDrawer, NavigationDrawerHeaderBase
from kivymd.navigationdrawer import NavigationLayout
from kivymd.navigationdrawer import NavigationDrawerDivider
from kivymd.navigationdrawer import NavigationDrawerToolbar
from kivymd.navigationdrawer import NavigationDrawerSubheader
from kivymd.selectioncontrols import MDSwitch
from kivymd.selectioncontrols import MDCheckbox
from kivymd.snackbar import Snackbar
from kivymd.theming import ThemeManager
from kivymd.time_picker import MDTimePicker
from kivymd.toolbar import Toolbar
from kivymd.list import MDList
from kivymd.textfields import MDTextField
from kivymd.spinner import MDSpinner
from kivymd.card import MDCard
from kivymd.card import MDSeparator
from kivymd.menu import MDDropdownMenu
from kivymd.grid import SmartTile
from kivymd.slider import MDSlider
from kivymd.tabs import MDTabbedPanel, MDTab, MDBottomNavigation, \
	MDBottomNavigationItem
from kivymd.progressbar import MDProgressBar
from kivymd.accordion import MDAccordion, MDAccordionItem
from kivymd.theme_picker import MDThemePicker

from kivyblocks.blocks import registerWidget

class TabbedPannel(MDTabbedPanel):
	def __init__(self,**options):
		
def kivyMDPlugin():
	registerWidget('MDSlider',MDSlider)
	registerWidget('MDTabbedPanel',MDTabbedPanel)
	registerWidget('MDTab',MDTab)
	registerWidget('MDBottomNavigation',MDBottomNavigation)
	registerWidget('MDBottomNavigationItem',MDBottomNavigationItem)
	registerWidget('MDProgressBar',MDProgressBar)
	registerWidget('MDAccordion',MDAccordion)
	registerWidget('MDAccordionItem',MDAccordionItem)
	registerWidget('MDThemePicker',MDThemePicker)
	registerWidget('MDListBottomSheet',MDListBottomSheet)
	registerWidget('MDGridBottomSheet',MDGridBottomSheet)
	registerWidget('MDIconButton', MDIconButton)
	registerWidget('MDDatePicker', MDDatePicker)
	registerWidget('MDDialog', MDDialog)
	registerWidget('MDLabel', MDLabel)
	registerWidget('ILeftBody',ILeftBody)
	registerWidget('ILeftBodyTouch',ILeftBodyTouch)
	registerWidget('IRightBodyTouch',IRightBodyTouch)
	registerWidget('BaseListItem',BaseListItem)
	registerWidget('MDNavigationDrawer',MDNavigationDrawer)
	registerWidget('NavigationDrawerHeaderBase',NavigationDrawerHeaderBase)
	registerWidget('MDCheckbox',MDCheckbox)
	registerWidget('Snackbar',Snackbar)
	registerWidget('ThemeManager',ThemeManager)
	registerWidget('MDTimePicker',MDTimePicker)
	registerWidget('Toolbar',Toolbar)
	registerWidget('NavigationLayout',NavigationLayout)
	registerWidget('NavigationDrawerDivider',NavigationDrawerDivider)
	registerWidget('NavigationDrawerToolbar',NavigationDrawerToolbar)
	registerWidget('NavigationDrawerSubheader',NavigationDrawerSubheader)
	registerWidget('MDSwitch',MDSwitch)
	registerWidget('MDList',MDList)
	registerWidget('MDTextField',MDTextField)
	registerWidget('MDSpinner',MDSpinner)
	registerWidget('MDCard',MDCard)
	registerWidget('MDSeparator',MDSeparator)
	registerWidget('SmartTile',SmartTile)

