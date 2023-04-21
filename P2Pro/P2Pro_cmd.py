import enum
import struct
import time
import logging

import usb.util
import usb.core

log = logging.getLogger(__name__)


class PseudoColorTypes(enum.IntEnum):
    PSEUDO_WHITE_HOT = 1
    PSEUDO_RESERVED = 2
    PSEUDO_IRON_RED = 3
    PSEUDO_RAINBOW_1 = 4
    PSEUDO_RAINBOW_2 = 5
    PSEUDO_RAINBOW_3 = 6
    PSEUDO_RED_HOT = 7
    PSEUDO_HOT_RED = 8
    PSEUDO_RAINBOW_4 = 9
    PSEUDO_RAINBOW_5 = 10
    PSEUDO_BLACK_HOT = 11
    # WHITE_HOT_MODE = 16   # unsure what the modes do, but it returns an error when trying to set
    # BLACK_HOT_MODE = 17
    # RAINBOW_MODE = 18
    # IRONBOW_MODE = 19
    # AURORA_MODE = 20
    # JUNGLE_MODE = 21
    # GLORY_HOT_MODE = 22
    # MEDICAL_MODE = 23
    # NIGHT_MODE = 24
    # SEPIA_MODE = 25
    # RED_HOT_MODE = 26


class PropTpdParams(enum.IntEnum):
    TPD_PROP_DISTANCE = 0   # 1/163.835 m, 0-32767, Distance
    TPD_PROP_TU = 1         # 1 K, 0-1024, Reflection temperature
    TPD_PROP_TA = 2         # 1 K, 0-1024, Atmospheric temperature
    TPD_PROP_EMS = 3        # 1/127, 0-127, Emissivity
    TPD_PROP_TAU = 4        # 1/127, 0-127, Atmospheric transmittance
    TPD_PROP_GAIN_SEL = 5   # binary, 0-1, Gain select (0=low, 1=high)


class DeviceInfoType(enum.IntEnum):
    DEV_INFO_CHIP_ID = 0
    DEV_INFO_FW_COMPILE_DATE = 1
    DEV_INFO_DEV_QUALIFICATION = 2
    DEV_INFO_IR_INFO = 3
    DEV_INFO_PROJECT_INFO = 4
    DEV_INFO_FW_BUILD_VERSION_INFO = 5
    DEV_INFO_GET_PN = 6
    DEV_INFO_GET_SN = 7
    DEV_INFO_GET_SENSOR_ID = 8


class CmdDir(enum.IntFlag):
    GET = 0x0000
    SET = 0x4000


class CmdCode(enum.IntEnum):
    sys_reset_to_rom = 0x0805
    spi_transfer = 0x8201
    get_device_info = 0x8405
    pseudo_color = 0x8409
    shutter_vtemp = 0x840c
    prop_tpd_params = 0x8514
    cur_vtemp = 0x8b0d
    preview_start = 0xc10f
    preview_stop = 0x020f
    y16_preview_start = 0x010a
    y16_preview_stop = 0x020a


