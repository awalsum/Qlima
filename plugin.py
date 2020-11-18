"""
<plugin key="Qlima" name="Qlima Wifi airconditioner" author="Alain" version="1.0.0">
    <description>
        <h2>Qlima Wifi AС</h2><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>On/Off</li>
            <li>HVAC Mode: Auto, Cool, Heat, Fan, Dry</li>
            <li>Fan speed: Low, Medium, High, Auto</li>
            <li>Swing: Off, Vertical, Horizontal, Both</li>
            <li>Set temp of (C) from 17 to 30</li>
            <li>Presets: Normal, ECO, Turbo</li>
            <li>Display: On/Off</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="192.168.0.61"/>
        <param field="Mode4" label="Port" width="100px" required="true" default="6444"/>
        <param field="Mode3" label="Unit id" width="300px" required="true" default="18691600000000"/>
        <param field="Mode1" label="Update interval (sec):" width="75px">
            <options>
                <option label="30" value="3" />
                <option label="60" value="6" default="true" />
                <option label="90" value="9" />
                <option label="120" value="12" />
            </options>
        </param>
        <param field="Mode2" label="Debug" width="75px">
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

sys.path.append('/usr/lib/python3/dist-packages')

from msmart.device import air_conditioning_device as ac
from msmart.device import device as midea_device



class BasePlugin:
    
    enabled = True
    run_counter = 0


    def __init__(self):
        return

    def onStart(self):
        device_ip = Parameters["Address"]
        device_id = Parameters["Mode3"]
        device_port = Parameters["Mode4"]
        client = midea_device(device_ip, int(device_id), int(device_port))
        device = client.setup()

# get AC info
        device.refresh() 
        
        
        if Parameters["Mode2"] == "Debug":
            Domoticz.Debugging(1)
            DumpConfigToLog()

        if len(Devices) == 0:
            Domoticz.Device(Name="Power", Unit=1, Image=9, TypeName="Switch", Used=1).Create()
            Domoticz.Device(Name="Temp Inside", Unit=2, TypeName="Temperature", Used=1).Create()
            Domoticz.Device(Name="Temp Outside", Unit=3, TypeName="Temperature", Used=1).Create()
            Domoticz.Device(Name="Setpoint", Unit=4, Type=242, Subtype=1, Image=16, Used=1).Create()

            Options = {"LevelActions": "||||||",
                       "LevelNames": "|Auto|Heat|Cool|Dry|Fan",
                       "LevelOffHidden": "true",
                       "SelectorStyle": "1"}

            Domoticz.Device(Name="Mode", Unit=5, TypeName="Selector Switch", Image=16, Options=Options, Used=1).Create()

            Options = {"LevelActions": "|||||",
                       "LevelNames": "|High|Medium|Low|Auto",
                       "LevelOffHidden": "true",
                       "SelectorStyle": "1"}

            Domoticz.Device(Name="Fan Rate", Unit=6, TypeName="Selector Switch", Image=7, Options=Options,
                            Used=1).Create()

            Options = {"LevelActions": "|||",
                       "LevelNames": "Off|Vertical|Horizontal|Both",
                       "LevelOffHidden": "false",
                       "SelectorStyle": "1"}

            Domoticz.Device(Name="Swing", Unit=7, TypeName="Selector Switch", Image=7, Options=Options, Used=1).Create()

            
            Domoticz.Device(Name="Turbo", Unit=8, Image=9, TypeName="Switch", Used=1).Create()

            Domoticz.Device(Name="Eco", Unit=9, Image=9, TypeName="Switch", Used=1).Create()

            Domoticz.Debug("Qlima Wifi Airco device created.")

        DumpConfigToLog()

        Domoticz.Heartbeat(10)

        self.DataUpdate()

    def onStop(self):
        Domoticz.Debug("onStop called")
        return True

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        device_ip = Parameters["Address"]
        device_id = Parameters["Mode3"]
        device_port = Parameters["Mode4"]
        client = midea_device(device_ip, int(device_id), int(device_port))
        device = client.setup()
      
        Domoticz.Debug(
            "Command received U=" + str(Unit) + " C=" + str(Command) + " L= " + str(Level) + " H= " + str(Hue))

        try:
            device.refresh()
        except:
            Domoticz.Error("AC (" + Parameters["Address"] + ") unavailable OnCommand")
            return

        if (Unit == 1):
            if (Command == "On"):
                device.power_state = True
                device.apply()
                Devices[1].Update(nValue=1, sValue="On")

            else:
                device.power_state = False
                device.apply()
                Devices[1].Update(nValue=0, sValue="Off")



        if (Unit == 4):
            if Level > 30:
                Level = 30
            elif Level < 17:
                Level = 17

            device.target_temperature = int(Level)
            device.apply()
            Devices[4].Update(nValue=device.power_state, sValue=str(Level))



        if (Unit == 5):
#            Domoticz.Error("Level is: " + str(Level))
            if (str(Level) == '10'):
                device.operational_mode = ac.operational_mode_enum.auto
                device.apply()
            elif (str(Level) == '20'):
                device.operational_mode = ac.operational_mode_enum.heat
                device.apply()
            elif (str(Level) == '30'):
                device.operational_mode = ac.operational_mode_enum.cool
                device.apply()
            elif (str(Level) == '40'):
                device.operational_mode = ac.operational_mode_enum.dry
                device.apply()
            else:
                device.operational_mode = ac.operational_mode_enum.fan_only
                device.apply()
            
            Devices[5].Update(nValue=device.power_state, sValue=str(Level))



        if (Unit == 6):
#            Domoticz.Error("Level is: " + str(Level))
            if (str(Level) == '10'):
                device.fan_speed = ac.fan_speed_enum.High
                device.apply()
            elif (str(Level) == '20'):
                device.fan_speed = ac.fan_speed_enum.Medium
                device.apply()
            elif (str(Level) == '30'):
                device.fan_speed = ac.fan_speed_enum.Low
                device.apply()
            
            else:
                device.fan_speed = ac.fan_speed_enum.Auto
                device.apply()
            
            Devices[6].Update(nValue=device.power_state, sValue=str(Level))



        if (Unit == 7):
 #           Domoticz.Error("Level is: " + str(Level))
            if (str(Level) == '0'):
                device.swing_mode = ac.swing_mode_enum.Off
                device.apply()
            elif (str(Level) == '10'):
                device.swing_mode = ac.swing_mode_enum.Vertical
                device.apply()
            elif (str(Level) == '20'):
                device.swing_mode = ac.swing_mode_enum.Horizontal
                device.apply()
            
            else:
                device.swing_mode = ac.swing_mode_enum.Both
                device.apply()
            
            Devices[7].Update(nValue=device.power_state, sValue=str(Level))



        if (Unit == 8):
            if (Command == "On"):
                device.eco_mode = False
                device.turbo_mode = True
                device.apply()
                Devices[8].Update(nValue=1, sValue="On")

            else:
                device.turbo_mode = False
                device.apply()
                Devices[8].Update(nValue=0, sValue="Off")



        if (Unit == 9):
            if (Command == "On"):
                device.turbo_mode = False
                device.eco_mode = True
                device.apply()
                Devices[9].Update(nValue=1, sValue="On")

            else:
                device.eco_mode = False
                device.apply()
                Devices[9].Update(nValue=0, sValue="Off")



    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(
            Priority) + "," + Sound + "," + ImageFile)


    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")


    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        self.run_counter = self.run_counter - 1
        if self.run_counter <= 0:
            Domoticz.Debug("Poll unit")
            self.run_counter = int(Parameters["Mode1"])
            self.DataUpdate()
        else:
            Domoticz.Debug("Polling unit in " + str(self.run_counter) + " heartbeats.")


    def DataUpdate(self):
        device_ip = Parameters["Address"]
        device_id = Parameters["Mode3"]
        device_port = Parameters["Mode4"]
        client = midea_device(device_ip, int(device_id), int(device_port))
        device = client.setup()
        
        try:
            device.refresh()
            if device.indoor_temperature == 0.0 and device.indoor_temperature == 0.0 and device.target_temperature == 17.0:
               raise ConnectionError('Could not connect with device',)
            Devices[1].Update(nValue=device.power_state, sValue=str(device.power_state))
            Devices[2].Update(nValue=0, sValue=str(device.indoor_temperature))
            Devices[3].Update(nValue=0, sValue=str(device.outdoor_temperature))
            Devices[4].Update(nValue=device.power_state, sValue=str(device.target_temperature))
            
            
            Devices[5].Update(nValue=device.power_state, sValue=str(device.operational_mode))
            if str(device.operational_mode) == 'operational_mode_enum.auto':
                Level = '10'
            elif str(device.operational_mode) == 'operational_mode_enum.heat':
                Level = '20'
            elif str(device.operational_mode) == 'operational_mode_enum.cool':
                Level = '30'
            elif str(device.operational_mode) == 'operational_mode_enum.dry':
                Level = '40'
            else:
                Level = '50'
            Devices[5].Update(nValue=device.power_state, sValue=str(Level))
            
            
            
            Devices[6].Update(nValue=device.power_state, sValue=str(device.fan_speed))
            if str(device.fan_speed) == 'fan_speed_enum.High':
                Level = '10'
            elif str(device.fan_speed) == 'fan_speed_enum.Medium':
                Level = '20'
            elif str(device.fan_speed) == 'fan_speed_enum.Low':
                Level = '30'
            else:
                Level = '40'
            Devices[6].Update(nValue=device.power_state, sValue=str(Level))
            
                        
            Devices[7].Update(nValue=device.power_state, sValue=str(device.swing_mode))
            if str(device.swing_mode) == 'swing_mode_enum.Vertical':
                Level = '10'
            elif str(device.swing_mode) == 'swing_mode_enum.Horizontal':
                Level = '20'
            elif str(device.swing_mode) == 'swing_mode_enum.Both':
                Level = '30'
            else:
                Level = '0'
            Devices[7].Update(nValue=device.power_state, sValue=str(Level))
                     
            
            Devices[8].Update(nValue=device.turbo_mode, sValue=str(device.turbo_mode))
            Devices[9].Update(nValue=device.eco_mode, sValue=str(device.eco_mode))

        except ConnectionError as error:
            Domoticz.Error(repr(error))
            return
            
        except:
            Domoticz.Error("Qlima (" + Parameters["Address"] + ") unavailable")
            return        


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


def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
