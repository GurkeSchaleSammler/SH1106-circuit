$ErrorActionPreference = "Stop"

$files = @(
    "config.py",
    "hardware.py",
    "buttonAndLightsController.py",
    "encoderController.py",
    "displayController.py",
    "soundPlayer.py",
    "ssd1306.py",
    "sh1106.py",
    "main.py"
)

Write-Host "Copying Python files to the real MacroPad..."

foreach ($file in $files) {
    python -m mpremote cp $file :
}

Write-Host "Copying WAV files..."

Get-ChildItem -Filter "sound*.wav" | ForEach-Object {
    python -m mpremote cp $_.FullName :
}

Write-Host "Resetting MacroPad..."

python -m mpremote reset