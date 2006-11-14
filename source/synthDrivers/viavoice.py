import time
import thread
import os
import _winreg
import ctypes
import debug

description="IBM ViaVoice Outloud (ibmeci50.dll)"

curVoice=1
#'SOFTWARE\\IBM\\ViaVoice\\Outloud Runtime\\En_US'

#Constants

#Synth parameters
eciSynthMode=0
eciDictionary=3
eciNumDeviceBlocks=13
eciSizeDeviceBlocks=14
#voice parameters
eciGender=0
eciHeadSize=1
eciPitchBaseline=2
eciPitchFluctuation=3
eciRoughness=4
eciBreathiness=5
eciSpeed=6
eciVolume=7
#Index types
eciIndexReply=2
#Callback return values
eciDataNotProcessed=0
eciDataProcessed=1
eciDataAbort=2

def getInstallPath():
	try:
		key_outloudRuntime=_winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,'SOFTWARE\\IBM\\ViaVoice\\Outloud Runtime')
		lang=_winreg.EnumKey(key_outloudRuntime,0)
		key_lang=_winreg.OpenKey(key_outloudRuntime,lang)
		(path,t)=_winreg.QueryValueEx(key_lang,'path')
		return path
	except:
		debug.writeException("viavoice install path")
		return None

def check():
	if getInstallPath() is not None:
		return True
	else:
		return False

class synthDriver(object):

	def __init__(self):
		self.dll=ctypes.windll.LoadLibrary(os.path.join(getInstallPath(),'ibmeci50.dll'))
		self.handle=self.dll.eciNew()
		self.dll.eciSetParam(self.handle,eciSynthMode,1)
		self.dll.eciSetParam(self.handle,eciDictionary,1)
		#self.keepWatching=True
		#thread.start_new_thread(self.indexWatcher,())

	def __del__(self):
		self.dll.eciDelete(self.handle)

	def getLastIndex(self):
		self.dll.eciSpeaking(self.handle)
		index=self.dll.eciGetIndex(self.handle)
		debug.writeMessage("viavoice getLastIndex %s"%index)
		return index

	def getRate(self):
		rate=self.dll.eciGetVoiceParam(self.handle,0,eciSpeed)-30
		return rate

	def getPitch(self):
			return self.dll.eciGetVoiceParam(self.handle,0,eciPitchBaseline)

	def getVolume(self):
		return self.dll.eciGetVoiceParam(self.handle,0,eciVolume)

	def getVoice(self):
		global curVoice
		return curVoice

	def getVoiceNames(self):
		voiceNames=[]
		for v in range(1,9):
			buf=ctypes.create_string_buffer(30)
			self.dll.eciGetVoiceName(self.handle,v,buf)
			voiceNames.append(buf.value)
		return voiceNames

	def getLastIndex(self):
		self.dll.eciSpeaking(self.handle)
		return self.dll.eciGetIndex(self.handle)

	def setRate(self,rate):
		self.dll.eciSetVoiceParam(self.handle,0,eciSpeed,rate+30)

	def setPitch(self,value):
		self.dll.eciSetVoiceParam(self.handle,0,eciPitchBaseline,value)

	def setVolume(self,value):
		self.dll.eciSetVoiceParam(self.handle,0,eciVolume,value)

	def setVoice(self,value):
		global curVoice
		self.dll.eciCopyVoice(self.handle,value,0)
		curVoice=value

	def speakText(self,text,wait=False,index=None):
		try:
			text=text.encode("iso-8859-1","ignore")
		except:
			return
		if index is not None:
			res=self.dll.eciInsertIndex(self.handle,index)
			debug.writeMessage("viavoice speak text index %s"%index)
		self.dll.eciAddText(self.handle,text)
		self.dll.eciSynthesize(self.handle)
		if wait:
			self.dll.eciSynchronize(self.handle)

	def cancel(self):
		try:
			if self.dll.eciSpeaking(self.handle):
				self.dll.eciStop(self.handle)
		except:
			pass

