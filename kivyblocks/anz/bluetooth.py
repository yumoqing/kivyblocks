from kivy.app import App

from jnius import autoclass
import kivy
from android.broadcast import BroadcastReceiver
import sys

from kivyblocks.baseWidget import VBox

BluetoothManager = autoclass('android.bluetooth.BluetoothManager')
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice  = autoclass('android.bluetooth.BluetoothDevice')

class BluetoothFinder(VBox):
	data = ListProperty([])
    def __init__(self, **kw):
        super().__init__(**kw)
		arg = context.getSystemService(context.BLUETOOTH_SERVICE)
		self.bt_manager = BluetoothManager(arg)
		self.bt_adapter = self.bt_manager.getAdaper()
        self.unpairedBT()
        
	def get_paired_bt(self):
		return self.bt_adapter.getBondedDevice()

	def __del__(self):
		self.adapter.cancelDiscovery()

    def unpairedBT(self):
        self.adapter = BluetoothAdapter.getDefaultAdapter()
        # Search foir unpaired devices
        print("Unpaired devices")
        self.data=[{"text": "Unpaired Devices"}]
        myReceiver = BroadcastReceiver(self.onReceive, actions = [BluetoothDevice.ACTION_FOUND, BluetoothAdapter.ACTION_DISCOVERY_STARTED, BluetoothAdapter.ACTION_DISCOVERY_FINISHED])
        myReceiver.start()
        self.adapter.startDiscovery()

    # Called by Broadcastreceiver
    def onReceive(self, context, intent):
        print(f"*BT* On receive context{context}", flush = True)
        print(f"*BT* On receive intent {intent}", flush = True)
        sys.stdout.flush()
        
        self.myData.append({"text": f"Context {context}, intent {intent}"})
        self.layout.data = [item for item in self.myData]

