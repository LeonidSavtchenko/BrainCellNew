param (
    [bool]$isBuildMechsForAstrocyte = $true,
    [bool]$isBuildMechsForNeuron = $true,
    [bool]$isPauseOnExit = $true
)


function BuildMechsForThisCellType {
    param (
        [string]$cellType
    )
    
    $buildScriptPath = "C:\nrn\bin\mknrndll.bat"
    
    $cellTypeFolderName = $cellType
    $modFilesFolderName = "MOD files"
    $tempFolderName = "temp_folder"
    
    Push-Location ..
    
    if (Test-Path $tempFolderName) {
        Remove-Item $tempFolderName -Force -Recurse
    }
    
    New-Item -ItemType Directory -Name $tempFolderName | Out-Null
    Set-Location $tempFolderName
    
    # Copy all mechanisms from the common folder to the temporary folder
    Copy-Item "..\Common\$modFilesFolderName\*" -Destination .
    
    # Copy all mechanisms from the cell-specific folder to the temporary folder with overwrite prompt
    Get-ChildItem -Path "..\$cellTypeFolderName\$modFilesFolderName\*" | ForEach-Object {
        $dstFile = Join-Path -Path . -ChildPath $_.Name
        if (Test-Path -Path $dstFile) {
            Write-Host ""
            do {
                $choice = Read-Host "The file `"$($_.Name)`" is present in two folders: `"Common`" and `"$cellTypeFolderName`". Which one to use? (1/[2])"
                if ($choice -eq '1') {
                    break
                } elseif ($choice -eq '2' -or $choice -eq '') {
                    Copy-Item -Path $_.FullName -Destination $dstFile -Force
                    break
                } else {
                    Write-Host "Incorrect choice. Try again."
                }
            } while ($true)
        } else {
            Copy-Item -Path $_.FullName -Destination $dstFile
        }
    }
    
    Write-Host ""
    Write-Host "Building $cellType mechs ..."
    Write-Host ""
    
    # Call "mknrndll.bat" with elevated privileges
    Start-Process -FilePath "cmd.exe" -ArgumentList "/C", "cd /d `"$PWD`" && `"$buildScriptPath`"" -Verb RunAs -Wait
    
    Write-Host ""
    
    # "mknrndll.bat" does not set $LASTEXITCODE to 1 on error, so we have to rely on "Test-Path" cmdlet
    $isError = -not (Test-Path "nrnmech.dll")
    
    if (-not $isError) {
        do {
            try {
                Copy-Item -Path .\nrnmech.dll -Destination "..\..\Nanogeometry\$cellTypeFolderName\" -Force
                Move-Item -Path .\nrnmech.dll -Destination "..\$cellTypeFolderName\" -Force
                break
            } catch {
                Write-Host "Cannot replace `"nrnmech.dll`" in the destination folder. Perhaps the old DLL is in use right now."
                Write-Host "Please close NEURON and press any key to retry ..."
                $null = Read-Host
            }
        } while ($true)
        
        Set-Location ..
        Remove-Item $tempFolderName -Force -Recurse
        
        Write-Host "    Success!"
    } else {
        Write-Host "    Build Failed!"
    }
    
    Pop-Location
    
    return $isError
}

function EndThisScript {
    if ($isPauseOnExit) {
        Write-Host ""
        Write-Host "Press any key to exit ..."
        $null = Read-Host
    }
    
    Exit
}


if ($isBuildMechsForAstrocyte) {
    $isError = (BuildMechsForThisCellType "Astrocyte")[-1]
    if ($isError) {
        EndThisScript
    }
}

if ($isBuildMechsForNeuron) {
    $null = BuildMechsForThisCellType "Neuron"
}

EndThisScript