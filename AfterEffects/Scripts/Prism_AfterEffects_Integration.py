import os
import sys
import platform
import shutil

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_AfterEffects_Integration(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin
        #C:\Users\%USERNAME%\AppData\Roaming\Adobe\CEP\extensions
        if platform.system() == "Windows":
            self.examplePath = self.getAfterEffectsPath()
    
    
    @err_catcher(name=__name__)
    def getAfterEffectsPath(self): 
        return (os.environ["userprofile"] + r"\AppData\Roaming\Adobe\CEP\extensions")



    @err_catcher(name=__name__)
    def getExecutable(self):
        execPath = ""
        if platform.system() == "Windows":
            defaultpath = os.path.join(r"C:\Program Files\Adobe\Adobe After Effects 2021\Support Files", "AfterFX.exe")
            if os.path.exists(defaultpath):
                execPath = defaultpath
        return execPath

    def addIntegration(self, installPath):
        pass

    def removeIntegration(self, installPath):
        pass

    def updateInstallerUI(self, userFolders, pItem):
        pass

    def installerExecute(self, afterEffectsItem, result):
        pass