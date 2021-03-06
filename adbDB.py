#!/usr/bin/python
# -*- coding: utf-8 -*-	
import os, platform, re, sys

from subprocess import PIPE, Popen

SDK_PATH = "/opt/android-sdk/"
OS = platform.system()

# Command line to control adb
def cmdline(command):
	process = Popen(args=command, stdout=PIPE, shell=True)
	return process.communicate()[0].decode("UTF-8")
	
if (OS == 'Windows'):
	currentPath = cmdline('echo %CD%').rstrip("\n").rstrip("\r")
else:
	currentPath = cmdline('pwd').rstrip("\n").rstrip("\r")

# Pushing a file to selected package
def pushFile(selectedDevice, selectedPackage, selectedFile):
	fileCurrentPath = currentPath+"/"+selectedFile
	if (os.path.exists(fileCurrentPath)):
		cmdline("{0} -s {1} shell run-as {2} chmod 666 databases/{3}".format(adb, selectedDevice, selectedPackage, selectedFile))
		cmdline("{0} -s {1} push {3} /data/data/{2}/databases/{3}".format(adb, selectedDevice, selectedPackage, selectedFile))
		cmdline("{0} -s {1} shell run-as {2} chmod 600 databases/{3}".format(adb, selectedDevice, selectedPackage, selectedFile))
		print("Done!")
	else:
		print("File not found!")
		
	

# Makeing widows users will see the messages!
def doExit(exit=1):
	c = "1"
	while (c == "1"):
		c = input("Press ENTER to continue...")
	if(exit == 1):
		raise SystemExit

# Get some string from cmd result and make a clean array
def makeCleanArray(text,splitCndition, start=0, replaces=[]):
	
	text = text.rstrip()
	if (len(replaces) > 0):
		for rl in replaces:
			text = text.replace(rl, "")
	output = text.split(splitCndition)
	
	return output[start:]

# Ask the user in which device to use
def selectDevice():
	devices = cmdline("%s devices" % adb)
	devices = [device for device in devices if device != '']
	devices = makeCleanArray(cmdline("%s devices" % adb),"\n",1,[" ", "\tdevice","\r"])
	userInput = 0
	if (len(devices) == 0):
		print("No available devices")
		doExit()
		
	if (len(devices) == 1):
		model = cmdline("%s -s %s shell getprop ro.product.model" % (adb, devices[0])).rstrip("\n").rstrip("\r")
		print("## Device %s - %s selected! ##" % (devices[0], model))
		return devices[0]
		
	print("# Please select a device:")
	i=1
	for device in devices:
		model = cmdline("%s -s %s shell getprop ro.product.model" % (adb, device))
		print("%d) %s - %s" % (i, device, model.rstrip("\n")))
		i = i + 1
	while (True):
		userInput = input(">> ")
		try:
			userInput = int(userInput)
			if (userInput > len(devices)):
				print("Device doesn't exists, try again")
			else:
				return devices[userInput-1]
				
		except:
			print("Inavlid input, please insert a valid number!")
		
		
# Ask the user which package to use
def selectPackage(device):
	androidSdkVersion = int(cmdline("%s -s %s shell getprop ro.build.version.sdk" % (adb, device)))
	
	if (androidSdkVersion > 15):
		packages = cmdline("%s -s %s shell pm list packages -3 -i" % (adb, device))
	else:
		packages = cmdline("%s -s %s shell pm list packages -3" % (adb, device))
		
	packages = makeCleanArray(packages, "\n", 0, ["\r",""])

	newPackages = []
	if (len(packages) == 0):
		print("No available packages")
		doExit()
	
	if (len(packages) == 1):
		print("## Package %s selected! ##" % packages[0])
		return packages[0]

	print("# Please select a package:")
	i=1
	for package in packages:
		if (androidSdkVersion > 15):
			if (package.find("installer=null") != -1):
				newPackages.append(package.replace("installer=null", "").replace(" ", "").replace("package:",""))
				print("%d) %s" % (i, newPackages[i-1]))
				i = i + 1
		else:
			newPackages.append(package.replace(" ", "").replace("package:",""))
			print("%d) %s" % (i, newPackages[i-1]))
			i = i + 1

	while(True):
		userInput = input(">> ")
		try:
			userInput = int(userInput)
			if (userInput > len(newPackages)):
				print("Package doesn't exists, try again")
			else:
				return newPackages[userInput-1]
				
		except:
			print("Inavlid input, please insert a valid number!")


