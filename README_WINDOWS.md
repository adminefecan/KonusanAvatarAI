# Konuşan Avatar — Windows Paketi

Bu proje fotoğrafınızı avatar yüzü olarak kullanır. Mikrofonla yaklaşık 5 saniye konuşmanızı kaydeder, konuşmayı metne çevirir, Ollama ile Türkçe cevap üretir, Piper ile cevap sesini üretir ve Wav2Lip ile fotoğrafın ağzını bu sese göre hareket ettiren kısa bir video oluşturur. Son video VLC ile tam ekran oynatılır.

## Önemli açıklama

Bu paket şu anda bağımsız bir `.exe` değildir. `calistir.bat` dosyasına çift tıkladığınızda Windows CMD arka planda çalışır; konuşma sırasında üretilen avatar videosu ayrı bir **VLC penceresinde** açılır. Fotoğraf, `foto/islenmis.png` dosyasıdır ve Wav2Lip'in yüzü hareket ettireceği kaynak görüntüdür.

Akış:

```text
Mikrofon → Faster-Whisper → Ollama → Piper → Wav2Lip + fotoğraf → VLC video penceresi
```

## Kurulum

CMD:

```bat
cd /d C:\projeler\avatar-proje
python -m venv avatar-env
call avatar-env\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install piper-tts
```

Ollama modeli:

```bat
ollama pull llama3.2:3b
```

Piper Türkçe `.onnx` ve `.onnx.json` dosyalarını `models` klasörüne koyun. Wav2Lip deposu, `wav2lip_gan.pth` ve `s3fd.pth` dosyaları da README'deki konumlarda olmalıdır.

## Çalıştırma

`calistir.bat` dosyasına çift tıklayın veya CMD'den çalıştırın:

```bat
cd /d C:\projeler\avatar-proje
calistir.bat
```

İlk çalıştırmada fotoğraf seçme penceresi açılır. Fotoğraf işlendikten sonra `foto/islenmis.png` olarak saklanır. Sonraki çalıştırmalarda aynı fotoğraf otomatik kullanılır.

## Fotoğrafı değiştirme

```bat
del foto\islenmis.png
python setup.py
```

## Sorun giderme

`WinError 2` ve Piper bulunamadı hatası alırsanız:

```bat
call avatar-env\Scripts\activate.bat
python -m pip install piper-tts
python -m piper --help
```

`librosa.filters.mel` hatası alırsanız Wav2Lip içindeki `audio.py` dosyasında `librosa.filters.mel` çağrısının `sr=...` ve `n_fft=...` adlı parametrelerle yapılması gerekir. Bu paketin Windows uyumlu dosyaları bu düzeltmeyi içerir.
