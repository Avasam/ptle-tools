$ScriptsFolder = "$PSScriptRoot\Scripts"
Remove-Item -Path $ScriptsFolder -Recurse -ErrorAction SilentlyContinue
Copy-Item -Path "$PSScriptRoot\Entrance Randomizer" -Destination $ScriptsFolder -Recurse
Copy-Item -Path "$PSScriptRoot\..\Various technical notes\transition_infos.json" -Destination $ScriptsFolder
Compress-Archive -Path $ScriptsFolder -DestinationPath 'Entrance Randomizer'
Remove-Item -Path $ScriptsFolder -Recurse