# Ask the user which file to select
def selectFile(device, package):
	res = cmdline("%s -s %s shell run-as %s ls databases/" % (adb, device, package))
	
	if (res.find("is not debuggable") != -1):
		print("This package is not debuggale!")
		doExit()
		
	files =	makeCleanArray(res, "\n",0,["","\r"])

	if (len(files) == 1 and files[0] == ""):
		print("No available files")
		doExit()	
		
	if (len(files) == 2):
		if (files[0].find(".db-journal")>-1):
			del(files[0])
		print("## file %s selected! ##" % files[0])
		return files[0]
	
	newFiles = []
	print("# Please select a file:")
	i=1
	for fl in files:
		if (fl.find(".db-journal") == -1):
			newFiles.append(fl)
			print("%d) %s" %(i, fl))
			i = i +1
			
	while(True):
		userInput = input(">> ")
		try:
			userInput = int(userInput)
			if (userInput > len(newFiles)):
				print("File doesn't exists, try again")
			else:
				return newFiles[userInput-1]
				
		except:
			print("Inavlid input, please insert a valid number!")
	
def mainProgram():
	os.system(['clear','cls'][os.name == 'nt'])
	flag = True
	dbExists = False
	selectedDevice  = selectDevice()
	selectedPackage = selectPackage(selectedDevice)
	selectedFile = selectFile(selectedDevice, selectedPackage)
	
	print("# Press '1' to get the file")
	print("# Press '2' to remove it from device")
	if (os.path.exists(currentPath+"/"+selectedFile) == True):
		print("# Press '3' to push the file")
		dbExists = True
	while(flag):
		userInput = input(">> ")
		try:
			userInput = int(userInput)
			if (userInput == 1): 
				cmdline("{0} -s {1} shell run-as {2} chmod 666 databases/{3}".format(adb, selectedDevice, selectedPackage, selectedFile))
				cmdline("%s -s %s pull /data/data/%s/databases/%s" % (adb, selectedDevice, selectedPackage, selectedFile))
				cmdline("{0} -s {1} shell run-as {2} chmod 600 databases/{3}".format(adb, selectedDevice, selectedPackage, selectedFile))
				flag = False
				if (OS == 'Windows'):
					print("Downloaded!, saved as: %s\%s" % (cmdline("echo %CD%").rstrip("\n").rstrip("\r"),selectedFile))
				else:
					print("Downloaded!, saved as: %s/%s" % (cmdline("pwd").rstrip("\n").rstrip("\r"),selectedFile))
			elif (userInput == 2):
				cmdline("{0} -s {1} shell run-as {2} rm databases/{3} databases/{3}-journal".format(adb, selectedDevice, selectedPackage, selectedFile))
				flag = False
				print("Removed!")
			elif ((userInput == 3) and (dbExists == True)):
				flag = False
				pushFile(selectedDevice, selectedPackage, selectedFile)
			else:
				print("What?! try again")
		except:
			if (flag == True):
				print("Inavlid input, please insert a valid number!")
		doExit(0)
		mainProgram()
	
	
if __name__=="__main__":
	if (os.path.exists(SDK_PATH + "/platform-tools/")):
		adb = SDK_PATH + "/platform-tools/adb"
		if (OS == 'Windows'):
			adb = adb + ".exe"
				
		mainProgram();
		
	else:
		print("Please launch the 'Android SDK Manager' and download Platform Tools!")
		doExit();
