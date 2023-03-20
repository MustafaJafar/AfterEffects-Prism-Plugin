# -*- coding: utf-8 -*-

"""
Script which builds a .jsx file, sends it to After Effects and then waits for data to be returned. 

This script became possible because of : 
    https://stackoverflow.com/questions/50848219/adobe-after-effects-com-object-model-id
    https://github.com/kingofthebongo/AE_PyJsx
    Many Thanks and appreciations! 
"""
import os, sys, subprocess, time , ctypes
import winreg as _winreg
from contextlib import suppress
import itertools

# Tool to get existing windows, usefull here to check if AE is loaded
class CurrentWindows():
    def __init__(self):
        self.EnumWindows = ctypes.windll.user32.EnumWindows
        self.EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        self.GetWindowText = ctypes.windll.user32.GetWindowTextW
        self.GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        self.IsWindowVisible = ctypes.windll.user32.IsWindowVisible

        self.titles = []
        self.EnumWindows(self.EnumWindowsProc(self.foreach_window), 0)

    def foreach_window(self, hwnd, lParam):
        if self.IsWindowVisible(hwnd):
            length = self.GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            self.GetWindowText(hwnd, buff, length + 1)
            self.titles.append(buff.value)
        return True

    def getTitles(self):
        return self.titles

# A Mini Python wrapper for the JS commands...
class AE_JSWrapper(object):
    def __init__(self, aeVersion = "", returnFolder = ""):

        #Search Reg Edit to find installed versions, and get the first one in the list
        root = _winreg.HKEY_LOCAL_MACHINE
        path = "SOFTWARE\\Adobe\\After Effects\\"
        if (not aeVersion ) : 
            versions = list(self.subkeys(root, path))
            self.aeVersion = versions[0]
        else : 
            self.aeVersion = aeVersion

        # Get the AE_ exe path from the registry. 
        try:
            self.aeKey = _winreg.OpenKey(root,path + self.aeVersion)
        except:
            print ("ERROR: Unable to find After Effects version " + self.aeVersion + " on this computer\nTo get correct version number please check https://en.wikipedia.org/wiki/Adobe_After_Effects\nFor example, \"After Effect CC 2019\" is version \"16.0\"")
            sys.exit()

        self.aeApp = _winreg.QueryValueEx(self.aeKey, 'InstallPath')[0] + 'AfterFX' #'AfterFX.exe'          

        # Get the path to the return file. Create it if it doesn't exist.
        if not len(returnFolder):
            returnFolder = os.path.join(os.path.expanduser('~'), "Documents", "temp", "AePyJsx")
        self.returnFile = os.path.join(returnFolder, "ae_temp_ret.txt")
        if not os.path.exists(returnFolder):
            os.mkdir(returnFolder)
        
        # Ensure the return file exists...
        with open(self.returnFile, 'w') as f:
                f.close()  
            
        # Establish the last time the temp file was modified. We use this to listen for changes. 
        self.lastModTime = os.path.getmtime(self.returnFile)         
        
        # Temp file to store the .jsx commands. 
        self.tempJsxFile = os.path.join(returnFolder, "ae_temp_com.jsx")
        
        # This list is used to hold all the strings which eventually become our .jsx file. 
        self.commands = []    

    def subkeys(self , root, path , flags=0):
        with suppress(WindowsError), _winreg.OpenKey(root, path, 0, _winreg.KEY_READ|flags) as k:
            for i in itertools.count():
                yield _winreg.EnumKey(k, i)

    @property
    def ae_process_exist(self):
        return next((t for t in  CurrentWindows().getTitles() if"Adobe After Effects".lower() in t.lower()), "")

    @property
    def waitingAELoading(self):
        loading = True
        attempts = 0
        while loading and attempts < 60:
            for t in CurrentWindows().getTitles():
                if "Adobe After Effects".lower() in t.lower():
                    loading = False
                    break

            attempts += 1
            time.sleep(0.5)

        return not loading
    

    def openAE(self):
        """Pass the commands to the subprocess module."""    
        target = [self.aeApp]
        ret = subprocess.Popen(target)


    # This group of helper functions are used to build and execute a jsx file.
    def jsNewCommandGroup(self):
        """clean the commands list. Called before making a new list of commands"""
        self.commands = []

    def jsExecuteCommand(self):
        """Pass the commands to the subprocess module."""
        self.compileCommands() 

        target = [self.aeApp, "-ro", self.tempJsxFile]
        ret = subprocess.Popen(target)
    
    def addCommand(self, command):
        """add a command to the commands list"""
        self.commands.append(command)

    def compileCommands(self):
        with open(self.tempJsxFile, "wb") as f:
            for command in self.commands:
                f.write(bytearray(command, encoding='utf-8'))

    def jsWriteDataOut(self, returnRequest):
        """ An example of getting a return value"""
        com = (
            """
            var retVal = %s; // Ask for some kind of info about something. 
            
            // Write to temp file. 
            var datFile = new File("[DATAFILEPATH]"); 
            datFile.open("w"); 
            datFile.writeln(String(retVal)); // return the data cast as a string.  
            datFile.close();
            """ % (returnRequest)
        )

        returnFileClean = "/" + self.returnFile.replace("\\", "/").replace(":", "").lower()
        com = com.replace("[DATAFILEPATH]", returnFileClean)

        self.commands.append(com)
        
        
    def readReturn(self):
        """Helper function to wait for AE to write some output for us."""
        # Give time for AE to close the file...
        time.sleep(0.1)        
        
        self._updated = False
        while not self._updated:
            self.thisModTime = os.path.getmtime(self.returnFile)
            if str(self.thisModTime) != str(self.lastModTime):
                self.lastModTime = self.thisModTime
                self._updated = True
        
        f = open(self.returnFile, "r+")
        content = f.readlines()
        f.close()

        res = []
        for item in content:
            res.append(str(item.rstrip()))
        return res
    
    
