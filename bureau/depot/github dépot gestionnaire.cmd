@echo off
chcp 65001 >nul
echo (c) pitagna corporation 2025
echo.
echo ...
timeout 2 /nobreak >nul
:debut
set /p "option=cloner?(1)envoyer?(2):"
if "%option%"=="1" (
	goto clone
) else (
	if "%option%"=="2" (
		goto envoyer
	) else (
		goto debut
	)
)
:clone
set /p "url=Entrez l'URL du dépôt à cloner : "
git clone %url%
goto fin

:envoyer
set /p "depot=nom du fichier de dépot : "
if exist "%depot%\" (
    cd "%depot%"
) else (
    echo Dossier "%depot%" introuvable.
    goto fin
)
git add .
set /p "msg=Message du commit : "
git commit -m "%msg%"
git push
goto fin

:fin
echo Opération terminée !
pause
