# InfiRay P2 Pro Viewer

:warning: **[WIP]**  
See [below](#roadmap) for a roadmap.

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
The cheapest vendor in Germany appears to be [Peargear](https://www.pergear.de/products/infiray-p2-pro?ref=067mg).  
Pergear also has [an international shop](https://www.pergear.com/products/infiray-p2-pro?ref=067mg) for other countries, but I'm not sure if they're the cheapest there.

## Additional Resources
- [Review and teardown video by mikeselectricstuff](https://www.youtube.com/watch?v=YMQeXq1ujn0)
- [Extensive review thread by Fraser](https://www.eevblog.com/forum/thermal-imaging/review-infiray-p2-pro-thermal-camera-dongle-for-android-mobile-phones/)
- [General discussion thread with some interesting resources](https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/)


## Roadmap
- [ ] USB Vendor Commands
    - [x] Read/Write commands
        - [x] "standard" cmd
        - [x] "long" cmd
        - [x] wait for camera ready
    - [x] Pseudo color 
    - [ ] NUC shutter control (auto/manual/trigger)
    - [ ] High/low temperature range
    - [ ] Other parameters (emissivity, distance, etc)
    - [ ] Switch to actual raw sensor readings?
    - [ ] Recalibrate lens?
    - [ ] Remaining (less relevant) commands
- [ ] Recording
    - [ ] Still image
        - [ ] JPEG and radiometry data in one file
            - [ ] Standardized format? R-JPEG?
        - [ ] Metadata (rotation, camera settings, location?, etc)
    - [ ] Video
        - [x] MKV file with radiometry data as second lossless video track
        - [x] Audio
        - [ ] Metadata
        - [ ] Rotation (on-the-fly possible? :D)
        - [ ] Render overlays into video (scale, min/max/center temps, etc)
        - [ ] Timelapse?
        - [ ] Min/Max/Center temperature in subtitles? :D
        - [ ] Standardized video format? (don't know any)
    - [ ] Find / build tool to analyze recordings later (or export to other formats)
    - [ ] Virtual webcam output with temperature scale overlays?
- [ ] GUI
    - [ ] Display video stream
    - [ ] Overlays
        - [ ] Temperature scale
        - [ ] Min/max/center temperature
        - [ ] Cursor hover temperature
    - [ ] Palette selection
    - [ ] Shutter control
    - [ ] Gain selection (camera temperature range)
    - [ ] Parameters (emissivity, distance, etc)
    - [ ] Recording controls (take picture, start/stop video, recording indicator and time)
    - [ ] Image rotation / flip
    - [ ] Manually set min/max range (probably need to apply own pseudo color from raw temperature data)
    - [ ] Own analysis controls (points, lines, rectangles, etc)
    - [ ] Log measurements to CSV
    - [ ] Plot measurements
    - [ ] ...
- [ ] Documentation
    - [ ] How to use
    - [ ] USB vendor command protocol
    - [ ] My video format (if I don't find a more standardized one)
    - [ ] P2Pro Android app JPEG file format, that has radiometry data embedded
- Very long-term plans:
    - Small device with a socket for the P2 Pro to convert it into a hand-held device
    - Android App
