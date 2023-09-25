Push-Location "Mechanisms\Common"
$null = .\build_astrocyte_`&_neuron_mechs.ps1 $true $true $false
Pop-Location
Write-Host ""
Write-Host "Press any key to exit ..."
$null = Read-Host