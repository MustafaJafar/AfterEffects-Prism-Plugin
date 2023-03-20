import os
import subprocess
import platform

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_AfterEffects_externalAccess_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

    @err_catcher(name=__name__)
    def getAutobackPath(self, origin, tab):
        autobackpath = ""
        if platform.system() == "Windows":
            autobackpath = "" #os.path.join(os.getenv("USERPROFILE"), "Documents", "Adobe","After Effects 2021")

        fileStr = "AfterEffects Scene File ("
        for i in self.sceneFormats:
            fileStr += "*%s " % i

        fileStr += ")"

        return autobackpath, fileStr

    @err_catcher(name=__name__)
    def projectBrowser_loadUI(self, origin): #origin : main ui
        if self.core.appPlugin.pluginName == "Standalone":
            aeMenu = QMenu("After Effects")
            aeAction = QAction("Connect", origin)
            aeAction.triggered.connect(lambda: self.connectToAfterEffects(origin))
            aeMenu.addAction(aeAction)
            origin.menuTools.insertSeparator(origin.menuTools.actions()[-2])
            origin.menuTools.insertMenu(origin.menuTools.actions()[-2], aeMenu)

    @err_catcher(name=__name__)
    def customizeExecutable(self, origin, appPath, filepath):
        self.connectToAfterEffects(origin, filepath=filepath)
        return True

    @err_catcher(name=__name__)
    def connectToAfterEffects(self, origin, filepath=""):
        pythonPath = self.core.getPythonPath(executable="Prism Project Browser")

        menuPath = os.path.join(
            self.core.prismRoot,
            "Plugins",
            "Apps",
            "AfterEffects",
            "Scripts",
            "Prism_AfterEffects_MenuTools.py",
        )
        subprocess.Popen([pythonPath, menuPath, "Tools", filepath])
