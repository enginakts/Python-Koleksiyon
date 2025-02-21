import speech_recognition as sr
import openai
from pathlib import Path
import os
from pydub import AudioSegment
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading

class SesYaziDonusturucu:
    def __init__(self, api_key):
        """
        Sınıfın başlatıcı metodu
        :param api_key: OpenAI API anahtarı
        """
        self.recognizer = sr.Recognizer()
        openai.api_key = api_key
        
        # FFmpeg yolunu ayarla
        if os.name == 'nt':  # Windows için
            AudioSegment.converter = r"C:\\ffmpeg\\bin\\ffmpeg.exe"
            AudioSegment.ffmpeg = r"C:\\ffmpeg\\bin\\ffmpeg.exe"
            AudioSegment.ffprobe = r"C:\\ffmpeg\\bin\\ffprobe.exe"
        
        self.create_gui()
    
    def create_gui(self):
        """
        Kullanıcı arayüzünü oluşturur
        """
        # Ana pencere oluşturma
        self.window = tk.Tk()
        self.window.title("Ses Dosyası Özetleyici")
        self.window.geometry("800x600")
        
        # Stil tanımlama
        style = ttk.Style()
        style.configure('Custom.TButton', padding=10)
        
        # Dosya seçme butonu
        self.dosya_sec_btn = ttk.Button(
            self.window, 
            text="Ses Dosyası Seç", 
            command=self.dosya_sec,
            style='Custom.TButton'
        )
        self.dosya_sec_btn.pack(pady=20)
        
        # Seçilen dosya adı etiketi
        self.dosya_adi_label = ttk.Label(self.window, text="Seçilen dosya: ")
        self.dosya_adi_label.pack(pady=10)
        
        # İşlem durumu için progress bar
        self.progress = ttk.Progressbar(
            self.window, 
            orient="horizontal", 
            length=300, 
            mode="indeterminate"
        )
        self.progress.pack(pady=20)
        
        # Metin ve özet için text alanları
        self.metin_frame = ttk.LabelFrame(self.window, text="Çevrilen Metin")
        self.metin_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.metin_alani = tk.Text(self.metin_frame, height=10)
        self.metin_alani.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.ozet_frame = ttk.LabelFrame(self.window, text="Özet")
        self.ozet_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.ozet_alani = tk.Text(self.ozet_frame, height=10)
        self.ozet_alani.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Kaydet butonu
        self.kaydet_btn = ttk.Button(
            self.window, 
            text="Sonuçları Kaydet",
            command=self.sonuclari_kaydet,
            style='Custom.TButton'
        )
        self.kaydet_btn.pack(pady=20)
        
        self.window.mainloop()
    
    def dosya_sec(self):
        """
        Dosya seçme dialogunu açar ve seçilen dosyayı işler
        """
        dosya_yolu = filedialog.askopenfilename(
            filetypes=[
                ("Ses Dosyaları", "*.mp3 *.wav *.m4a *.ogg")
            ]
        )
        if dosya_yolu:
            self.dosya_adi_label.config(text=f"Seçilen dosya: {Path(dosya_yolu).name}")
            self.progress.start()
            # İşlemi arka planda başlat
            threading.Thread(
                target=self.dosyayi_isle, 
                args=(dosya_yolu,),
                daemon=True
            ).start()

    def dosyayi_isle(self, dosya_yolu):
        """
        Seçilen dosyayı işler ve sonuçları gösterir
        """
        try:
            # GUI'yi güncelle
            self.window.after(0, lambda: self.metin_alani.delete(1.0, tk.END))
            self.window.after(0, lambda: self.metin_alani.insert(tk.END, "Ses işleniyor...\n"))
            
            # Ses dosyasını metne çevir
            metin = self.ses_dosyasini_yaziya_cevir(dosya_yolu)
            
            # Metni göster
            self.window.after(0, lambda: self.metin_alani.delete(1.0, tk.END))
            self.window.after(0, lambda: self.metin_alani.insert(tk.END, metin))
            
            # Metni özetle
            self.window.after(0, lambda: self.ozet_alani.delete(1.0, tk.END))
            self.window.after(0, lambda: self.ozet_alani.insert(tk.END, "Metin özetleniyor...\n"))
            
            ozet = self.metni_ozetle(metin)
            
            # Özeti göster
            self.window.after(0, lambda: self.ozet_alani.delete(1.0, tk.END))
            self.window.after(0, lambda: self.ozet_alani.insert(tk.END, ozet))
            
        except Exception as e:
            hata_mesaji = f"İşlem sırasında hata oluştu:\n{str(e)}"
            self.window.after(0, lambda: messagebox.showerror("Hata", hata_mesaji))
            self.window.after(0, lambda: self.metin_alani.delete(1.0, tk.END))
            self.window.after(0, lambda: self.metin_alani.insert(tk.END, f"HATA: {hata_mesaji}"))
        finally:
            self.window.after(0, self.progress.stop)

    def sonuclari_kaydet(self):
        """
        Metin ve özeti dosyaya kaydeder
        """
        dosya_yolu = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if dosya_yolu:
            try:
                with open(dosya_yolu, 'w', encoding='utf-8') as f:
                    f.write("ORİJİNAL METİN:\n\n")
                    f.write(self.metin_alani.get(1.0, tk.END))
                    f.write("\n\nÖZET:\n\n")
                    f.write(self.ozet_alani.get(1.0, tk.END))
                messagebox.showinfo("Başarılı", "Sonuçlar başarıyla kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Kayıt sırasında hata oluştu: {str(e)}")

    def ses_dosyasini_yaziya_cevir(self, ses_dosyasi_yolu):
        """
        Ses dosyasını metne çevirir
        :param ses_dosyasi_yolu: İşlenecek ses dosyasının yolu
        :return: Çevrilen metin
        """
        try:
            # Ses dosyasının var olup olmadığını kontrol et
            if not os.path.exists(ses_dosyasi_yolu):
                raise Exception(f"Ses dosyası bulunamadı: {ses_dosyasi_yolu}")

            # Ses dosyasının uzantısını kontrol et
            dosya_formati = Path(ses_dosyasi_yolu).suffix.lower()
            gecici_wav = None
            
            if dosya_formati != '.wav':
                try:
                    # Eğer WAV formatında değilse, WAV'a çevir
                    print(f"Dosya {dosya_formati} formatında, WAV'a dönüştürülüyor...")
                    ses = AudioSegment.from_file(ses_dosyasi_yolu)
                    gecici_wav = str(Path(ses_dosyasi_yolu).parent / "gecici.wav")
                    ses.export(gecici_wav, format="wav")
                    ses_dosyasi_yolu = gecici_wav
                    print("WAV dönüşümü tamamlandı.")
                except Exception as e:
                    raise Exception(f"Ses dönüştürme hatası: {str(e)}\nLütfen ffmpeg'in kurulu olduğundan emin olun.")

            print("Ses dosyası okunuyor...")
            with sr.AudioFile(ses_dosyasi_yolu) as kaynak:
                # Gürültü azaltma uygula
                print("Gürültü azaltma uygulanıyor...")
                self.recognizer.adjust_for_ambient_noise(kaynak, duration=0.5)
                
                # Sesi yakala
                print("Ses kaydı alınıyor...")
                ses = self.recognizer.record(kaynak)
                
                # Sesi metne çevir
                print("Ses metne çevriliyor...")
                metin = self.recognizer.recognize_google(ses, language="tr-TR")
                print("Ses metne çevrildi.")
                
                if not metin:
                    raise Exception("Ses metne çevrilemedi veya boş metin döndü.")
                
                return metin

        except sr.UnknownValueError:
            raise Exception("Ses anlaşılamadı veya konuşma algılanamadı.")
        except sr.RequestError as e:
            raise Exception(f"Google Speech Recognition servisi hatası: {str(e)}")
        except Exception as e:
            raise Exception(f"Ses işleme hatası: {str(e)}")
        finally:
            if gecici_wav and os.path.exists(gecici_wav):
                try:
                    os.remove(gecici_wav)
                except:
                    print("Geçici dosya silinirken hata oluştu.")

    def metni_ozetle(self, metin, max_tokens=150):
        """
        Metni OpenAI GPT kullanarak özetler
        :param metin: Özetlenecek metin
        :param max_tokens: Özet uzunluğu
        :return: Özetlenmiş metin
        """
        try:
            yanit = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen bir metin özetleme uzmanısın."},
                    {"role": "user", "content": f"Lütfen bu metni özetle: {metin}"}
                ],
                max_tokens=max_tokens
            )
            return yanit.choices[0].message.content
        except Exception as e:
            return f"Özetleme sırasında hata oluştu: {str(e)}"

def main():
    """
    Ana program fonksiyonu
    """
    # OpenAI API anahtarınızı buraya girin
    api_key = "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"
    
    # Uygulamayı başlat
    SesYaziDonusturucu(api_key)

if __name__ == "__main__":
    main()
