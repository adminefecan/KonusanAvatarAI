@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

title Konusan Avatar - Ilk Kurulum ve Baslatma
cd /d "%~dp0"

echo ========================================
echo   KONUSAN AVATAR - KURULUM / BASLATMA
echo ========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [HATA] Python bulunamadi.
    echo Python 3.11 veya 3.12 kurun: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

if not exist "avatar-env\Scripts\python.exe" (
    echo [1/7] Python sanal ortami olusturuluyor...
    python -m venv avatar-env
    if errorlevel 1 goto :fail
)

set "PY=%CD%\avatar-env\Scripts\python.exe"
if not exist "%PY%" goto :fail

if not exist ".kurulum_tamam" (
    echo [2/7] Python paketleri kuruluyor. Ilk seferde uzun surebilir...
    "%PY%" -m pip install --upgrade pip
    "%PY%" -m pip install -r requirements.txt
    "%PY%" -m pip install opencv-python piper-tts
    if errorlevel 1 goto :fail
    echo tamam>".kurulum_tamam"
)

if not exist "foto" mkdir "foto"
if not exist "models" mkdir "models"
if not exist "sesler" mkdir "sesler"
if not exist "videolar" mkdir "videolar"

rem Ana dizindeki Piper modelini models klasorune tasir.
if not exist "models\*.onnx" (
    for %%F in ("*.onnx") do move /Y "%%~fF" "models\" >nul 2>nul
)
for %%F in ("*.onnx.json") do move /Y "%%~fF" "models\" >nul 2>nul

where ollama >nul 2>nul
if errorlevel 1 (
    echo [UYARI] Ollama bulunamadi. https://ollama.com/download/windows adresinden kurun.
) else (
    ollama list | findstr /I "llama3.2:3b" >nul 2>nul
    if errorlevel 1 (
        echo [3/7] Ollama llama3.2:3b modeli indiriliyor...
        ollama pull llama3.2:3b
    )
)

where git >nul 2>nul
if errorlevel 1 (
    echo [UYARI] Git bulunamadi. Wav2Lip otomatik klonlanamiyor.
) else if not exist "Wav2Lip\inference.py" (
    echo [4/7] Wav2Lip kodu indiriliyor...
    git clone https://github.com/Rudrabha/Wav2Lip.git
    if exist "Wav2Lip\requirements.txt" "%PY%" -m pip install -r Wav2Lip\requirements.txt
)

rem Ana dizindeki Wav2Lip agirliklarini gerekli alt klasorlere tasir.
if exist "Wav2Lip\inference.py" (
    if not exist "Wav2Lip\checkpoints" mkdir "Wav2Lip\checkpoints"
    if exist "wav2lip_gan.pth" if not exist "Wav2Lip\checkpoints\wav2lip_gan.pth" move /Y "wav2lip_gan.pth" "Wav2Lip\checkpoints\" >nul
    if not exist "Wav2Lip\face_detection\detection\sfd" mkdir "Wav2Lip\face_detection\detection\sfd"
    if exist "s3fd.pth" if not exist "Wav2Lip\face_detection\detection\sfd\s3fd.pth" move /Y "s3fd.pth" "Wav2Lip\face_detection\detection\sfd\" >nul
)

if not exist "models\*.onnx" (
    echo [UYARI] Piper .onnx modeli eksik.
    echo Turkce Piper modelini models klasorune koyun.
)

if not exist "Wav2Lip\checkpoints\wav2lip_gan.pth" (
    echo [UYARI] Wav2Lip agirligi eksik: Wav2Lip\checkpoints\wav2lip_gan.pth
    echo Modeli resmi Wav2Lip Google Drive baglantisindan indirmeniz gerekir.
)

if not exist "Wav2Lip\face_detection\detection\sfd\s3fd.pth" (
    echo [UYARI] Yuz modeli eksik: Wav2Lip\face_detection\detection\sfd\s3fd.pth
)

if not exist "foto\islenmis.png" (
    echo [5/7] Ilk kurulum: fotograf secme penceresi aciliyor...
    "%PY%" setup.py
    if errorlevel 1 goto :fail
)

if not exist "models\*.onnx" goto :missing
if not exist "Wav2Lip\inference.py" goto :missing
if not exist "Wav2Lip\checkpoints\wav2lip_gan.pth" goto :missing
if not exist "Wav2Lip\face_detection\detection\sfd\s3fd.pth" goto :missing

set "PIPER_MODEL="
for %%F in ("%CD%\models\*.onnx") do if not defined PIPER_MODEL set "PIPER_MODEL=%%~fF"
set "WAV2LIP_DIR=%CD%\Wav2Lip"
set "WAV2LIP_CHECKPOINT=%CD%\Wav2Lip\checkpoints\wav2lip_gan.pth"
set "OLLAMA_MODEL=llama3.2:3b"

echo [6/7] Model yolları hazir.
echo [7/7] Python avatar uygulamasi baslatiliyor...
echo.
"%PY%" app.py
if errorlevel 1 goto :fail
endlocal
exit /b 0

:missing
echo.
echo [BEKLENEN DOSYALAR EKSIK]
echo Yukaridaki uyari mesajlarindaki model dosyalarini indirin.
pause
endlocal
exit /b 1

:fail
echo.
echo [HATA] Kurulum veya baslatma basarisiz oldu. Hata mesajini kontrol edin.
pause
endlocal
exit /b 1
