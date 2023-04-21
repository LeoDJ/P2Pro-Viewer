import threading
import time
import os
import logging

import P2Pro.video
import P2Pro.P2Pro_cmd as P2Pro_CMD
import P2Pro.recorder

logging.basicConfig()
logging.getLogger('P2Pro.recorder').setLevel(logging.INFO)
logging.getLogger('P2Pro.P2Pro_cmd').setLevel(logging.INFO)

try:
    vid = P2Pro.video.Video()
    video_thread = threading.Thread(target=vid.open, args=(1,))
    video_thread.start()

    while not vid.video_running:
        time.sleep(0.01)

    rec = P2Pro.recorder.VideoRecorder(vid.frame_queue[1], "test")
    rec.start()

    cam_cmd = P2Pro_CMD.P2Pro()

    # print (cam_cmd._dev)
    # cam_cmd._standard_cmd_write(P2Pro_CMD.CmdCode.sys_reset_to_rom)
    # print(cam_cmd._standard_cmd_read(P2Pro_CMD.CmdCode.cur_vtemp, 0, 2))
    # print(cam_cmd._standard_cmd_read(P2Pro_CMD.CmdCode.shutter_vtemp, 0, 2))
    cam_cmd.pseudo_color_set(0, P2Pro_CMD.PseudoColorTypes.PSEUDO_IRON_RED)
    print(cam_cmd.pseudo_color_get())
    # cam_cmd.set_prop_tpd_params(P2Pro_CMD.PropTpdParams.TPD_PROP_GAIN_SEL, 0)
    print(cam_cmd.get_prop_tpd_params(P2Pro_CMD.PropTpdParams.TPD_PROP_GAIN_SEL))
    print(cam_cmd.get_device_info(P2Pro_CMD.DeviceInfoType.DEV_INFO_GET_PN))

    time.sleep(5)
    rec.stop()

    while True:
        # print(vid.frame_queue[0].get(True, 2)) # test
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Killing...")
    time.sleep(5)
    pass
os._exit(0)