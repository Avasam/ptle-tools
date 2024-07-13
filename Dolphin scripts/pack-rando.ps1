$ScriptsFolder = "$PSScriptRoot\Scripts"
$RandoFolderName = 'Entrance Randomizer'
$VersionFilePath = "$ScriptsFolder\$RandoFolderName/lib/constants.py"
Remove-Item -Path $ScriptsFolder -Recurse -ErrorAction SilentlyContinue
Copy-Item -Path "$PSScriptRoot\$RandoFolderName" -Destination "$ScriptsFolder\$RandoFolderName" -Recurse
Copy-Item -Path "$PSScriptRoot\..\Various technical notes\transition_infos.json" -Destination "$ScriptsFolder\$RandoFolderName\lib"

$VersionFileContent = Get-Content $VersionFilePath
$VersionLine = $VersionFileContent | Select-String -Pattern '^__version\s*=\s*".*"'
$RandoVersion = $VersionLine -replace '^\s*__version\s*=\s*"', '' -replace '".*$', ''
$DevVersion = git rev-parse --short HEAD
$VersionFileContent -replace '^\s*__dev_version.*', "__dev_version = `"$DevVersion`"" | Set-Content $VersionFilePath

Compress-Archive -Path $ScriptsFolder -DestinationPath "$RandoFolderName v$RandoVersion-$DevVersion.zip" -Force
Remove-Item -Path $ScriptsFolder -Recurse