# An interface to actually call those commands. 
class AE_JSInterface(object):
    
    def __init__(self, aeVersion = "", returnFolder = ""):
        self.aeWindowName = "Adobe After Effects"
        self.untitledName = "- Untitled Project.aep"
        self.aeCom = AE_JSWrapper(aeVersion, returnFolder) # Create wrapper to handle JSX
        
    @property
    def ae_process_exist(self):
        return next((t for t in  CurrentWindows().getTitles() if"Adobe After Effects".lower() in t.lower()), "")

    @property
    def waitingAELoading(self):
        loading = True
        attempts = 0
        while loading and attempts < 60:
            for t in CurrentWindows().getTitles():
                if self.aeWindowName.lower() in t.lower():
                    loading = False
                    break

            attempts += 1
            time.sleep(0.5)

        return not loading

    #core functionality, run directly from cmd, don't return. 
    def openAE(self):
        self.aeCom.openAE()

    def jsSaveAS(self , path): 
        target = ['"'+self.aeCom.aeApp+'"' , "-so", 'app.project.save(File("' + path +'"));' ]
        target = " ".join(target)
        ret = subprocess.Popen(target)


    def jsOpenScene(self, path):
        ae_process = self.ae_process_exist
        if (not ae_process ): 
            self.aeCom.openAE()
            
        if (self.waitingAELoading) :
            target = ['"'+self.aeCom.aeApp+'"' , "-so", 'app.open(File("' + path +'"));' ]
            target = " ".join(target)
            ret = subprocess.Popen(target)

    #additional functionality, run from wrapper class above , support return. 
    def jsAlert(self, msg):
        self.aeCom.jsNewCommandGroup() # Clean JSX command list
        # Write new JSX commandsjsOpenScene
        jsxTodo =  "alert(\"" + msg + "\");"
        self.aeCom.addCommand(jsxTodo)
        self.aeCom.jsExecuteCommand() # Execute command list
    
    def jsImport(self, path):
        self.aeCom.jsNewCommandGroup() # Clean JSX command list
        # Write new JSX commandsjsOpenScene
        path = path.replace("\\" , "\\\\")

        jsxTodo =  "var item = app.project.importFile(new ImportOptions(File(\"" + path + "\")));"
        jsxTodo += "item.name =   item.name + \"_PRISM_IMG\" ;"
        self.aeCom.addCommand(jsxTodo)
        self.aeCom.jsExecuteCommand() # Execute command list
    
    def jsImportSequence(self, path):
        self.aeCom.jsNewCommandGroup() # Clean JSX command list
        # Write new JSX commandsjsOpenScene
        path = path.replace("\\" , "\\\\")

        jsxTodo =  "var importOptions  =  new ImportOptions();"
        jsxTodo += "importOptions.file = new File(\"" + path + "\");"
        jsxTodo += "importOptions.sequence = true;"
        jsxTodo += "var item = app.project.importFile(importOptions);"
        jsxTodo += "item.name =   item.name + \"_PRISM_PASS\";"
        self.aeCom.addCommand(jsxTodo)
        self.aeCom.jsExecuteCommand() # Execute command list

    def jsGetActiveDocument(self):
        ae_process = self.ae_process_exist
        if (not ae_process ): 
            return ""

        elif ae_process.endswith(self.untitledName): 
            path = os.path.join(os.path.expanduser('~') , "Documents", "Untitled Project.aep").replace("\\","/")
            self.jsSaveAS(path)
            return path
        
        self.aeCom.jsNewCommandGroup() # Clean JSX command list
        # Write new JSX commands
        resultVarName = "aeFilePath"
        jsxTodo = ("var %s = app.project.file.fsName;" % resultVarName)
        self.aeCom.addCommand(jsxTodo)
        self.aeCom.jsWriteDataOut(resultVarName) # Add JSX commands to write result in temp file
        self.aeCom.jsExecuteCommand() # Execute command list
        return self.aeCom.readReturn()[0].replace("\\","/") # Read the temp file to get the JSX returned value

    @property
    def Version(self):
        self.aeCom.jsNewCommandGroup() # Clean JSX command list
        # Write new JSX commands
        resultVarName = "aeVersion"
        jsxTodo = ("var %s =  app.version;" % resultVarName)
        self.aeCom.addCommand(jsxTodo)
        self.aeCom.jsWriteDataOut(resultVarName) # Add JSX commands to write result in temp file
        self.aeCom.jsExecuteCommand() # Execute command list
        return self.aeCom.readReturn()[0] # Read the temp file to get the JSX returned value   


