#!/usr/bin/python
# -*- coding: utf-8 -*-	
import os, platform, re
from subprocess import PIPE, Popen

SDK_PATH = "/opt/android-sdk/"
OS = platform.system()

def cmdline(command):
	process = Popen(args=command, stdout=PIPE, shell=True)
	return process.communicate()[0].decode("ASCII")

if __name__=="__main__":
	deviceList = []
	if (os.path.exists(SDK_PATH + "platform-tools/")):
		platfromtools = SDK_PATH + "platform-tools/"
		if (OS == 'Windows'):
			adb = platfromtools + "adb.exe"
			sqlite = platfromtools + "sqlite3.exe"
		else:
			adb = platfromtools + "adb"
			sqlite = platfromtools + "sqlite3"
		
		devices = cmdline(adb + " devices").split("\n")[1:]
		devices = [device for device in devices if device != '']
		
		print("Please select a device:\n")
		i=1
		for device in devices:
			curDevice = device.split("\t")[0]
			model = cmdline('%s -s %s shell "getprop ro.product.model"' % (adb, curDevice))
			deviceList.append(curDevice)
			print("%d) %s - %s" % (i, curDevice, model.rstrip("\n")))
			i = i + 1
			
			
		userInput = int(input("Enter number of device: "))
		selectedDevice = deviceList[userInput - 1]
		
		packageList = cmdline("%s -s %s shell pm list packages -3 -i | grep null | sed 's/package://' | sed 's/installer=null//'" % (adb, selectedDevice)).strip().replace("\r","").replace(" ", "").split("\n")
		print("Please select a package: ")
		i = 1
		for pk in packageList:
			print("%d) %s" % (i, pk))
			i = i + 1 
			
		package = packageList[int(input("Enter number of package: ")) - 1]
		print(package)
		
		listFiles = cmdline("%s -s %s shell run-as %s ls databases/" % (adb, selectedDevice, package)).rstrip("\n").replace("\r", "").split("\n")
		
		print("Select file: ");
		i=1
		for fl in listFiles:
			if (fl.find("-journal") == -1):
				print("%d) %s" % (i, fl))
				i = i + 1
			
		userInput = int(input("Enter number of file: "))
		selectedFile = listFiles[userInput - 1]
		
		print("To get the file press '1', to remove it press '2'")
		userInput = int(input("number: "))
		if (userInput == 1):
			cmd = "{0} -s {1} shell run-as {2} cp databases/{3} /sdcard/".format(adb, selectedDevice, package, selectedFile)
			cmdline(cmd)
			cmdline("%s -s %s pull /sdcard/%s" % (adb, selectedDevice, selectedFile))
			cmdline("%s -s %s shell rm /sdcard/%s" % (adb, selectedDevice, selectedFile))
			print("Done!, saved as: %s/%s" % (cmdline("pwd").replace("\n",""),selectedFile))
		else:
			cmd = "{0} -s {1} shell run-as {2} rm databases/{3} databases/sdcard{3}-journal".format(adb, selectedDevice, package, selectedFile)
			cmdline(cmd)
			print("Removed!")
		
	else:
		print("Please launch the 'Android SDK Manager' and download Platform Tools!")
