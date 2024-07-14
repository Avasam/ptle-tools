$RandoFolderName = 'Entrance Randomizer'
$VersionFilePath = "$PSScriptRoot\$RandoFolderName/lib/constants.py"

$RandoVersion = Read-Host 'Version number (X.X.X)'
$VersionFileContent = Get-Content $VersionFilePath
$VersionFileContent -replace '^\s*__version = .*', "__version = `"$RandoVersion`"" | Set-Content $VersionFilePath

towncrier build --yes --version $RandoVersion
