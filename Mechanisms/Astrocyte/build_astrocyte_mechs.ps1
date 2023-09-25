Push-Location "..\Common"
$null = .\build_astrocyte_`&_neuron_mechs.ps1 $true $false $false
Pop-Location
Write-Host ""
Write-Host "Press any key to exit ..."
$null = Read-Host