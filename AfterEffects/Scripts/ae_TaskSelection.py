'''
This works with original prism's folder hierarchy
'''
import os
import sys
import shutil

from json import dumps

from collections import OrderedDict

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    psVersion = 2
except:
    from PySide.QtCore import *
    from PySide.QtGui import *
    psVersion = 1


uiPath = os.path.join(os.path.dirname(__file__), "UserInterfaces")
if uiPath not in sys.path:
    sys.path.append(uiPath)

if psVersion == 1:
    import ae_TaskSelection_ui as TaskSelection_ui
else:
    import ae_TaskSelection_ui_ps2 as TaskSelection_ui

from PrismUtils.Decorators import err_catcher


class TaskSelection(QDialog, TaskSelection_ui.Ui_dlg_TaskSelection):
    productPathSet = Signal(object)

    def __init__(self, core, importState=None):
        QDialog.__init__(self)
        self.setupUi(self)
        self.core = core

        self.importState = importState
        self.productPath = None
        self.curEntity = None
        self.curTask = None
        self.adclick = False
        self.autoClose = True
        self.handleImport = True    
        self.preferredUnit = getattr(self.importState, "preferredUnit", "meter")
        self.importLocations = self.core.paths.getRenderProductBasePaths()
        #self.core.popup( self.importLocations)

        if len(self.importLocations) > 1:
            newImportPaths = OrderedDict([("all", "all")])
            newImportPaths.update(self.importLocations)
            self.importLocations = newImportPaths
        else:
            self.w_paths.setVisible(False)

        self.cb_paths.addItems(list(self.importLocations.keys()))
        if self.core.appPlugin.pluginName == "Standalone":
            self.b_custom.setVisible(False)

        self.tw_versions.setDragEnabled(True)

        self.versionLabels = [ "Name" , "AOV Pass" , "Version", "Comment", "Type", "Units", "User", "Date", "Path"]

        if len(self.importLocations) > 1:
            self.versionLabels.insert(4, "Location")

        self.tw_versions.setColumnCount(len(self.versionLabels))
        self.tw_versions.setHorizontalHeaderLabels(self.versionLabels)
        self.tw_versions.setColumnHidden(len(self.versionLabels) - 1, True)
        self.tw_versions.setColumnHidden(5,True)
        self.tw_versions.sortByColumn(0, Qt.DescendingOrder)

        if psVersion == 1:
            self.tw_versions.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        else:
            self.tw_versions.horizontalHeader().setSectionResizeMode(
                1, QHeaderView.Stretch
            )

        self.core.callback(
            name="onSelectTaskOpen", types=["curApp", "custom"], args=[self]
        )

        self.connectEvents()
        self.updateAssets()
        self.updateShots()

        navPath = self.core.getCurrentFileName()
        if self.importState:
            result = self.navigateToFile(os.path.split(self.importState.e_file.text())[0])
            if result:
                navPath = None
        
        self.navigateToFile(navPath)

    @err_catcher(name=__name__)
    def connectEvents(self):
        self.cb_paths.activated.connect(self.locationChanged)
        self.tbw_entity.currentChanged.connect(lambda x: self.entityClicked())
        self.tw_assets.itemExpanded.connect(self.aItemCollapsed)
        self.tw_assets.itemCollapsed.connect(self.aItemCollapsed)
        self.tw_assets.itemSelectionChanged.connect(self.entityClicked)
        self.tw_assets.mousePrEvent = self.tw_assets.mousePressEvent
        self.tw_assets.mousePressEvent = lambda x: self.mouseClickEvent(x, "a")
        self.tw_assets.mouseClickEvent = self.tw_assets.mouseReleaseEvent
        self.tw_assets.mouseReleaseEvent = lambda x: self.mouseClickEvent(x, "a")
        # 	self.tw_assets.mouseDClick = self.tw_assets.mouseDoubleClickEvent
        # 	self.tw_assets.mouseDoubleClickEvent = lambda x: self.mousedb(x,"a", self.tw_assets)

        self.tw_shots.itemExpanded.connect(self.sItemCollapsed)
        self.tw_shots.itemCollapsed.connect(self.sItemCollapsed)
        self.tw_shots.itemSelectionChanged.connect(self.entityClicked)
        self.tw_shots.mousePrEvent = self.tw_shots.mousePressEvent
        self.tw_shots.mousePressEvent = lambda x: self.mouseClickEvent(x, "s")
        self.tw_shots.mouseClickEvent = self.tw_shots.mouseReleaseEvent
        self.tw_shots.mouseReleaseEvent = lambda x: self.mouseClickEvent(x, "s")
        # 	self.tw_shots.mouseDClick = self.tw_shots.mouseDoubleClickEvent
        # 	self.tw_shots.mouseDoubleClickEvent = lambda x: self.mousedb(x,"s", self.tw_shots)

        self.lw_tasks.mousePrEvent = self.lw_tasks.mousePressEvent
        self.lw_tasks.mousePressEvent = lambda x: self.mouseClickEvent(x, "t")
        self.lw_tasks.mouseClickEvent = self.lw_tasks.mouseReleaseEvent
        self.lw_tasks.mouseReleaseEvent = lambda x: self.mouseClickEvent(x, "t")
        self.lw_tasks.itemSelectionChanged.connect(self.taskClicked)
        self.lw_tasks.doubleClicked.connect(
            lambda: self.loadVersion(None, currentVersion=True)
        )
        self.tw_versions.doubleClicked.connect(self.loadVersion)
        self.b_custom.clicked.connect(self.openCustom)

        self.tw_assets.customContextMenuRequested.connect(
            lambda pos: self.rclicked(pos, "assets")
        )
        self.tw_shots.customContextMenuRequested.connect(
            lambda pos: self.rclicked(pos, "shots")
        )
        self.lw_tasks.customContextMenuRequested.connect(
            lambda pos: self.rclicked(pos, "tasks")
        )
        self.tw_versions.customContextMenuRequested.connect(
            lambda pos: self.rclicked(pos, "versions")
        )
        self.tw_versions.mouseMoveEvent = self.mouseDrag

    @err_catcher(name=__name__)
    def mouseClickEvent(self, event, uielement):
        if QEvent != None:
            if event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    if uielement == "a":
                        index = self.tw_assets.indexAt(event.pos())
                        if index.data() == None:
                            self.tw_assets.setCurrentIndex(
                                self.tw_assets.model().createIndex(-1, 0)
                            )
                        self.tw_assets.mouseClickEvent(event)
                    elif uielement == "s":
                        index = self.tw_shots.indexAt(event.pos())
                        if index.data() == None:
                            self.tw_shots.setCurrentIndex(
                                self.tw_shots.model().createIndex(-1, 0)
                            )
                        self.tw_shots.mouseClickEvent(event)
                    elif uielement == "t":
                        index = self.lw_tasks.indexAt(event.pos())
                        if index.data() == None:
                            self.lw_tasks.setCurrentIndex(
                                self.lw_tasks.model().createIndex(-1, 0)
                            )
                        self.lw_tasks.mouseClickEvent(event)
            elif event.type() == QEvent.MouseButtonPress:
                if uielement == "a":
                    self.adclick = True
                    self.tw_assets.mousePrEvent(event)
                elif uielement == "s":
                    self.sdclick = True
                    self.tw_shots.mousePrEvent(event)
                elif uielement == "t":
                    self.lw_tasks.mousePrEvent(event)

    @err_catcher(name=__name__)
    def mousedb(self, event, tab, uielement):
        if tab == "a" and not self.adclick:
            pos = self.tw_assets.mapFromGlobal(QCursor.pos())
            item = self.tw_assets.itemAt(pos.x(), pos.y())
            if item is not None:
                item.setExpanded(not item.isExpanded())

        elif tab == "s":
            pos = self.tw_shots.mapFromGlobal(QCursor.pos())
            item = self.tw_shots.itemAt(pos.x(), pos.y())
            if item is not None:
                item.setExpanded(not item.isExpanded())

    # 		mIndex = uielement.indexAt(event.pos())
    # 		if mIndex.data() is not None and mIndex.parent().column() == -1:
    # 			uielement.setExpanded(mIndex, not uielement.isExpanded(mIndex))
    # 			uielement.mouseDClick(event)

    @err_catcher(name=__name__)
    def keyPressEvent(self, event):
        if self.autoClose or (event.key() != Qt.Key_Escape):
            super(TaskSelection, self).keyPressEvent(event)

    @err_catcher(name=__name__)
    def mouseDrag(self, event):
        if event.buttons() != Qt.LeftButton:
            return

        if getattr(self, "closing", False):
            return

        versions = [self.getCurSelection()]
        urlList = []
        for version in versions:
            url = "file:///%s" % version
            url = url.replace("\\", "/")
            urlList.append(QUrl(url))

        if len(urlList) == 0:
            return

        drag = QDrag(self)
        mData = QMimeData()

        mData.setUrls(urlList)
        mData.setData("text/plain", str(urlList[0].toLocalFile()).encode())
        drag.setMimeData(mData)

        drag.exec_()

    @err_catcher(name=__name__)
    def openCustom(self):
        startPath = os.path.dirname(self.getCurSelection())
        customFile = QFileDialog.getOpenFileName(
            self, "Select File to import", startPath, "All files (*.*)"
        )[0]
        customFile = self.core.fixPath(customFile)

        fileName = getattr(self.core.appPlugin, "fixImportPath", lambda x: x)(
            customFile
        )

        if fileName != "":
            result = self.setProductPath(path=fileName)
            if result:
                if self.autoClose:
                    self.close()
                elif self.handleImport:
                    sm = self.core.getStateManager()
                    sm.importFile(self.productPath)

    @err_catcher(name=__name__)
    def loadVersion(self, index, currentVersion=False):
        if currentVersion:
            self.tw_versions.sortByColumn(0, Qt.DescendingOrder)
            pathC = self.tw_versions.model().columnCount() - 1
            versionPath = self.tw_versions.model().index(0, pathC).data()
            if versionPath is None:
                return
        else:
            pathC = index.model().columnCount() - 1
            versionPath = index.model().index(index.row(), pathC).data()

        incompatible = []
        for i in self.core.unloadedAppPlugins.values():
            incompatible += getattr(i, "appSpecificFormats", [])

        if os.path.splitext(versionPath)[1] in incompatible:
            self.core.popup("This filetype is incompatible. Can't import the selected file.")
        else:
            result = self.setProductPath(path=versionPath)
            if result:
                if self.autoClose:
                    self.closing = True
                    self.close()
                elif self.handleImport:
                    sm = self.core.getStateManager()
                    sm.importFile(self.productPath)

    @err_catcher(name=__name__)
    def setProductPath(self, path):
        if self.importState:
            result = getattr(self.importState, "validateFilepath", lambda x: True)(path)
            if result is not True:
                self.core.popup(result)
                return

        self.productPath = path
        self.productPathSet.emit(path)
        return True

    @err_catcher(name=__name__)
    def rclicked(self, pos, listType):
        showInfo = False
        if listType == "assets":
            viewUi = self.tw_assets
            item = self.tw_assets.itemAt(pos)
            if not item or not item.data(0, Qt.UserRole):
                if not item:
                    self.tw_assets.setCurrentIndex(
                        self.tw_assets.model().createIndex(-1, 0)
                    )
                    self.updateTasks()
                path = self.core.assetPath
            else:
                path = item.data(0, Qt.UserRole)[0]["path"]

        elif listType == "shots":
            viewUi = self.tw_shots
            item = self.tw_shots.itemAt(pos)
            if not item or not item.data(0, Qt.UserRole):
                if not item:
                    self.tw_shots.setCurrentIndex(
                        self.tw_shots.model().createIndex(-1, 0)
                    )
                    self.updateTasks()
                path = self.core.getShotPath()
            else:
                path = item.data(0, Qt.UserRole)[0]["path"]

        elif listType == "tasks":
            viewUi = self.lw_tasks
            item = self.lw_tasks.itemAt(pos)
            if self.tbw_entity.tabText(self.tbw_entity.currentIndex()) == "Assets":
                entityItem = self.tw_assets.currentItem()
            else:
                entityItem = self.tw_shots.currentItem()

            if not entityItem:
                return

            if not item:
                self.lw_tasks.setCurrentRow(-1)
                if not entityItem.data(0, Qt.UserRole):
                    return

                entityPath = entityItem.data(0, Qt.UserRole)[0]["path"]
                #path = self.core.products.getProductPathFromEntityPath(entityPath)
                path = self.get2dRenderingPathFromEntityPath(entityPath)

                #self.core.popup("rclicked_path: "+  dumps(path))
                if not os.path.exists(path):
                    return
            else:
                path = item.data(Qt.UserRole)["locations"][0]

        elif listType == "versions":
            viewUi = self.tw_versions
            row = self.tw_versions.rowAt(pos.y())

            if row == -1:
                if self.tbw_entity.tabText(self.tbw_entity.currentIndex()) == "Assets":
                    entityItem = self.tw_assets.currentItem()
                else:
                    entityItem = self.tw_shots.currentItem()

                self.tw_versions.setCurrentIndex(
                    self.tw_versions.model().createIndex(-1, 0)
                )
                if self.lw_tasks.currentItem() is None:
                    return

                path = self.lw_tasks.currentItem().data(Qt.UserRole)["locations"][0]
            else:
                pathC = self.tw_versions.model().columnCount() - 1
                path = self.tw_versions.model().index(row, pathC).data()
                showInfo = True

        rcmenu = QMenu(viewUi)
        openex = QAction("Open in Explorer", viewUi)
        openex.triggered.connect(lambda: self.core.openFolder(path))
        rcmenu.addAction(openex)

        copAct = QAction("Copy path", viewUi)
        copAct.triggered.connect(lambda: self.core.copyToClipboard(path))
        rcmenu.addAction(copAct)

        if showInfo:
            useMaster = self.core.getConfig("globals", "useMasterVersion", dft=False, config="project")
            if useMaster:
                column = self.versionLabels.index("Version")
                version = self.tw_versions.item(row, column).text()
                if version.startswith("master"):
                    masterAct = QAction("Delete master", viewUi)
                    masterAct.triggered.connect(
                        lambda: self.core.products.deleteMasterVersion(path)
                    )
                    masterAct.triggered.connect(self.updateVersions)
                    rcmenu.addAction(masterAct)
                else:
                    masterAct = QAction("Set as master", viewUi)
                    masterAct.triggered.connect(
                        lambda: self.core.products.updateMasterVersion(path)
                    )
                    masterAct.triggered.connect(self.updateVersions)
                    rcmenu.addAction(masterAct)

            if "Location" in self.versionLabels:
                column = self.versionLabels.index("Location")
                location = self.tw_versions.item(row, column).text()
                if "local" in location and "global" not in location:
                    glbAct = QAction("Move to global", viewUi)
                    versionDir = os.path.dirname(os.path.dirname(path))
                    glbAct.triggered.connect(lambda: self.moveToGlobal(versionDir))
                    rcmenu.addAction(glbAct)

            infoAct = QAction("Show version info", viewUi)
            infoAct.triggered.connect(
                lambda: self.showVersionInfo(os.path.dirname(os.path.dirname(path)))
            )
            rcmenu.addAction(infoAct)

            infoPath = os.path.join(os.path.dirname(path), "versioninfo.yml")

            if not os.path.exists(infoPath):
                self.core.configs.findDeprecatedConfig(infoPath)

            depAct = QAction("Show dependencies", viewUi)
            depAct.triggered.connect(
                lambda: self.core.dependencyViewer(infoPath, modal=True)
            )
            rcmenu.addAction(depAct)

        self.core.callback("productSelectorContextMenuRequested", args=[self, viewUi, pos, rcmenu])
        rcmenu.exec_((viewUi.viewport()).mapToGlobal(pos))

    @err_catcher(name=__name__)
    def moveToGlobal(self, localPath):
        dstPath = self.core.convertPath(localPath, "global")

        if os.path.exists(dstPath):
            for root, folders, files in os.walk(dstPath):
                if files:
                    msg = "Found existing files in the global directory. Copy to global was canceled."
                    self.core.popup(msg)
                    return

            shutil.rmtree(dstPath)

        shutil.copytree(localPath, dstPath)

        try:
            shutil.rmtree(localPath)
        except:
            msg = "Could not delete the local file. Probably it is used by another process."
            self.core.popup(msg)

        self.updateVersions()

    @err_catcher(name=__name__)
    def showVersionInfo(self, path):
        vInfo = "No information is saved with this version."

        infoPath = os.path.join(path, "versioninfo.yml")

        iData = self.core.getConfig("information", configPath=infoPath)

        if iData:
            vInfo = ""
            for i in iData:
                i = i[0].upper() + i[1:]
                if i == "Version":
                    vInfo += "%s:\t\t\t%s\n" % (i, iData[i])
                else:
                    vInfo += "%s:\t\t%s\n" % (i, iData[i])

        self.core.popup(vInfo, title="Versioninfo", severity="info")

    @err_catcher(name=__name__)
    def locationChanged(self, location):
        task = version = None
        row = self.tw_versions.currentIndex().row()
        pathC = self.tw_versions.model().columnCount() - 1
        path = self.tw_versions.model().index(row, pathC).data()
        
        if path:
            task = self.lw_tasks.currentItem().text()
            version = self.tw_versions.model().index(row, 0).data()
        else:
            item = self.lw_tasks.currentItem()
            if item and item.data(Qt.UserRole):
                path = item.data(Qt.UserRole)["locations"][0]
                task = item.text()
            else:
                if self.tbw_entity.tabText(self.tbw_entity.currentIndex()) == "Assets":
                    entityItem = self.tw_assets.currentItem()
                else:
                    entityItem = self.tw_shots.currentItem()

                if entityItem and entityItem.data(0, Qt.UserRole):
                    path = entityItem.data(0, Qt.UserRole)[0]["path"]

        self.updateAssets()
        self.updateShots()

        if not path or not self.navigateToFile(path, task=task, version=version):
            self.navigateToFile(self.core.getCurrentFileName())

    @err_catcher(name=__name__)
    def entityClicked(self, entityType=None):
        if entityType is None:
            if self.tbw_entity.tabText(self.tbw_entity.currentIndex()) == "Assets":
                entityType = "assets"
            else:
                entityType = "shots"

        if entityType == "assets":
            uielement = self.tw_assets
        else:
            uielement = self.tw_shots

        sItems = uielement.selectedItems()

        if len(sItems) == 1:
            self.curEntity = [entityType, sItems[0].text(0)]
        else:
            self.curEntity = None

        self.updateTasks()

    @err_catcher(name=__name__)
    def taskClicked(self):
        sItems = self.lw_tasks.selectedItems()
        if len(sItems) == 1 and sItems[0].text() != self.curTask:
            self.curTask = sItems[0].text()
        else:
            self.curTask = ""

        self.updateVersions()

    @err_catcher(name=__name__)
    def updateAssets(self, load=False):
        self.tw_assets.clear()

        basePath = self.cb_paths.currentText()
        if basePath == "all":
            basePaths = list(self.importLocations.keys())[1:]
        else:
            basePaths = [basePath]
        
        assetPaths = self.getFilteredAssetPaths(basePaths)
        

        for basePath in assetPaths:
            for path in assetPaths[basePath]:
                assetBase = self.core.assetPath.replace(self.core.projectPath, basePath)
                

                relPath = path.replace(assetBase, "")
                pathData = relPath.split(os.sep)[1:]
                
                lastItem = None
                
                for idx, val in enumerate(pathData):
                    curPath = assetBase
                    for k in range(idx + 1):
                        curPath = os.path.join(curPath, pathData[k])
                    
                    if lastItem is None:
                        for k in range(self.tw_assets.topLevelItemCount()):
                            curItem = self.tw_assets.topLevelItem(k)
                            if curItem.text(0) == val:
                                lastItem = curItem
                                newData = lastItem.data(0, Qt.UserRole)
                                newData.append({"path": curPath})
                                lastItem.setData(0, Qt.UserRole, newData)

                        if lastItem is None:
                            lastItem = QTreeWidgetItem([val, curPath])
                            lastItem.setData(0, Qt.UserRole, [{"path": curPath}])
                            self.tw_assets.addTopLevelItem(lastItem)
                    else:
                        newItem = None
                        for k in range(lastItem.childCount()):
                            curItem = lastItem.child(k)
                            if curItem.text(0) == val:
                                newItem = curItem
                                newData = newItem.data(0, Qt.UserRole)
                                newData.append({"path": curPath})
                                newItem.setData(0, Qt.UserRole, newData)

                        if newItem is None:
                            newItem = QTreeWidgetItem([val, curPath])
                            newItem.setData(0, Qt.UserRole, [{"path": curPath}])
                            lastItem.addChild(newItem)

                        lastItem = newItem

                    if idx == (len(pathData) - 1):
                        lastItem.setText(2, "Asset")
                        iFont = lastItem.font(0)
                        iFont.setBold(True)
                        lastItem.setFont(0, iFont)
                    else:
                        lastItem.setText(2, "Folder")

        
        if self.tw_assets.topLevelItemCount() > 0:
            self.tw_assets.setCurrentItem(self.tw_assets.topLevelItem(0))
        
        self.entityClicked()




    @err_catcher(name=__name__)
    def getRenderProductNamesFromAsset(self, assetPath):
        render2dPath = self.get2dRenderingPathFromEntityPath(assetPath)
        pnames = []
        for root, folders, files in os.walk(render2dPath):
            pnames += folders
            break

        render3dPath = self.get3dRenderingPathFromEntityPath(assetPath)
        for root, folders, files in os.walk(render3dPath):
            pnames += folders
            break

        playblastsPath = self.getPlayblastsPathFromEntityPath(assetPath)
        for root, folders, files in os.walk(playblastsPath):
            pnames += folders
            break

        return pnames

    @err_catcher(name=__name__)
    def getPlayblastsPathFromEntityPath(self, path):
        return os.path.join(path, "Playblasts")

    @err_catcher(name=__name__)
    def get2dRenderingPathFromEntityPath(self, path):
        return os.path.join(path, "Rendering\\2dRender")

    @err_catcher(name=__name__)
    def get3dRenderingPathFromEntityPath(self, path):
        return os.path.join(path, "Rendering\\3dRender")

    @err_catcher(name=__name__)
    def getFilteredAssetPaths(self, basePaths):
        filteredAssets = {}
        
        for ePath in basePaths:
            basePath = self.importLocations[ePath]
            aPath = self.core.assetPath.replace(os.path.normpath(self.core.projectPath), basePath)
            assetPaths = self.core.entities.getAssetPaths(path=aPath)

            if not basePath.endswith(os.sep):
                basePath += os.sep
            
            
            
            for assetPath in assetPaths:
                if self.core.entities.isAssetPathOmitted(assetPath):
                    continue

                products = self.getRenderProductNamesFromAsset(assetPath)
                
                if not products:
                    continue

                if basePath not in filteredAssets:
                    filteredAssets[basePath] = []

                filteredAssets[basePath].append(assetPath)

        return filteredAssets

    @err_catcher(name=__name__)
    def aItemCollapsed(self, item):
        self.adclick = False

    @err_catcher(name=__name__)
    def sItemCollapsed(self, item):
        self.sdclick = False

    @err_catcher(name=__name__)
    def updateShots(self):
        self.tw_shots.clear()

        location = self.cb_paths.currentText()
        if location == "all":
            locations = list(self.importLocations.keys())[1:]
        else:
            locations = [location]

        sequences, shotData = self.core.entities.getShots(locations=locations)
        shots = {}
        for shot in shotData:
            seqName = shot[0]
            shotName = shot[1]
            shotPaths = shot[3]

            tasks = []
            for shotPath in shotPaths:
                #taskPath = self.core.products.getProductPathFromEntityPath(shotPath["path"])
                taskPath = self.get2dRenderingPathFromEntityPath(shotPath["path"])
                for foldercont in os.walk(taskPath):
                    tasks += foldercont[1]
                    break
            #self.core.popup("updateShots_tasks: " + dumps(tasks))
            if len(tasks) == 0:
                continue

            if seqName not in shots:
                shots[seqName] = {}

            if shotName not in shots[seqName]:
                shots[seqName][shotName] = []

            for shotPath in shotPaths:
                if shotPath not in shots[seqName][shotName]:
                    shots[seqName][shotName].append(shotPath)

        sequences = self.core.sortNatural(shots.keys())
        if "no sequence" in sequences:
            sequences.insert(
                len(sequences), sequences.pop(sequences.index("no sequence"))
            )

        for seqName in sequences:
            seqItem = QTreeWidgetItem([seqName])
            self.tw_shots.addTopLevelItem(seqItem)

            for shot in self.core.sortNatural(shots[seqName]):
                sItem = QTreeWidgetItem([shot])
                sItem.setData(0, Qt.UserRole, shots[seqName][shot])
                seqItem.addChild(sItem)

        if self.tw_shots.topLevelItemCount() > 0:
            self.tw_shots.setCurrentItem(self.tw_shots.topLevelItem(0))

        self.entityClicked()

    @err_catcher(name=__name__)
    def getTasks(self):
        tasks = {}
        if self.tbw_entity.tabText(self.tbw_entity.currentIndex()) == "Assets":
            entityItem = self.tw_assets.currentItem()
        else:
            entityItem = self.tw_shots.currentItem()
        
        
        
        if entityItem and entityItem.data(0, Qt.UserRole):
            #self.core.popup("getTasks_tasks: " + str(entityItem.data))
            taskPaths  = [self.get2dRenderingPathFromEntityPath(x["path"]) for x in entityItem.data(0, Qt.UserRole) if x]
            taskPaths += [self.get3dRenderingPathFromEntityPath(x["path"]) for x in entityItem.data(0, Qt.UserRole) if x]
            taskPaths += [self.getPlayblastsPathFromEntityPath(x["path"]) for x in entityItem.data(0, Qt.UserRole) if x]
            

            
            tasks = self.core.products.getProductsFromPaths(taskPaths)
        #self.core.popup("getTasks_tasks: " + dumps(tasks))
        return tasks

    
    @err_catcher(name=__name__)
    def updateTasks(self, item=None):
        self.lw_tasks.clear()

        tasks = self.getTasks()
        taskNames = sorted(tasks.keys(), key=lambda s: s.lower())

        for tn in taskNames:
            item = QListWidgetItem(tn.replace("_ShotCam", "ShotCam"))
            item.setData(Qt.UserRole, tasks[tn])
            self.lw_tasks.addItem(item)

        if self.lw_tasks.count() > 0:
            self.lw_tasks.setCurrentRow(0)

        self.updateVersions()

    @err_catcher(name=__name__)
    def getPreferredFileFromVersion(self, version, location=None):
        #preferredUnit = preferredUnit or getattr(self.core.appPlugin, "preferredUnit", "centimeter")

        if location:
            locationPath = self.core.products.getLocationPathFromLocation(location)

        
        filepath = None
        
        for vlocation in version["locations"]:
            filepath = version["locations"][vlocation]
            
        #self.core.popup(filepath)
        return filepath
        
    @err_catcher(name=__name__)
    def updateVersions(self):
        self.tw_versions.clearContents()
        self.tw_versions.setRowCount(0)

        twSorting = [
            self.tw_versions.horizontalHeader().sortIndicatorSection(),
            self.tw_versions.horizontalHeader().sortIndicatorOrder(),
        ]
        self.tw_versions.setSortingEnabled(False)

        # currentItem() leads to crashes in blender
        taskItem = self.lw_tasks.currentItem()
        
        if taskItem and taskItem.data(Qt.UserRole):
            taskData = taskItem.data(Qt.UserRole)
            versionPaths = taskData["locations"]
            
            
            for root, folders, files in os.walk(versionPaths[0]):
                for folder in folders : 
                    

                    version = os.path.join(root , folder) #self.getVersionsFromPaths(versionPaths)
                    versionName = folder
                    
                
                    #version = versions[versionName]
                    #self.core.popup("updateVersions: " + dumps(folder))
                    
                    if (not versionName.startswith("v0") ):#versionName == "master":
                        #self.core.popup(version)
                        p = self.getImgSources(path = version , getFirstFile = True)
                        filepath = p[0] if p else ""
                        location = ""
                        comment = ""
                        
                        tmp = filepath.split("\\")[-1].split(".")[0].split("_")
                        file_name = "_".join(tmp[:-1])
                        #versionName = tmp[-1]
                        uStr = "" 
                        
                        infoPath = os.path.join("\\".join(filepath.split("\\")[:-2]), "versioninfo.yml")
                        #self.core.popup("\\".join(filepath.split("\\")[:-2]))
                        if(os.path.exists(infoPath)) : 
                            f = open(infoPath, "r")
                            user = f.read().split("Created by:")[-1].split("\n")[0]
                            f.close()
                        else : 
                            user = ""

                        if filepath :
                            if (versionName == "master"): 
                                filepath += "0" 
                                aov_pass = ""
                            else :   
                                tmp = filepath.split("\\")[-3]
                                #self.core.popup(tmp)
                                filepath += "1" 
                                aov_pass = versionName
                                
                                if (tmp.startswith("v0")):
                                    versionName = tmp 
                                else : 
                                    versionName = ""

                            self.addVersionToTable(filepath, file_name ,aov_pass , versionName, comment, uStr, user, location=location)
                   
                    else:
                        pass 
                    
            versions = self.getVersionsFromPaths(versionPaths)
            for versionName in versions:
                version = versions[versionName]
                for v in version["locations"] : 
                    if (not next(os.walk(v))[1]) :
                        if versionName == "master":
                            pass 
                        elif versionName.startswith("v0"):
                            filepath = self.getPreferredFileFromVersion(version)
                            #versionNameData = self.core.products.getDataFromVersionName(versionName)
                            file_name = filepath.split("\\")[-1].split(".")[0]
                            #file_name = "_".join(tmp[:-1])
                            versionName = v.split("\\")[-1]

                            #self.core.popup(list(version["locations"])[0])
                            infoPath = os.path.join(list(version["locations"])[0], "versioninfo.yml")

                            if(os.path.exists(infoPath)) : 
                                f = open(infoPath, "r")
                                user = f.read().split("Created by:")[-1].split("\n")[0]
                                f.close()
                            else : 
                                user = ""
                            comment = version.get("comment" , "")
                            #user = version.get("user", "")     
                            uStr = "" 
                            aov_pass = ""

                            if len(self.importLocations) > 1:
                                location = self.core.products.getLocationFromFilepath(filepath)
                            else:
                                location = ""

                            #self.core.popup("updateVersions: " + dumps((filepath, versionName, comment, uStr, user, location)))
                            if filepath : 
                                filepath += "0" 
                                self.addVersionToTable(filepath, file_name ,aov_pass, versionName, comment, uStr, user, location=location)

        self.tw_versions.resizeColumnsToContents()
        self.tw_versions.setColumnWidth(0 , 200 * self.core.uiScaleFactor)
        self.tw_versions.setColumnWidth(1, 90 * self.core.uiScaleFactor)
        self.tw_versions.setColumnWidth(3, 70 * self.core.uiScaleFactor)
        self.tw_versions.setColumnWidth(4, 50 * self.core.uiScaleFactor)
        self.tw_versions.setColumnWidth(
            self.tw_versions.columnCount() - 4, 70 * self.core.uiScaleFactor
        )
        self.tw_versions.setColumnWidth(
            self.tw_versions.columnCount() - 3, 150 * self.core.uiScaleFactor
        )

        self.tw_versions.sortByColumn(twSorting[0], twSorting[1])
        self.tw_versions.setSortingEnabled(True)

        if self.tw_versions.model().rowCount() > 0:
            self.tw_versions.selectRow(0)

    @err_catcher(name=__name__)
    def addVersionToTable(self, filepath, file_name ,aov_pass, versionName, comment, units, user, location=None):
        depPath, depExt = getattr(
            self.core.appPlugin,
            "splitExtension",
            lambda x: os.path.splitext(x),
        )(filepath)

        row = self.tw_versions.rowCount()
        self.tw_versions.insertRow(row)


        item = QTableWidgetItem(file_name)
        item.setTextAlignment(Qt.Alignment(Qt.AlignCenter))
        rowItems = 0
        self.tw_versions.setItem(row, rowItems, item)
        rowItems += 1

        item = QTableWidgetItem(aov_pass)
        item.setTextAlignment(Qt.Alignment(Qt.AlignCenter))
        self.tw_versions.setItem(row, rowItems, item)
        rowItems += 1


        if versionName.startswith("master") and sys.version[0] != "2":
            item = MasterItem(versionName)
        else:
            item = QTableWidgetItem(versionName)

        item.setTextAlignment(Qt.Alignment(Qt.AlignCenter))
        #rowItems = 0
        self.tw_versions.setItem(row, rowItems, item)
        rowItems += 1

        if comment == "nocomment":
            comment = ""

        item = QTableWidgetItem(comment)
        item.setTextAlignment(Qt.Alignment(Qt.AlignCenter))
        self.tw_versions.setItem(row, rowItems, item)
        rowItems += 1

        item = QTableWidgetItem(depExt[:-1])
        item.setTextAlignment(Qt.Alignment(Qt.AlignCenter))
        self.tw_versions.setItem(row, rowItems, item)
        rowItems += 1

        item = QTableWidgetItem(units)
        item.setTextAlignment(Qt.Alignment(Qt.AlignCenter))
        self.tw_versions.setItem(row, rowItems, item)
        rowItems += 1

        if location and len(self.importLocations) > 1:
            item = QTableWidgetItem(location)
            item.setTextAlignment(Qt.Alignment(Qt.AlignCenter))
            self.tw_versions.setItem(row, rowItems, item)
            rowItems += 1

        item = QTableWidgetItem(user)
        item.setTextAlignment(Qt.Alignment(Qt.AlignCenter))
        self.tw_versions.setItem(row, rowItems, item)
        rowItems += 1

        cdate = self.core.getFileModificationDate(filepath[:-1])
        item = QTableWidgetItem()
        item.setTextAlignment(Qt.Alignment(Qt.AlignCenter))
        dateStr = QDateTime.fromString(cdate, "dd.MM.yy,  hh:mm:ss").addYears(100)
        item.setData(Qt.DisplayRole, dateStr)
        item.setToolTip(cdate)
        self.tw_versions.setItem(row, rowItems, item)
        rowItems += 1

        impPath = getattr(self.core.appPlugin, "fixImportPath", lambda x: x)(
            filepath
        )
        item = QTableWidgetItem(impPath)
        self.tw_versions.setItem(row, rowItems, item)
        rowItems += 1

    @err_catcher(name=__name__)
    def getCurSelection(self):
        curPath = self.core.getScenePath()

        if self.tbw_entity.tabText(self.tbw_entity.currentIndex()) == "Assets":
            entityItem = self.tw_assets.currentItem()
        else:
            entityItem = self.tw_shots.currentItem()

        if entityItem is None:
            return curPath

        #curPath = self.core.products.getProductPathFromEntityPath(entityItem.text(1))
        curPath = self.get2dRenderingPathFromEntityPath(entityItem.text(1))
        
        #self.core.popup("getCurSelection_curPath: " + dumps(curPath))
        
        if self.lw_tasks.currentItem() is None:
            return curPath

        curPath = os.path.join(
            curPath, self.lw_tasks.currentItem().text().replace("ShotCam", "_ShotCam")
        )

        if self.tw_versions.selectionModel().currentIndex().row() == -1:
            return curPath

        pathC = self.tw_versions.model().columnCount() - 1
        row = self.tw_versions.selectionModel().currentIndex().row()
        return self.tw_versions.model().index(row, pathC).data()

    @err_catcher(name=__name__)
    def navigateToFile(self, fileName, task=None, version=None):
        if not fileName:
            return False

        if not os.path.exists(fileName):
            fileName = os.path.dirname(fileName)
            if not os.path.exists(fileName):
                return False

        fileName = os.path.normpath(fileName)

        relFileName = None
        for ePath in self.importLocations.values():
            sceneBase = self.core.scenePath.replace(os.path.normpath(self.core.projectPath), ePath)
            if sceneBase in os.path.normpath(fileName):
                relFileName = fileName.replace(sceneBase, "")
                fileImportPath = ePath

        if not relFileName:
            return False

        fileNameData = relFileName.split(os.sep)
        prjPath = os.path.normpath(self.core.projectPath)
        aBase = self.core.assetPath.replace(prjPath, fileImportPath)
        if aBase in fileName:
            entityType = "asset"
        else:
            entityType = "shot"

        if not task:
            task = self.core.paths.getCachePathData(fileName).get("task", "")

        versionName = version
        if not version and self.importState:
            versionName = self.importState.l_curVersion.text()

        if versionName and versionName != "-":
            versionName = versionName[:5]

        foundEntity = False

        if entityType == "asset":
            uielement = self.tw_assets
            self.tbw_entity.setCurrentIndex(0)

            itemPath = fileName.replace(aBase + os.sep, "")
            hierarchy = itemPath.split(os.sep)
            hItem = self.tw_assets.findItems(hierarchy[0], Qt.MatchExactly, 0)
            if len(hItem) == 0:
                return False

            hItem = hItem[-1]
            hItem.setExpanded(True)

            endIdx = None
            if len(hierarchy) > 1:
                for idx, i in enumerate((hierarchy[1:])):
                    for k in range(hItem.childCount() - 1, -1, -1):
                        if hItem.child(k).text(0) == i:
                            hItem = hItem.child(k)
                            if len(hierarchy) > (idx + 2):
                                hItem.setExpanded(True)
                            break
                    else:
                        endIdx = idx + 1
                        break

            self.tw_assets.setCurrentItem(hItem)
            foundEntity = True

        else:
            uielement = self.tw_shots
            entityName = fileNameData[2]
            self.tbw_entity.setCurrentIndex(1)

            shotName, seqName = self.core.entities.splitShotname(entityName)

            for i in range(self.tw_shots.topLevelItemCount()):
                sItem = self.tw_shots.topLevelItem(i)
                if sItem.text(0) == seqName:
                    sItem.setExpanded(True)
                    for k in range(sItem.childCount()):
                        shotItem = sItem.child(k)
                        if shotItem.text(0) == shotName:
                            self.tw_shots.setCurrentItem(shotItem)
                            foundEntity = True
                            break

                    if foundEntity:
                        break
            else:
                if entityType == "shot" and self.tw_shots.topLevelItemCount() > 0:
                    seqItem = self.tw_shots.topLevelItem(0)
                    seqItem.setExpanded(True)
                    self.tw_shots.setCurrentItem(seqItem.child(0))
                    foundEntity = True

        if foundEntity:
            self.updateTasks()
            if task == "_ShotCam":
                task = "ShotCam"

            if self.lw_tasks.findItems(task, Qt.MatchExactly) != []:
                self.lw_tasks.setCurrentItem(
                    self.lw_tasks.findItems(task, Qt.MatchExactly)[0]
                )

                self.updateVersions()

                for i in range(self.tw_versions.model().rowCount()):
                    if self.tw_versions.model().index(i, 0).data() == versionName:
                        self.tw_versions.selectRow(i)
                        return True
            return True

        return False

    @err_catcher(name=__name__)
    def navigateToEntity(self, entity, entityName):
        if entity == "asset":
            result = self.navigateToAsset(entityName)
        elif entity == "shot":
            result = self.navigateToShot(entityName)

        return result

    @err_catcher(name=__name__)
    def navigateToAsset(self, assetName):
        self.tbw_entity.setCurrentIndex(0)

        hierarchy = assetName.split(os.sep)
        hItem = self.tw_assets.findItems(hierarchy[0], Qt.MatchExactly, 0)
        if len(hItem) == 0:
            return False

        hItem = hItem[-1]
        hItem.setExpanded(True)

        if len(hierarchy) > 1:
            for idx, i in enumerate(hierarchy[1:]):
                for k in range(hItem.childCount() - 1, -1, -1):
                    if hItem.child(k).text(0) == i:
                        hItem = hItem.child(k)
                        if len(hierarchy) > (idx + 2):
                            hItem.setExpanded(True)
                        break
                else:
                    break

        self.tw_assets.setCurrentItem(hItem)
        return True

    @err_catcher(name=__name__)
    def navigateToShot(self, shotName):
        self.tbw_entity.setCurrentIndex(1)
        shotName, seqName = self.core.entities.splitShotname(shotName)

        for seqNum in range(self.tw_shots.topLevelItemCount()):
            seqItem = self.tw_shots.topLevelItem(seqNum)
            if seqItem.text(0) == seqName:
                seqItem.setExpanded(True)
                for shotNum in range(seqItem.childCount()):
                    shotItem = seqItem.child(shotNum)
                    if shotItem.text(0) == shotName:
                        self.tw_shots.setCurrentItem(shotItem)
                        return True

        return False

    @err_catcher(name=__name__)
    def navigateToProduct(self, product, entity=None, entityName=None):
        if entity and entityName:
            result = self.navigateToEntity(entity, entityName)
            if not result:
                return False

        self.updateTasks()
        if product == "_ShotCam":
            product = "ShotCam"

        matchingItems = self.lw_tasks.findItems(product, Qt.MatchExactly)
        if matchingItems:
            self.lw_tasks.setCurrentItem(matchingItems[0])
            return True

        return False

    @err_catcher(name=__name__)
    def navigateToVersion(self, version, entity=None, entityName=None, product=None):
        if product:
            result = self.navigateToProduct(product, entity, entityName)
            if not result:
                return False

        self.updateVersions()

        for versionNum in range(self.tw_versions.model().rowCount()):
            if self.tw_versions.model().index(versionNum, 0).data() == version:
                self.tw_versions.selectRow(versionNum)
                return True

        return False

    @err_catcher(name=__name__)
    def getVersionsFromPaths(self, paths):
        versions = {}
        for path in paths:
            pathVersions = self.getVersionsFromPath(path)
            for pathVersion in pathVersions:
                if pathVersion in versions:
                    versions[pathVersion]["locations"].update(pathVersions[pathVersion]["locations"])
                else:
                    versions[pathVersion] = pathVersions[pathVersion]

        return versions

    @err_catcher(name=__name__)
    def isVersionFolderName(self, name):
        nameData = name.split(self.core.filenameSeparator)
        #self.core.popup("isVersionFolderName: " + dumps(name) + dumps(name[0] == "v") )
        isValid = name[0] == "v" #and len(nameData) == 3
        return isValid

    @err_catcher(name=__name__)
    def getVersionsFromPath(self, path):
        versions = {}
        versionPaths = []
        for root, folders, files in os.walk(path):
            for folder in folders:
                
                isVersion = self.isVersionFolderName(folder)
                
                isMaster = folder == "master"
                if not isVersion and not isMaster:
                    continue

                versionPath = os.path.join(root, folder)
                versionPaths.append(versionPath)
            break

        #units = ["centimeter", "meter", ""]
        blacklistExtensions = [".txt", ".ini", ".yml", ".xgen" , ".pdf" , ".mb" , ".ma"]
        for versionPath in versionPaths:
            name = os.path.basename(versionPath)
            productName = os.path.basename(os.path.dirname(versionPath))
            version = {"type": "productVersion", "name": name, "locations": {versionPath: {}}}
            #for unit in units:

                #unitPath = os.path.join(versionPath, unit)
            filepath = None
            #self.core.popup("versionPath: " + dumps(versionPath))
            for root, folders, files in os.walk(versionPath):
                if not files:
                    break

                for file in files:
                    ext = os.path.splitext(file)[1]
                    if ext in blacklistExtensions or file[0] == ".":
                        continue

                    filepath = os.path.join(root, file)
                    #filepath = getattr(self.core.appPlugin, "overrideImportpath", lambda x: x)(filepath)
                    
                    '''
                    shotCamFormat = getattr(self.core.appPlugin, "shotcamFormat", ".abc")
                    if (
                        shotCamFormat == ".fbx"
                        and productName == "_ShotCam"
                        and filepath.endswith(".abc")
                        and os.path.exists(filepath[:-3] + "fbx")
                    ):
                        filepath = filepath[:-3] + "fbx"

                    objPath = filepath[:-3] + "obj"
                    if filepath.endswith(".mtl") and os.path.exists(objPath):
                        filepath = objPath
                        break
                
                    '''
                if not filepath:
                    continue

                version["locations"][versionPath] = filepath

            if not version["locations"][versionPath]:
                continue

            versions[name] = version

        return versions

    @err_catcher(name=__name__)
    def getImgSources(self, path, getFirstFile=False):
        foundSrc = []
        for k in os.walk(path):
            sources = []
            psources = []
            for m in k[2]:
                baseName, extension = os.path.splitext(m)
                if extension in [
                    ".jpg",
                    ".jpeg",
                    ".JPG",
                    ".png",
                    ".PNG",
                    ".tif",
                    ".tiff",
                    ".exr",
                    ".mp4",
                    ".mov",
                    ".avi",
                    ".dpx",
                ]:
                    src = [baseName, extension]
                    if len(baseName) > 3:
                        endStr = baseName[-4:]
                        if endStr.isnumeric():
                            src = [baseName[:-4], extension]

                    psources.append(src)

            for m in sorted(k[2]):
                baseName, extension = os.path.splitext(m)
                if extension in [
                    ".jpg",
                    ".jpeg",
                    ".JPG",
                    ".png",
                    ".PNG",
                    ".tif",
                    ".tiff",
                    ".exr",
                    ".mp4",
                    ".mov",
                    ".avi",
                    ".dpx",
                ]:
                    fname = m
                    if getFirstFile:
                        return [os.path.join(path, m)]

                    if len(baseName) > 3:
                        endStr = baseName[-4:]
                        if (
                            endStr.isnumeric()
                            and len(psources) == psources.count(psources[0])
                            and extension not in [".mp4", ".mov", ".avi"]
                        ):
                            fname = "%s@@@@%s" % (baseName[:-4], extension)

                    if fname in sources:
                        if len(sources) == 1:
                            break  # sequence detected
                    else:
                        foundSrc.append(os.path.join(path, fname))
                        sources.append(fname)
            break

        return foundSrc

class MasterItem(QTableWidgetItem):
    def __lt__(self, other):
        return False
