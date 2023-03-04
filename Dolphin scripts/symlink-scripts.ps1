Param([Parameter(mandatory=$true)][String]$dolphinLocation)
New-Item `
  -ItemType SymbolicLink `
  -Path "$dolphinLocation\Scripts" `
  -Target $PSScriptRoot
