class Prism_AfterEffects_Variables(object):
    def __init__(self, core, plugin):
        self.version = "v1.3.0.0"
        self.pluginName = "AfterEffects"
        self.pluginType = "App"
        self.appShortName = "AfterEffects"
        self.appType = "2d"
        self.hasQtParent = False
        self.sceneFormats = [".aep" , ".aet"]
        self.appSpecificFormats = self.sceneFormats
        self.appColor = [35 , 35, 35]
        self.appVersionPresets = ["1.0"]
        self.renderPasses = []
        self.canOverrideExecuteable = False
        self.platforms = ["Windows"]
