import P2Pro.P2Pro_cmd as P2Pro

cam = P2Pro.P2Pro()
# print (cam._dev)
# cam._standard_cmd_write(P2Pro.CmdCode.sys_reset_to_rom)
# print(cam._standard_cmd_read(P2Pro.CmdCode.cur_vtemp, 0, 2))
# print(cam._standard_cmd_read(P2Pro.CmdCode.shutter_vtemp, 0, 2))
cam.pseudo_color_set(0, P2Pro.PseudoColorTypes.PSEUDO_IRON_RED)
print(cam.pseudo_color_get())
# cam.set_prop_tpd_params(P2Pro.PropTpdParams.TPD_PROP_GAIN_SEL, 0)
print(cam.get_prop_tpd_params(P2Pro.PropTpdParams.TPD_PROP_GAIN_SEL))