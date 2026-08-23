Write-Host "Starte main.py auf dem laufenden Wokwi-MicroPython-Pico..."

python -m mpremote `
    connect port:rfc2217://localhost:4000 `
    mount . `
    exec "import main"
