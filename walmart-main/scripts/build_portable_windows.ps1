param(
    [string]$PythonEmbedUrl = 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip',
    [string]$PackageName = 'GondolaVision_MVP_Windows_x64_2026-10-21'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$stage = Join-Path $projectRoot "artifacts\portable\$PackageName"
$zip = Join-Path $projectRoot "artifacts\portable\$PackageName.zip"
$downloads = Join-Path $projectRoot 'artifacts\downloads'
$pythonZip = Join-Path $downloads 'python-3.11.9-embed-amd64.zip'
$sitePackages = Join-Path $projectRoot '.venv\Lib\site-packages'
$weights = Join-Path $projectRoot 'artifacts\models\gondola-yolo26n.pt'
$companionWeights = Join-Path $projectRoot 'artifacts\models\companero-yolo.pt'
$metadata = Join-Path $projectRoot 'artifacts\models\metadata.json'
$companionMetadata = Join-Path $projectRoot 'artifacts\models\companion_metadata.json'
$demo = Join-Path $projectRoot 'data\shelf_products_v2\images\val\045_8_jpeg_jpg.rf.cf4d78bc08b6bee810ccfc30b5497398.jpg'

if ($PackageName -notmatch '^GondolaVision_MVP_Windows_x64_[A-Za-z0-9_-]+$') {
    throw 'Nombre de paquete invalido.'
}
if ((Test-Path -LiteralPath $stage) -or (Test-Path -LiteralPath $zip)) {
    throw 'El paquete ya existe. Revise la copia existente antes de crear otra version.'
}
if (-not (Test-Path -LiteralPath $sitePackages) -or -not (Test-Path -LiteralPath $weights) -or -not (Test-Path -LiteralPath $companionWeights) -or -not (Test-Path -LiteralPath $metadata) -or -not (Test-Path -LiteralPath $demo)) {
    throw 'Faltan .venv, los pesos de ambos modelos, los metadatos activos o la imagen de demostracion.'
}

New-Item -ItemType Directory -Path $downloads -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $stage 'runtime\Lib') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $stage 'artifacts\models') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $stage 'demo') -Force | Out-Null

if (-not (Test-Path -LiteralPath $pythonZip)) {
    Invoke-WebRequest -Uri $PythonEmbedUrl -OutFile $pythonZip
}
Expand-Archive -LiteralPath $pythonZip -DestinationPath (Join-Path $stage 'runtime')
Copy-Item -LiteralPath $sitePackages -Destination (Join-Path $stage 'runtime\Lib\site-packages') -Recurse
Copy-Item -LiteralPath (Join-Path $projectRoot 'deploy\python311._pth') -Destination (Join-Path $stage 'runtime\python311._pth')
Copy-Item -LiteralPath (Join-Path $projectRoot 'backend') -Destination (Join-Path $stage 'backend') -Recurse
Copy-Item -LiteralPath (Join-Path $projectRoot 'frontend') -Destination (Join-Path $stage 'frontend') -Recurse
Copy-Item -LiteralPath $weights -Destination (Join-Path $stage 'artifacts\models\gondola-yolo26n.pt')
Copy-Item -LiteralPath $companionWeights -Destination (Join-Path $stage 'artifacts\models\companero-yolo.pt')
Copy-Item -LiteralPath $metadata -Destination (Join-Path $stage 'artifacts\models\metadata.json')
if (Test-Path -LiteralPath $companionMetadata) {
    Copy-Item -LiteralPath $companionMetadata -Destination (Join-Path $stage 'artifacts\models\companion_metadata.json')
}
Copy-Item -LiteralPath $demo -Destination (Join-Path $stage 'demo\gondola_ejemplo.jpg')
Copy-Item -LiteralPath (Join-Path $projectRoot 'deploy\INICIAR_MVP_DUOC.cmd') -Destination $stage
Copy-Item -LiteralPath (Join-Path $projectRoot 'deploy\LEEME_DUOC.txt') -Destination $stage
Copy-Item -LiteralPath (Join-Path $projectRoot 'deploy\CREDENCIALES_DEMO.txt') -Destination $stage
Copy-Item -LiteralPath (Join-Path $projectRoot 'backend\requirements.txt') -Destination (Join-Path $stage 'requirements.txt')

Write-Host "Carpeta preparada: $stage"
Write-Host 'Comprimiendo el paquete portable...'
Compress-Archive -LiteralPath $stage -DestinationPath $zip -CompressionLevel Optimal
$hash = Get-FileHash -LiteralPath $zip -Algorithm SHA256
Write-Host "ZIP listo: $zip"
Write-Host "SHA256: $($hash.Hash)"
