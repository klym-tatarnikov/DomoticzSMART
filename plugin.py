"""
<plugin key="SMARTMonitor" name="SMART Monitor" author="klym.tatarnikov" version="1.0.0">
    <description>
        <h2>SMART Monitoring Plugin</h2><br/>
        Collects raw values for all SMART attributes<br/>
        <br/>
        <h3>Installation:</h3><br/>
        pySMART Python3 module should be installed first:<br/>
            pip3 install pySMART<br/>
        also smartmontools needs to be installed:<br/>
            apt-get install smartmontools
        <br/>
    </description>
    <params>
        <param field="Address" label="Disk path" width="250px" required="true" default="/dev/sda"/>
        <param field="Mode4" label="Check Interval (minutes)" width="75px" required="true" default="1"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import sys
import site
import subprocess
from pySMART import Device

for site in site.getsitepackages():
    sys.path.append(site)

from struct import unpack
#v.1.0.0:   First Commit

class BasePlugin:

    enabled = False

    def __init__(self):
        self.pollPeriod = 0
        self.pollCount = 0
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
            
        self.DEVICEPATH = Parameters["Address"]

        smartDevice = Device(self.DEVICEPATH)
        Domoticz.Log(smartDevice)
        smartAttributes = smartDevice.attributes
       
        if (len(Devices) == 0):
            attCount = 0
            for attribute in smartAttributes:
                if attribute is not None:
                    Domoticz.Log("Adding new attribute: " + str(attribute.name))
                    attCount += 1
                    if "Temperature" in attribute.name:
                         Domoticz.Device(Name=attribute.name, Unit=attribute.num, TypeName='Temperature', Used=0).Create()
                    else:
                         Domoticz.Device(Name=attribute.name, Unit=attribute.num, TypeName='Custom', Used=0).Create()
            Domoticz.Log ('Added '+str(attCount)+' new attributes')

        self.pollPeriod = 6 * int(Parameters["Mode4"]) 
        self.pollCount = self.pollPeriod - 1
        Domoticz.Heartbeat(10)

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartBeat called:"+str(self.pollCount)+"/"+str(self.pollPeriod))
        if self.pollCount >= self.pollPeriod:
            smartDevice = Device(self.DEVICEPATH)
            Domoticz.Debug("Reading SMART for" + str(smartDevice))
            smartAttributes = smartDevice.attributes
            for attribute in smartAttributes:
                if attribute is not None:
                    Value = attribute.raw
                    Domoticz.Debug(attribute.name + ' : ' + Value)
                    UpdateDevice(attribute.num, 0, Value)
            self.pollCount = 0 #Reset Pollcount
        else:
            self.pollCount += 1

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def UpdateDevice(Unit, nValue, sValue):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
            Domoticz.Debug("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

