!pip install yt_dlp pydub spleeter
import yt_dlp
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os

def download_audio_from_youtube(youtube_url, output_path):
    # Geçici dosya adı
    temp_file = 'temp_audio.mp3'
    expected_temp_file = 'temp_audio.mp3'

    # yt_dlp seçenekleri
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': temp_file,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    # yt_dlp kullanarak indirme işlemi
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        # Dosyanın tam adını belirle
        if not os.path.isfile(temp_file):
            if os.path.isfile(f"{temp_file}.mp3"):
                temp_file = f"{temp_file}.mp3"
            else:
                raise FileNotFoundError("İndirme başarısız oldu. 'temp_audio.mp3' dosyası bulunamadı.")

        # Ses dosyasını wav formatına dönüştür
        audio = AudioSegment.from_file(temp_file)
        wav_output_path = f"{output_path}.wav"
        audio.export(wav_output_path, format='wav')

        # Geçici mp3 dosyasını kaldır
        os.remove(temp_file)

        return wav_output_path

    except Exception as e:
        print(f"Hata: {e}")
        return None

def separate_audio_with_spleeter(input_audio_path, output_directory):
    # spleeter kullanarak ses ayırma işlemi
    os.system(f'spleeter separate -p spleeter:2stems -o {output_directory} {input_audio_path} -d 3600')

    # Ayırılan dosya yolu
    vocals_path = os.path.join(output_directory, "komple_ses", "vocals.wav")
    return vocals_path

def process_audio(input_audio_path, output_path):
    # Sesi yeniden örnekleme, mono kanala çevirme ve örnek genişliği ayarlama
    sound = AudioSegment.from_file(input_audio_path)
    sound = sound.set_frame_rate(16000)
    sound = sound.set_channels(1)
    sound = sound.set_sample_width(2)
    processed_path = f"{output_path}_processed.wav"
    sound.export(processed_path, format="wav")
    return processed_path

def split_on_silence_and_save(input_audio_path, output_directory):
    # Sessizliğe göre parçalama ve kısa parçaları filtreleme
    sound_file = AudioSegment.from_wav(input_audio_path)
    audio_chunks = split_on_silence(
        sound_file,
        min_silence_len=500,
        silence_thresh=-50
    )

    for i, chunk in enumerate(audio_chunks):
        out_file = os.path.join(output_directory, f"parca_{i}.wav")
        chunk.export(out_file, format="wav")

        # Parçanın süresini kontrol et, 3 saniyeden kısa ise sil
        duration_seconds = len(chunk) / 1000.0
        if duration_seconds < 3:
            os.remove(out_file)

# Kullanım
youtube_url = "https://www.youtube.com/watch?v=Cz_b9EE5H4w"
output_directory = "output"
os.makedirs(output_directory, exist_ok=True)

# YouTube'dan sesi indir
wav_file_path = download_audio_from_youtube(youtube_url, "komple_ses")

if wav_file_path:
    # Spleeter ile sesi ayır
    separated_audio_path = separate_audio_with_spleeter(wav_file_path, output_directory)

    # Sesi işleme tabi tut (16000 Hz, mono, 2-byte örnek genişliği)
    processed_audio_path = process_audio(separated_audio_path, "khz_duzenlenmis")

    # Sessizliğe göre parçaları ayır ve kaydet
    split_on_silence_and_save(processed_audio_path, output_directory)
else:
    print("Ses dosyası indirilemedi.")
