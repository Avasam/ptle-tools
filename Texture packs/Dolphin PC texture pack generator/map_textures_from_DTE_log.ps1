# Reads a DolphinTextureExtraction.log file to map the textures' original names to their Dolphin equivalent hashed-names.
# Used to generate DTETextureMap.jsonc.

param ([string]$dteLogFile)
if (-not $args) {
  $dteLogFile = Read-Host 'Enter the path to DolphinTextureExtraction.log'
  # $dteLogFile = 'E:\Users\Avasam\Pictures\Pitfall\Textures dumps\GPHE52 DTE textures\DolphinTextureExtraction.log'
}
else {
  $dteLogFile = $args[0]
}

$map = [ordered]@{}
Get-Content $dteLogFile |
  Where-Object { $_.StartsWith('[01] Extract: ') } |
  # Remove _arb if DTE was run with arbitrary mipmap detection
  ForEach-Object { $_.Substring(14, $_.Length - 4 - 14) -replace '_arb$', '' } |
  ForEach-Object {
    $key, $value = $_.Split('\')
    if (!$map.Contains($key)) {
      $map[$key] = @()
    }
    $map[$key] += $value
  }

Set-Content `
  "$PSScriptRoot/Console Generator/DTETextureMap.jsonc" `
  "// Generated using: map_textures_from_DTE_log.ps1 '$dteLogFile'"
$map | Sort-Object | ConvertTo-Json | Out-File "$PSScriptRoot/Console Generator/DTETextureMap.jsonc" -Append