#for this to work smoothly, run script multipletimes one for each command
# or just wait for a good amount of time! 
# Do : 
    #run : openAE()
    #run : jsGetActiveDocument()
#Not to Do : 
    #run : openAE(), jsGetActiveDocument()

if __name__ == '__main__':
    #x = next((t for t in  CurrentWindows().getTitles() if"Adobe After Effects".lower() in t.lower()), "")
    #print(x)
    # Create the wrapper
    aeApp = AE_JSInterface( returnFolder = os.path.join(os.path.expanduser('~'), "Documents", "temp"))
    aeApp.openAE()
    #print(aeApp)
    if aeApp.waitingAELoading:
        current = aeApp.jsGetActiveDocument()
        aeApp.jsAlert(current)
    #     print(aeApp.waitingAELoading)
    #     current = aeApp.jsGetActiveDocument()
    #     print(current)

    #     new_path = os.path.join(os.path.expanduser('~') , "Desktop" , "test2.aep").replace("\\","\\\\")
    #     aeApp.jsSaveAS(new_path)

    
    
    #aeApp.jsOpenScene(new_path)
    # Open AE if needed
    #aeApp.openAE()
    #print(aeApp)
    #if aeApp.waitingAELoading:
        # Launch function if AE is ready
        #aeApp.jsOpenScene((os.path.expanduser('~')+"\\Desktop\\test.aep").replace("\\","\\\\"))

        #print(aeApp.jsGetActiveDocument())
