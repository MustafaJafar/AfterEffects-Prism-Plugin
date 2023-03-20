import os
import sys
import platform


prismRoot = os.getenv("PRISM_ROOT")
if not prismRoot:
    prismRoot = "C:/Prism"

sys.path.append(os.path.join(prismRoot, "Scripts"))

if sys.version[0] == "2":
    sys.path.append(os.path.join(prismRoot, "PythonLibs", "Python27"))
    sys.path.append(os.path.join(prismRoot, "PythonLibs", "Python27", "PySide"))
else:
    sys.path.append(os.path.join(prismRoot, "PythonLibs", "Python37"))
    sys.path.append(os.path.join(prismRoot, "PythonLibs", "Python37", "PySide"))


import PrismCore

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *


qapp = QApplication.instance()
if qapp == None:
    qapp = QApplication(sys.argv)

pcore = PrismCore.PrismCore(app="AfterEffects")

if hasattr(pcore.appPlugin, "aeApp") or platform.system() == "Darwin":
    curPrj = pcore.getConfig("globals", "current project")

    result = False
    if sys.argv[1] == "Tools":
        result = pcore.appPlugin.openAfterEffectsTools()
    elif sys.argv[1] == "SaveVersion":
        pcore.saveScene()
    elif sys.argv[1] == "SaveComment":
        result = pcore.saveWithComment()
    elif sys.argv[1] == "Import":
        result = pcore.appPlugin.importImages(origin=pcore)
    elif sys.argv[1] == "Export":
        result = pcore.appPlugin.exportImage()
    elif sys.argv[1] == "ProjectBrowser":
        result = pcore.projectBrowser()
    elif sys.argv[1] == "Settings":
        result = pcore.prismSettings()
    

    if len(sys.argv) > 2:
        pcore.appPlugin.openScene(origin=pcore, filepath=sys.argv[2])

    if result:
        qapp.exec_()
    
    
