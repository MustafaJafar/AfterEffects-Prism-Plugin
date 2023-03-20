
import os
import sys
import platform
import subprocess
import ae_TaskSelection as TaskSelection
#import TaskSelection
from AE_PyJsx import *

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *



if platform.system() == "Windows":
    import win32com.client

from PrismUtils.Decorators import err_catcher as err_catcher


class Prism_AfterEffects_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin
        self.win = platform.system() == "Windows"

    @err_catcher(name=__name__)
    def startup(self, origin):
        origin.timer.stop()

        with (
            open(
                os.path.join(
                    self.core.prismRoot,
                    "Plugins",
                    "Apps",
                    "AfterEffects",
                    "UserInterfaces",
                    "AfterEffectsStyleSheet",
                    "AfterEffects.qss",
                ),
                "r",
            )
        ) as ssFile:
            ssheet = ssFile.read()

        ssheet = ssheet.replace(
            "qss:",
            os.path.join(
                self.core.prismRoot,
                "Plugins",
                "Apps",
                "AfterEffects",
                "UserInterfaces",
                "AfterEffectsStyleSheet",
            ).replace("\\", "/")
            + "/",
        )
        ssheet = ssheet.replace("#c8c8c8", "rgb(35, 35, 35)")#.replace("#727272", "rgb(83, 83, 83)").replace("#5e90fa", "rgb(89, 102, 120)").replace("#505050", "rgb(70, 70, 70)")
        ssheet = ssheet.replace("#a6a6a6", "rgb(145, 145, 145)")#.replace("#8a8a8a", "rgb(95, 95, 95)").replace("#b5b5b5", "rgb(155, 155, 155)").replace("#999999", "rgb(105, 105, 105)")
        ssheet = ssheet.replace("#9f9f9f", "rgb(58, 58, 58)")#.replace("#b2b2b2", "rgb(58, 58, 58)").replace("#aeaeae", "rgb(65, 65, 65)").replace("#c1c1c1", "rgb(65, 65, 65)")

        qApp.setStyleSheet(ssheet)
        appIcon = QIcon(
            os.path.join(
                self.core.prismRoot, "Scripts", "UserInterfacesPrism", "p_tray.png"
            )
        )
        qApp.setWindowIcon(appIcon)

        if self.win:
            try:
                # CS6: .60, CC2015: .90, CC2017: 14.0 CC2021: 18.0
                # it will get the version automatically
                self.aeApp = AE_JSInterface(aeVersion = "" ,returnFolder = os.path.join(os.path.expanduser('~'), "Documents", "temp")) #win32com.client.Dispatch("AfterFX.Application")
                ae_process = self.aeApp.ae_process_exist 
                
                if (not ae_process ): 
                    self.aeApp.openAE()
                    self.aeApp.waitingAELoading
                    
                    '''
                    if self.aeApp.waitingAELoading:
                        path = os.path.join(os.path.expanduser('~') , "Documents","Adobe","After Effects 2021" , "Untitled Project.aep").replace("\\","/")
                        self.aeApp.jsSaveAS(path)
                        self.aeApp.waitingAELoading
                    '''
                #self.core.popup(str(self.aeApp) + ae_process)

            except Exception as e:
                QMessageBox.warning(
                    self.core.messageParent,
                    "Warning",
                    "Could not connect to AfterEffects:\n\n%s" % str(e),
                )
                return False

        return False


    @err_catcher(name=__name__)
    def executeScript(self, origin, code, preventError=False):
        if preventError:
            try:
                return eval(code)
            except Exception as e:
                msg = "\npython code:\n%s" % code
                exec("raise type(e), type(e)(e.message + msg), sys.exc_info()[2]")
        else:
            return eval(code)


    @err_catcher(name=__name__)
    def onProjectBrowserStartup(self, origin):
        origin.actionStateManager.setEnabled(False)
        aeMenu = QMenu("After Effects", origin)
        aeAction = QAction("Open tools", origin)
        aeAction.triggered.connect(self.openAfterEffectsTools)
        aeMenu.addAction(aeAction)
        origin.menuTools.addSeparator()
        origin.menuTools.addMenu(aeMenu)


    @err_catcher(name=__name__)
    def exportImage(self):
        self.core.popup("Export is clicked!")

    @err_catcher(name=__name__)
    def importImages(self, origin):
        path = self.afterEffectsImportSource(origin)
        if (path):
            if (path[-1] == "0"):
                self.aeApp.jsImport(path[:-1])
            elif (path[-1] == "1"):
                self.aeApp.jsImportSequence(path[:-1])
        else : 
            self.core.popup("Nothing to import!")

        '''
        fString = "Please select an import option:"
        msg = QMessageBox(
            QMessageBox.NoIcon, "After Effect Import", fString, QMessageBox.Cancel
        )
        msg.addButton("Current pass", QMessageBox.YesRole)
        msg.addButton("All passes", QMessageBox.YesRole)
        msg.addButton("Layout all passes", QMessageBox.YesRole)
        self.core.parentWindow(msg)
        action = msg.exec_()

        if action == 0:
            path = self.afterEffectsImportSource(origin)
            if (path):
                self.aeApp.jsImport(path)
            else : 
                self.core.popup("Nothing to import!")

        elif action == 1:
            self.afterEffectsImportPasses(origin)
        elif action == 2:
            self.afterEffectsLayout(origin)
        else:
            return
        '''
    
    @err_catcher(name=__name__)
    def afterEffectsImportSource(self , origin): 
        ts = TaskSelection.TaskSelection(core=origin)
        origin.parentWindow(ts)
        ts.exec_()

        productPath = ts.productPath if ts.productPath else ""
        #self.core.popup(dir(ts))
        #isSequence = 
        #sourceData = origin.projectBrowser().compGetImportSource()
        #self.core.popup( '"Current pass" : ' + productPath)
        return productPath

    @err_catcher(name=__name__)
    def afterEffectsImportPasses(self , origin): 
        #sourceData = origin.projectBrowser().compGetImportPasses()
        self.core.popup('"All passes" was clicked')
    
    @err_catcher(name=__name__)
    def afterEffectsLayout(self , origin): 
        self.core.popup('"Layout all passes" was clicked')



    @err_catcher(name=__name__)
    def openScene(self, origin, filepath, force=False):
        if not force and os.path.splitext(filepath)[1] not in self.sceneFormats:
            return False

        if self.win:
            self.aeApp.jsOpenScene(filepath)


    @err_catcher(name=__name__)
    def getCurrentFileName(self, origin, path=True):
        try:
            if self.win:
                #doc = self.aeApp.jsGetActiveDocument()
                
                currentFileName = self.aeApp.jsGetActiveDocument() #doc.FullName
                
                if currentFileName is None:
                    raise

                if currentFileName.endswith("\n"):
                    currentFileName = currentFileName[:-1]

        except:
            currentFileName = ""

        if not path and currentFileName != "":
            currentFileName = os.path.basename(currentFileName)

        return currentFileName

    @err_catcher(name=__name__)
    def openAfterEffectsTools(self):
        self.dlg_tools = QDialog()

        lo_tools = QVBoxLayout()
        self.dlg_tools.setLayout(lo_tools)

        b_saveVersion = QPushButton("Save Version")
        b_saveComment = QPushButton("Save Extended")
        b_import = QPushButton("Import")
        b_export = QPushButton("Export")
        b_projectBrowser = QPushButton("Project Browser")
        b_settings = QPushButton("Settings")

        b_saveVersion.clicked.connect(self.core.saveScene)
        b_saveComment.clicked.connect(self.core.saveWithComment)
        b_import.clicked.connect(lambda: self.importImages(self.core))
        b_export.clicked.connect(self.exportImage)
        b_projectBrowser.clicked.connect(self.core.projectBrowser)
        b_settings.clicked.connect(self.core.prismSettings)

        lo_tools.addWidget(b_saveVersion)
        lo_tools.addWidget(b_saveComment)
        lo_tools.addWidget(b_import)
        lo_tools.addWidget(b_export)
        lo_tools.addWidget(b_projectBrowser)
        lo_tools.addWidget(b_settings)

        self.core.parentWindow(self.dlg_tools)
        self.dlg_tools.setWindowTitle("After Effects Prism")

        self.dlg_tools.show()

        self.core.projectBrowser()

        return True



    @err_catcher(name=__name__)
    def saveScene(self, origin, filepath, details={}):

        if self.win:
            if( not self.aeApp.ae_process_exist ): 
                self.core.popup("There is no active document in After Effects.")
                return False

            if "fileFormat" in details:
                filepath = os.path.splitext(filepath)[0] + details["fileFormat"]
            
            #self.core.popup(filepath)
            self.aeApp.jsSaveAS(filepath)
            
        else : 
            return ""

    @err_catcher(name=__name__)
    def getSceneExtension(self, origin):
        doc = self.core.getCurrentFileName()
        if doc != "":
            return os.path.splitext(doc)[1]

        return self.sceneFormats[0]
    @err_catcher(name=__name__)
    def onProjectChanged(self, origin):
        pass

    @err_catcher(name=__name__)
    def onSaveExtendedOpen(self, origin):
        origin.l_format = QLabel("Save as:")
        origin.cb_format = QComboBox()
        origin.cb_format.addItems(self.sceneFormats)
        curFilename = self.core.getCurrentFileName()
        if curFilename:
            ext = os.path.splitext(curFilename)[1]
            idx = self.sceneFormats.index(ext)
            if idx != -1:
                origin.cb_format.setCurrentIndex(idx)
        rowIdx = origin.w_details.layout().rowCount()
        origin.w_details.layout().addWidget(origin.l_format, rowIdx, 0)
        origin.w_details.layout().addWidget(origin.cb_format, rowIdx, 1)

    @err_catcher(name=__name__)
    def onGetSaveExtendedDetails(self, origin, details):
        details["fileFormat"] = origin.cb_format.currentText()

    @err_catcher(name=__name__)
    def onPrismSettingsOpen(self, origin):
        pass


    @err_catcher(name=__name__)
    def getFrameRange(self, origin):
        startframe = 1001 
        endframe = 1100
        return [startframe, endframe]

    @err_catcher(name=__name__)
    def setFrameRange(self, origin, startFrame, endFrame):
        pass

    