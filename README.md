# Konuşan Avatar

Windows üzerinde çalışan, Türkçe konuşmalı fotoğraf avatarı prototipidir. Sistem mikrofondan kısa bir ses kaydı alır, Faster-Whisper ile Türkçe metne çevirir, Ollama üzerinden kısa bir cevap üretir, Piper ile cevap sesini oluşturur ve Wav2Lip kullanarak fotoğrafın ağız hareketini üretilen sesle eşleştirir.

Bu proje kişisel ve araştırma amaçlı hazırlanmıştır. **Kendi sesinizi ve kendi fotoğrafınızı veya açık izin aldığınız içerikleri kullanın.** Üretilen ses ve görüntünün yapay olarak oluşturulduğunu uygun yerlerde belirtin.

## Özellikler

| Özellik | Açıklama |
|---|---|
| Fotoğraf kurulumu | İlk çalıştırmada fotoğraf seçer ve `rembg` ile arka planı kaldırır. |
| Türkçe konuşma tanıma | Faster-Whisper ile mikrofon sesini Türkçe metne çevirir. |
| Yerel LLM | Ollama üzerindeki `llama3.2:3b` modeliyle cevap üretir. |
| Türkçe ses üretimi | Piper Türkçe ONNX sesiyle cevap verir. |
| Dudak senkronu | Wav2Lip, fotoğrafı cevap sesine göre hareketli videoya dönüştürür. |
| Windows arayüzü | Tkinter penceresinde avatar videosunu ve sesi oynatır. |
| CPU optimizasyonu | Faster-Whisper int8, kısa kayıt ve düşük Wav2Lip çözünürlüğü kullanılır. |

## Çalışma akışı

```text
Mikrofon
   ↓
Faster-Whisper Türkçe STT
   ↓
Ollama yerel LLM
   ↓
Piper Türkçe TTS
   ↓
Wav2Lip + fotoğraf
   ↓
Tkinter Windows penceresi
```

## Proje yapısı

```text
avatar-proje/
├── app.py                    # Tkinter Windows arayüzü ve konuşma döngüsü
├── main.py                   # Konsol tabanlı alternatif çalışma döngüsü
├── setup.py                  # İlk fotoğraf hazırlama sihirbazı
├── stt.py                    # Mikrofon ve Faster-Whisper
├── llm.py                    # Ollama bağlantısı ve Türkçe cevap filtresi
├── tts.py                    # Piper ses üretimi
├── lipsync.py                # Wav2Lip çağrısı
├── calistir.bat              # Windows başlatma dosyası
├── requirements.txt          # Python bağımlılıkları
├── .gitignore                # Büyük ve kişisel dosyaları dışarıda bırakır
├── foto/                     # Yerel fotoğraf dosyaları; Git'e gönderilmez
├── models/                   # Piper modeli; Git'e gönderilmez
├── sesler/                   # Üretilen WAV dosyaları; Git'e gönderilmez
├── videolar/                 # Üretilen MP4 dosyaları; Git'e gönderilmez
└── Wav2Lip/                  # Yerel klon; Git'e gönderilmez
```

## Gereksinimler

Windows 10 veya Windows 11, Python 3.11 veya 3.12, Git, FFmpeg, Ollama ve VLC gerekir. VLC yalnızca eski konsol akışı için gereklidir; Tkinter uygulaması kendi penceresinde görüntü ve sesi oynatır.

Büyük model dosyaları ve sanal ortam GitHub'a yüklenmemelidir. `avatar-env`, `models`, `Wav2Lip`, fotoğraf, ses ve video çıktıları `.gitignore` içinde dışarıda bırakılmıştır.

## Kurulum

CMD'yi açın ve proje klasörüne geçin:

```bat
cd /d C:\projeler\avatar-proje
```

Sanal ortamı oluşturun ve etkinleştirin:

