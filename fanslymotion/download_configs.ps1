# Download config files for SVD model
$baseUrl = "https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt/resolve/main"
$basePath = ".\cache\models\models--stabilityai--stable-video-diffusion-img2vid-xt\snapshots\9e43909513c6714f1bc78bcb44d96e733cd242aa"

Write-Host "Downloading config files..." -ForegroundColor Cyan

# Create directories
$dirs = @(
    "$basePath\feature_extractor",
    "$basePath\image_encoder",
    "$basePath\scheduler",
    "$basePath\unet",
    "$basePath\vae"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

# Download config files
$configs = @(
    @{path="model_index.json"; dest="$basePath\model_index.json"},
    @{path="feature_extractor/preprocessor_config.json"; dest="$basePath\feature_extractor\preprocessor_config.json"},
    @{path="image_encoder/config.json"; dest="$basePath\image_encoder\config.json"},
    @{path="scheduler/scheduler_config.json"; dest="$basePath\scheduler\scheduler_config.json"},
    @{path="unet/config.json"; dest="$basePath\unet\config.json"},
    @{path="vae/config.json"; dest="$basePath\vae\config.json"}
)

foreach ($config in $configs) {
    $url = "$baseUrl/$($config.path)"
    $dest = $config.dest
    Write-Host "  Downloading $($config.path)..." -ForegroundColor Gray
    try {
        Invoke-WebRequest -Uri $url -OutFile $dest -ErrorAction Stop
        Write-Host "    OK" -ForegroundColor Green
    } catch {
        Write-Host "    FAILED: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Config files downloaded!" -ForegroundColor Green
Write-Host ""
Write-Host "Now download the big safetensors files manually:" -ForegroundColor Yellow
Write-Host "  1. image_encoder/model.fp16.safetensors (1.2 GB)" -ForegroundColor Gray
Write-Host "  2. unet/diffusion_pytorch_model.fp16.safetensors (2.9 GB)" -ForegroundColor Gray
Write-Host "  3. vae/diffusion_pytorch_model.fp16.safetensors (10.3 GB)" -ForegroundColor Gray
Write-Host ""




