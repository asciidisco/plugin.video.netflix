# Installing LibreElec, KODI, and Netflix on a Raspberry Pi

These instructions assume you have an unused Raspberry Pi and are starting from scratch. The steps will wipe whatever is on the Raspberry Pi's SD card.

This has been tested on a Raspberry Pi 3, but the steps are likely to be very similar if not the same for other models.

## Installation the latest Alpha LibreElec and KODI 18

* Download the [LibreElec USB-SD Creator](https://libreelec.tv/downloads/)
* Install the latest LibreElec stable version onto your Raspberry Pi's SD card using the USB-SD Creator 
* Insert the SD card into the Raspberry Pi and boot it
* Enable SSH and Samba (SMB) options when asked - make note of the default user and password
* Download the [latest LibreElec Alpha](https://forum.kodi.tv/showthread.php?tid=298461) (These instructions were tested using 0722, but the latest build should generally work)
* Connect to the Updates folder on the Raspberry Pi over SMB
* Copy the LibreElec Alpha .tar file to the Updates folder on the Raspberry Pi
* Reboot the Raspberry Pi - it should detect and install the alpha version
* Enable SSH and Samba (SMB) options when asked again
* Download the .zip of https://github.com/asciidisco/plugin.video.netflix from GitHub (click "Clone or Download" then "Download ZIP")
* Connect to the Downloads folder on the Raspberry Pi over SMB
* Copy the .zip file to the Downloads folder on the Raspberry Pi
* On KODI go to Add-ons, Install from zip file
* Navigate to the Downloads folder and select the zip file and install it
* Connect to the Raspberry Pi over SSH using the default user and password
* Run `wget http://nmacleod.com/public/libreelec/getwidevine.sh`
* Run `sh getwidevine.sh`
* Reboot the Raspberry Pi

The Netflix plugin should now be installed in Add-ons, and you should be able to stream Netflix content once you have logged in with a Netflix account.
