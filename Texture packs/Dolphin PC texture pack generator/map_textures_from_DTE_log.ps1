# Reads a DolphinTextureExtraction.log file to map the textures' original names to their Dolphin equivalent hashed-names.
# Used to generate DTE_texture_map.json/xml.

param ([string]$dteLogFile)
if (-not $args) {
  # $dteLogFile = Read-Host 'Enter the path to DolphinTextureExtraction.log'
  $dteLogFile = 'E:\Users\Avasam\Documents\ROMs & Mods\PC\Pitfall-TLE\ARCs\Gamecube_US\files\~textures_2\DolphinTextureExtraction.log'
}
else {
  $dteLogFile = $args[0]
}

$map = @{}
Get-Content $dteLogFile
| Where-Object { $_.StartsWith('[01] Extract: ') }
| ForEach-Object { $_.Substring(14, $_.Length - 4 - 14) }
| ForEach-Object {
  $key, $value = $_.Split('\')
  if (!$map.ContainsKey($key)) {
    $map[$key] = @()
  }
  $map[$key] += $value
}

$map | ConvertTo-Json | Out-File "$PSScriptRoot/Console Generator/DTETextureMap.json"
