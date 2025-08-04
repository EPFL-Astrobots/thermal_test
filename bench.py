import classCamera
import DEFINES
import classConfig
import positioner
from serial.tools import list_ports
import can
from status import *


def bench_init(comBus = None):
    cam = None
    pos = None
    bus = None

    allPos = None
    pos21 = None
    pos22 = None
    pos23 = None
    pos24 = None
    pos25 = None
    pos26 = None

    # # prepare camera and set auto exposure
    exposure_time = 8000
    time_expo = exposure_time

    cam = classCamera.Camera(cameraType = DEFINES.PC_CAMERA_TYPE_XY)
    cam.setMaxROI()
    if exposure_time == 1000:
        exposure_time = cam.getOptimalExposure(exposure_time)
        print(f"exposure time auto set to: {time_expo} us")
    else:
        exposure_time = cam.setExposure(exposure_time)
        print(f"exposure time manually set to: {time_expo} us")
    config = classConfig.Config()
    cam.setDistortionCorrection(config)

    # check communication handler for can bus
    if comBus is None:
        comPorts = list(list_ports.comports())
        for port_no, description, device in comPorts:
            if 'USB' in description:
                try:
                    bus = can.interface.Bus(port_no, bustype='slcan', ttyBaudrate=921600, bitrate=1000000)
                    print('communication bus at ' + port_no)
                except:
                    print ('no commucation bus found')
    else:
        try:
            bus = can.interface.Bus(comBus, bustype='slcan', ttyBaudrate=921600, bitrate=1000000)
            print('communication bus at ' + comBus)
        except:
                print('no communication bus')

    if bus is not None:
        allPos = positioner.Positioner(bus, 0)
        pos21 = positioner.Positioner(bus, 21)
        pos22 = positioner.Positioner(bus, 22)
        pos23 = positioner.Positioner(bus, 23)
        pos24 = positioner.Positioner(bus, 24)
        pos25 = positioner.Positioner(bus, 25)
        pos26 = positioner.Positioner(bus, 26)
        
        for pos in [pos21, pos22, pos23, pos24, pos25, pos26]:
            pos.reset_all_positions()
            pos.set_mode_open_loop()
            pos.set_current(60, 40)
            pos.set_speed(1000, 1000)
            pos.set_precision_mode_off()

            newFlags = PositionerStatus()
            newFlags.datum_alpha_calibrated = 1
            newFlags.datum_beta_calibrated = 1

            pos.set_status(newFlags)

    return cam, allPos, pos21, pos22, pos23, pos24, pos25, pos26
