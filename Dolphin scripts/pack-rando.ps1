$ScriptsFolder = "$PSScriptRoot\Scripts"
$RandoFolderName = 'Entrance Randomizer'
$VersionLine = Get-Content "$PSScriptRoot\$RandoFolderName/lib/constants.py" | Select-String -Pattern '^__version__\s*=\s*".*"'
$RandoVersion = $VersionLine -replace '^\s*__version__\s*=\s*"', '' -replace '".*$', ''
Remove-Item -Path $ScriptsFolder -Recurse -ErrorAction SilentlyContinue
Copy-Item -Path "$PSScriptRoot\$RandoFolderName" -Destination "$ScriptsFolder\$RandoFolderName" -Recurse
Copy-Item -Path "$PSScriptRoot\..\Various technical notes\transition_infos.json" -Destination "$ScriptsFolder\$RandoFolderName\lib"
Compress-Archive -Path $ScriptsFolder -DestinationPath "$RandoFolderName v$RandoVersion.zip" -Force
Remove-Item -Path $ScriptsFolder -Recurse