class P2Pro:
    _dev: usb.core.Device

    def __init__(self):
        self._dev = usb.core.find(idVendor=0x0BDA, idProduct=0x5830)
        if (self._dev == None):
            raise FileNotFoundError("Infiray P2 Pro thermal module not found, please connect and try again!")
        pass

    def _check_camera_ready(self) -> bool:
        """
        Checks if the camera is ready (i2c_usb_check_access_done in the SDK) 

        :return: True if the camera is ready
        :raises UserWarning: When the return code of the camera is abnormal
        """
        ret = self._dev.ctrl_transfer(0xC1, 0x44, 0x78, 0x200, 1)
        if (ret[0] & 1 == 0 and ret[0] & 2 == 0):
            return True
        if (ret[0] & 0xFC != 0):
            raise UserWarning(f"vdcmd status error {ret[0]:#X}")
        return False

    def _block_until_camera_ready(self, timeout: int = 5) -> bool:
        """
        Blocks until the camera is ready or the timeout is reached

        :param timeout: Timeout in seconds
        :return: True if the camera is ready, False if the timout occured
        :raises UserWarning: When the return code of the camera is abnormal
        """
        start = time.time()
        while True:
            if (self._check_camera_ready()):
                return True
            time.sleep(0.001)
            if (time.time() > start + timeout):
                return False

    def _long_cmd_write(self, cmd: int, p1: int, p2: int, p3: int = 0, p4: int = 0):
        data1 = struct.pack("<H", cmd)
        data1 += struct.pack(">HI", p1, p2)
        data2 = struct.pack(">II", p3, p4)
        log.debug(f'l_cmd_w {0x9d00:#x} {data1.hex()}')
        log.debug(f'l_cmd_w {0x1d08:#x} {data2.hex()} ')
        self._dev.ctrl_transfer(0x41, 0x45, 0x78, 0x9d00, data1)
        self._dev.ctrl_transfer(0x41, 0x45, 0x78, 0x1d08, data2)
        self._block_until_camera_ready()

    def _long_cmd_read(self, cmd: int, p1: int, p2: int = 0, p3: int = 0, dataLen: int = 2):
        data1 = struct.pack("<H", cmd)
        data1 += struct.pack(">HI", p1, p2)
        data2 = struct.pack(">II", p3, dataLen)
        log.debug(f'l_cmd_r {0x9d00:#x} {data1.hex()}')
        log.debug(f'l_cmd_r {0x1d08:#x} {data2.hex()} ')
        self._dev.ctrl_transfer(0x41, 0x45, 0x78, 0x9d00, data1)
        self._dev.ctrl_transfer(0x41, 0x45, 0x78, 0x1d08, data2)
        self._block_until_camera_ready()
        log.debug(f'l_cmd_r {0x1d10:#x} ...')
        res = self._dev.ctrl_transfer(0xC1, 0x44, 0x78, 0x1d10, dataLen)
        return bytes(res)

    def _standard_cmd_write(self, cmd: int, cmd_addr: int = 0, data: bytes = b'\x00', dataLen: int = -1):
        if dataLen == -1:
            dataLen = len(data)

        # If there is no payload, send the 8 byte command immediately
        if (dataLen == 0 or data == b'\x00'):
            # send 1d00 with cmd
            d = struct.pack("<H", cmd)
            d += struct.pack(">I2x", cmd_addr)
            log.debug(f's_cmd_w {0x1d00:#x} ({len(d):2}) {d.hex()}')
            self._dev.ctrl_transfer(0x41, 0x45, 0x78, 0x1d00, d)
            self._block_until_camera_ready()
            return

        outer_chunk_size = 0x100
        inner_chunk_size = 0x40

        # A "camera command" can be 256 bytes long max, but we can split the data and
        # send more with an incremented address parameter (only spi_read/write actually uses that afaik)
        for i in range(0, dataLen, outer_chunk_size):
            outer_chunk = data[i:i+outer_chunk_size]

            # Send initial "camera command"
            initial_data = struct.pack("<H", cmd)
            initial_data += struct.pack(">IH", cmd_addr + i, len(outer_chunk))
            log.debug(f's_cmd_w {0x9d00:#x} ({len(initial_data):2}) {initial_data.hex()}')
            self._dev.ctrl_transfer(0x41, 0x45, 0x78, 0x9d00, initial_data)
            self._block_until_camera_ready()

            # Each vendor control transfer can be 64 bytes max. Split up and send with incrementing wIndex value
            for j in range(0, len(outer_chunk), inner_chunk_size):
                inner_chunk = outer_chunk[j:j+inner_chunk_size]
                to_send = len(outer_chunk) - j

                # The logic for splitting up long vendor requests is a bit weird
                # I just reimplemented it like Infiray did according to the USB trace. Don't want to cause unnecessary problems
                if (to_send <= 8):
                    log.debug(f's_cmd_w {(0x1d08 + j):#x} ({len(inner_chunk):2}) {inner_chunk.hex()}')
                    self._dev.ctrl_transfer(0x41, 0x45, 0x78, 0x1d08 + j, inner_chunk)
                    self._block_until_camera_ready()
                elif (to_send <= 64):
                    log.debug(f's_cmd_w {(0x9d08 + j):#x} ({len(inner_chunk[:-8]):2}) {inner_chunk[:-8].hex()}')
                    log.debug(
                        f's_cmd_w {(0x1d08 + j + to_send - 8):#x} ({len(inner_chunk[-8:]):2}) {inner_chunk[-8:].hex()}')
                    self._dev.ctrl_transfer(0x41, 0x45, 0x78, 0x9d08 + j, inner_chunk[:-8])
                    self._dev.ctrl_transfer(0x41, 0x45, 0x78, 0x1d08 + j + to_send - 8, inner_chunk[-8:])
                    self._block_until_camera_ready()
                else:
                    log.debug(f's_cmd_w {(0x9d08 + j):#x} ({len(inner_chunk):2}) {inner_chunk.hex()}')
                    self._dev.ctrl_transfer(0x41, 0x45, 0x78, 0x9d08 + j, inner_chunk)

    # pretty similar to _standard_cmd_write, but a bit simpler

    def _standard_cmd_read(self, cmd: int, cmd_addr: int = 0, dataLen: int = 0) -> bytes:
        if dataLen == 0:
            return b''

        result = b''
        outer_chunk_size = 0x100
        # A "camera command" can be 256 bytes long max, but we can split the data and
        # read more with an incremented address parameter (only spi_read/write actually uses that afaik)
        for i in range(0, dataLen, outer_chunk_size):
            to_read = min(dataLen - i, outer_chunk_size)
            # Send initial "camera command"
            initial_data = struct.pack("<H", cmd)
            initial_data += struct.pack(">IH", cmd_addr + i, to_read)
            log.debug(f's_cmd_r {0x1d00:#x} ({len(initial_data):2}) {initial_data.hex()}')
            self._dev.ctrl_transfer(0x41, 0x45, 0x78, 0x1d00, initial_data)
            self._block_until_camera_ready()

            # read request (USB: 0xC1, 0x44)
            log.debug(f's_cmd_r {0x1d08:#x} ({to_read:2}) ...')
            res = self._dev.ctrl_transfer(0xC1, 0x44, 0x78, 0x1d08, to_read)
            result += bytes(res)

        return result

    def pseudo_color_set(self, preview_path: int, color_type: PseudoColorTypes):
        # preview_path probably gets packed right after the command, but both RevEng insights are inconclusive
        self._standard_cmd_write((CmdCode.pseudo_color | CmdDir.SET), preview_path, struct.pack("<B", color_type))

    def pseudo_color_get(self, preview_path: int = 0) -> PseudoColorTypes:
        res = self._standard_cmd_read(CmdCode.pseudo_color, preview_path, 1)
        return PseudoColorTypes(int.from_bytes(res, 'little'))

    def set_prop_tpd_params(self, tpd_param: PropTpdParams, value: int):
        self._long_cmd_write(CmdCode.prop_tpd_params | CmdDir.SET, tpd_param, value)

    def get_prop_tpd_params(self, tpd_param: PropTpdParams) -> int:
        res = self._long_cmd_read(CmdCode.prop_tpd_params, tpd_param)
        return struct.unpack(">H", res)[0]

    def get_device_info(self, dev_info: DeviceInfoType):
        res = self._standard_cmd_read(CmdCode.get_device_info, dev_info, 8)
        return res
