$ScriptsFolder = "$PSScriptRoot\Scripts"
$RandoFolderName = 'Entrance Randomizer'
Remove-Item -Path $ScriptsFolder -Recurse -ErrorAction SilentlyContinue
Copy-Item -Path "$PSScriptRoot\$RandoFolderName" -Destination "$ScriptsFolder\$RandoFolderName" -Recurse
Copy-Item -Path "$PSScriptRoot\..\Various technical notes\transition_infos.json" -Destination "$ScriptsFolder\$RandoFolderName\lib"
Compress-Archive -Path $ScriptsFolder -DestinationPath $RandoFolderName -Force
Remove-Item -Path $ScriptsFolder -Recurse
