# InfiRay P2 Pro Viewer

[WIP]

This project aims to be an open-source image viewer and API for the InfiRay P2 Pro thermal camera module.

The communication protocol was reverse-engineered, to avoid needing to include the proprietary precompiled InfiRay libraries.

## Notices
### Windows
For sending vendor control transfers to the UVC camera in addition to opening the camera as a normal UVC camera, libusb needs to be installed as an upper filter driver.  
This can be installed relatively easily using Zadig.  
- Options > List all devices
- Select "USB Camera (Interface 0)"
- Scroll to "libusb-win32" and select "Install filter driver" from the dropdown besides "Replace driver"

Also, the camera video stream needs to be opened first before using the script to send commands to it, otherwise the call to libusb will just hang for whatever reason.

### Linux
Still needs to be tested, but should work™