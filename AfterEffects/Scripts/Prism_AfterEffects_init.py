from Prism_AfterEffects_Variables import Prism_AfterEffects_Variables
from Prism_AfterEffects_externalAccess_Functions import Prism_AfterEffects_externalAccess_Functions
from Prism_AfterEffects_Functions import Prism_AfterEffects_Functions
from Prism_AfterEffects_Integration import Prism_AfterEffects_Integration

class Prism_Plugin_AfterEffects(
    Prism_AfterEffects_Variables,
    Prism_AfterEffects_externalAccess_Functions,
    Prism_AfterEffects_Functions,
    Prism_AfterEffects_Integration,
):
    def __init__(self, core):
        Prism_AfterEffects_Variables.__init__(self, core, self)
        Prism_AfterEffects_externalAccess_Functions.__init__(self, core, self)
        Prism_AfterEffects_Functions.__init__(self, core, self)
        Prism_AfterEffects_Integration.__init__(self, core, self)