```bat
python -m venv avatar-env
call avatar-env\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Ollama modelini indirin:

```bat
ollama pull llama3.2:3b
```

Wav2Lip'i proje klasörünün içine indirin:

```bat
git clone https://github.com/Rudrabha/Wav2Lip.git
cd Wav2Lip
python -m pip install -r requirements.txt
mkdir checkpoints
cd ..
```

`wav2lip_gan.pth` dosyasını şu konuma koyun:

```text
C:\projeler\avatar-proje\Wav2Lip\checkpoints\wav2lip_gan.pth
```

Wav2Lip yüz algılama dosyası `s3fd.pth` şu konumda olmalıdır:

```text
C:\projeler\avatar-proje\Wav2Lip\face_detection\detection\sfd\s3fd.pth
```

Piper Türkçe modelinin `.onnx` ve `.onnx.json` dosyalarını şu klasöre koyun:

```text
C:\projeler\avatar-proje\models\
```

## Çalıştırma ve ilk kurulum

Proje klasöründeki `calistir.bat` dosyası ilk çalıştırmada otomatik olarak şunları yapar:

1. Python sanal ortamını oluşturur.
2. `requirements.txt`, OpenCV ve Piper paketlerini kurar.
3. Ollama'da `llama3.2:3b` yoksa indirir.
4. Git kuruluysa Wav2Lip deposunu indirir.
5. Gerekli klasörleri oluşturur.
6. `foto/islenmis.png` yoksa fotoğraf seçme penceresini açar.
7. Bütün büyük model dosyaları hazırsa Python avatar penceresini başlatır.

Başlatmak için dosyaya çift tıklayın veya CMD'den çalıştırın:

```bat
cd /d C:\projeler\avatar-proje
calistir.bat
```

İlk çalıştırmada Python paketleri, Ollama modeli ve Wav2Lip kodu indirileceği için işlem uzun sürebilir. Fotoğraf seçim penceresi yalnızca `foto/islenmis.png` yoksa açılır.

### Manuel indirilmesi gereken büyük modeller

Lisans, boyut ve resmi indirme sayfalarının doğrulama adımları nedeniyle `calistir.bat` aşağıdaki büyük ağırlıkları otomatik indirmez; eksik olduklarında ekranda kesin konumlarını gösterir:

```text
models\*.onnx
Wav2Lip\checkpoints\wav2lip_gan.pth
Wav2Lip\face_detection\detection\sfd\s3fd.pth
```

Bu dosyaları README'deki resmi model bağlantılarından indirip proje ana dizinine de koyabilirsiniz. `calistir.bat` ilk çalıştırmada bunları otomatik olarak doğru klasörlere taşır:

```text
Proje ana dizini\\wav2lip_gan.pth  → Wav2Lip\\checkpoints\\wav2lip_gan.pth
Proje ana dizini\\s3fd.pth          → Wav2Lip\\face_detection\\detection\\sfd\\s3fd.pth
Proje ana dizini\\*.onnx            → models\\*.onnx
Proje ana dizini\\*.onnx.json       → models\\*.onnx.json
```

Taşıma işleminden sonra `calistir.bat` dosyasını tekrar çalıştırmanız yeterlidir.

Alternatif olarak:

```bat
python app.py
```

Açılan pencerede **Konuşmayı Başlat** düğmesine basın. Uygulama yaklaşık üç saniye mikrofonu dinler, cevabı üretir ve avatar videosunu aynı Tkinter penceresinde oynatır.

## GitHub'a yükleme

Önce GitHub'da yeni ve boş bir repository oluşturun. Örnek repository adı:

```text
konusan-avatar
```

GitHub'da README, `.gitignore` veya lisans dosyasını otomatik oluşturmayın; bunlar bu projede zaten bulunmaktadır.

Sonra CMD'de:

```bat
cd /d C:\projeler\avatar-proje

git init
git branch -M main
git add .
git status
git commit -m "İlk Windows avatar sürümü"
git remote add origin https://github.com/KULLANICI_ADINIZ/konusan-avatar.git
git push -u origin main
```

`KULLANICI_ADINIZ` bölümünü kendi GitHub kullanıcı adınızla değiştirin. GitHub giriş isterse tarayıcı üzerinden doğrulama yapın veya GitHub Desktop kullanın.

Yüklemeden önce `git status` çıktısında aşağıdaki dosyaların görünmediğinden emin olun:

```text
avatar-env/
models/*.onnx
Wav2Lip/
foto/orijinal.jpg
foto/islenmis.png
sesler/*.wav
videolar/*.mp4
```

## Güncelleme gönderme

Kodda değişiklik yaptıktan sonra:

```bat
git add .
git commit -m "Windows avatar arayüzü güncellendi"
git push
```

## Fotoğrafı değiştirme

```bat
del foto\islenmis.png
python setup.py
```

## Hız ve doğruluk notları

Intel UHD Graphics 630 üzerinde Wav2Lip CPU ile çalıştığı için her cevapta video üretimi gecikmeli olabilir. Faster-Whisper `small` modeli Türkçe doğruluğunu artırır ancak `tiny` modelinden daha fazla disk ve işlem süresi kullanır. Daha düşük gecikme için `stt.py` içinde `small` yerine `tiny` kullanılabilir.

Gerçek zamanlı, milisaniye gecikmeli dudak hareketi için Wav2Lip yerine GPU destekli bir avatar motoru veya ses enerjisine göre çalışan basit 2D ağız animasyonu gerekir. Bu repository'deki Wav2Lip akışı daha gerçekçi fakat CPU üzerinde daha yavaştır.

## Resmi kaynaklar

- [Ollama](https://ollama.com/)
- [Wav2Lip](https://github.com/Rudrabha/Wav2Lip)
- [Piper voices](https://huggingface.co/rhasspy/piper-voices)
- [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
