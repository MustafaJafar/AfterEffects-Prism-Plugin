var panelGlobal = this;

/*
This UI was created by using https://scriptui.joonas.me  
*/ 

// PALETTE
// =======
var palette = (panelGlobal instanceof Panel) ? panelGlobal : new Window("palette"); 
    if ( !(panelGlobal instanceof Panel) ) palette.text = "After Effects Prism"; 
    palette.orientation = "column"; 
    palette.alignChildren = ["center","top"]; 
    palette.spacing = 10; 
    palette.margins = 16; 

var save_version = palette.add("button", undefined, undefined, {name: "save_version"}); 
    save_version.helpTip = "Save as new version in prism"; 
    save_version.text = "Save Version"; 
    save_version.preferredSize.width = 121; 
    save_version.preferredSize.height = 25; 

var save_extended = palette.add("button", undefined, undefined, {name: "save_extended"}); 
    save_extended.helpTip = "Save as new version with comment in prism"; 
    save_extended.text = "Save Extended"; 
    save_extended.preferredSize.width = 121; 
    save_extended.preferredSize.height = 25; 

var import_button = palette.add("button", undefined, undefined, {name: "import_button"}); 
    import_button.helpTip = "Import from prism"; 
    import_button.text = "Import"; 
    import_button.preferredSize.width = 121; 
    import_button.preferredSize.height = 25; 

var export_button = palette.add("button", undefined, undefined, {name: "export_button"}); 
    export_button.helpTip = "Render to prism\n\u0022It's not implemented yet\u0022"; 
    export_button.text = "Export"; 
    export_button.preferredSize.width = 121; 
    export_button.preferredSize.height = 25; 

var project_browser = palette.add("button", undefined, undefined, {name: "project_browser"}); 
    project_browser.helpTip = "Open prism's project browser"; 
    project_browser.text = "Project Browser"; 
    project_browser.preferredSize.width = 121; 
    project_browser.preferredSize.height = 25; 

var settings_button = palette.add("button", undefined, undefined, {name: "settings_button"}); 
    settings_button.helpTip = "Open prism's settings"; 
    settings_button.text = "Settings"; 
    settings_button.preferredSize.width = 121; 
    settings_button.preferredSize.height = 25; 

palette.layout.layout(true);
palette.layout.resize();
palette.onResizing = palette.onResize = function () { this.layout.resize(); }

if ( palette instanceof Window ) palette.show();


//Currently it doesn't work as "system.callSystem" doesn't act as calling the command itself in cmd
save_version.onClick = function(){ 
    var command = 'start cmd /k "%PRISM_ROOT%/Python37/python %PRISM_ROOT%/Plugins/Apps/AfterEffects/Scripts/Prism_AfterEffects_MenuTools.py SaveVersion"' ; 
    system.callSystem(command);
}

save_extended.onClick = function(){ 
    var command = 'start cmd /k "%PRISM_ROOT%/Python37/python %PRISM_ROOT%/Plugins/Apps/AfterEffects/Scripts/Prism_AfterEffects_MenuTools.py SaveComment"' ; 
    system.callSystem(command);
}

import_button.onClick = function(){ 
    var command = 'start cmd /k "%PRISM_ROOT%/Python37/python %PRISM_ROOT%/Plugins/Apps/AfterEffects/Scripts/Prism_AfterEffects_MenuTools.py Import"' ; 
    system.callSystem(command);
}

export_button.onClick = function(){
    alert("It's not implemented yet!");
}

project_browser.onClick = function(){
    var command = 'start cmd /k "%PRISM_ROOT%/Python37/python %PRISM_ROOT%/Plugins/Apps/AfterEffects/Scripts/Prism_AfterEffects_MenuTools.py ProjectBrowser"' ; 
    system.callSystem(command);
    
}

settings_button.onClick = function(){ 
    var command = 'start cmd /k "%PRISM_ROOT%/Python37/python %PRISM_ROOT%/Plugins/Apps/AfterEffects/Scripts/Prism_AfterEffects_MenuTools.py Settings"' ; 
    system.callSystem(command);
}