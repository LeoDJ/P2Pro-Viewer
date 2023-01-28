# InfiRay P2 Pro Viewer

[WIP]

This project aims to be an open-source image viewer and API for the InfiRay P2 Pro thermal camera module.

The communication protocol was reverse-engineered, to avoid needing to include the proprietary precompiled InfiRay libraries.

**Disclaimer**: This is my first big Python multi-module project. So there are bound to be horrific architectural decisions and many other beginner's mistakes. Please excuse that.  
The premise is to get to the first milestone with as little premature optimization as possible, otherwise I would never arrive there.

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

## Where to buy
The cheapest vendor in Germany appears to be Peargear. [Link to the product page](https://www.pergear.de/products/infiray-p2-pro?ref=067mg).

## Additional Resources
- [Review and teardown video by mikeselectricstuff](https://www.youtube.com/watch?v=YMQeXq1ujn0)
- [Extensive review thread by Fraser](https://www.eevblog.com/forum/thermal-imaging/review-infiray-p2-pro-thermal-camera-dongle-for-android-mobile-phones/)
- [General discussion thread with some interesting resources](https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/)