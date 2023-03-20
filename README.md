# AfterEffects Prism Plugin :
  A prism plugin for adobe after effects 
## Supported Actions : 
    1) save version
    2) save version with comment 
    3) import single media files / image sequence  
    4) create new version from current (in AE Prism browser)

## Setup : 
  Copy AfterEffects Folder to Apps folder in Prism <br />
        
    C:\Prism\Plugins\Apps
        
## Usage : 
  from prism standalone 
    
    Options > After Effects > Connect 
    
 ![image](https://user-images.githubusercontent.com/20871534/226311719-87cddd1c-d526-43a2-a411-26f423098df3.png)


## Version Notes :
    It works on windows only
    It was tested with AE 2021 and prism v1.3.0.83 
    
    However, it is finished yet, it works fine, does the work and you can rely on it
    (we did rely on it in our studio)
    
    It still needs a lot of work although 
    To me I consider it a good concept on how to make a prism plugin for After Effects 
    

## Dev Notes : 
    This plugin was possiple by Creating an AE_JSInterface to mimic 
    the functionality of "win32com.client.Dispatch" 
    as After Effects doesn't seem to appear into COM objects list. 

    There's a jsx file in integration folder in this repo 
      after_effects_prism.jsx
    that calls prism commands from After Effects  
    for some reason it doesn't work from After Effects however it works from cmd 
  
    

### Credits :
  This script became possible because of : <br />
      https://stackoverflow.com/questions/50848219/adobe-after-effects-com-object-model-id <br />
      https://github.com/kingofthebongo/AE_PyJsx <br />
  Many Thanks and appreciations! <br />
    
    
