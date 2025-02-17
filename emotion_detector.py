import cv2
from deepface import DeepFace
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import numpy as np

class YuzIfadesiTanima:
    def __init__(self):
        # Ana pencere oluşturma
        self.pencere = tk.Tk()
        self.pencere.title("Yüz İfadesi Tanıma Sistemi")
        self.pencere.geometry("1000x800")
        self.pencere.configure(bg='#f0f0f0')

        # Başlık
        baslik = tk.Label(self.pencere, 
                         text="Yüz İfadesi Tanıma Sistemi", 
                         font=("Arial", 24, "bold"),
                         bg='#f0f0f0',
                         fg='#2c3e50')
        baslik.pack(pady=20)

        # Ana çerçeve
        ana_frame = ttk.Frame(self.pencere)
        ana_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Video gösterici
        self.video_frame = ttk.Frame(ana_frame)
        self.video_frame.pack(pady=10)
        
        # Video çerçevesi
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack()

        # Kontrol paneli
        kontrol_frame = ttk.Frame(ana_frame)
        kontrol_frame.pack(pady=20)

        # Duygu durumu göstergesi
        self.duygu_frame = ttk.Frame(kontrol_frame)
        self.duygu_frame.pack(pady=10)
        
        self.duygu_label = ttk.Label(self.duygu_frame, 
                                    text="Duygu: Bekleniyor...",
                                    font=("Arial", 16))
        self.duygu_label.pack()

        # Güven skoru
        self.guven_label = ttk.Label(self.duygu_frame,
                                    text="Güven Skoru: %0",
                                    font=("Arial", 12))
        self.guven_label.pack()

        # Butonlar
        buton_frame = ttk.Frame(kontrol_frame)
        buton_frame.pack(pady=10)

        # Stil tanımlama
        style = ttk.Style()
        style.configure('Custom.TButton', 
                       font=('Arial', 12),
                       padding=10)

        # Başlat/Durdur butonu
        self.calisiyor = True
        self.baslat_buton = ttk.Button(buton_frame,
                                      text="Durdur",
                                      style='Custom.TButton',
                                      command=self.baslat_durdur)
        self.baslat_buton.pack(side=tk.LEFT, padx=5)

        # Çıkış butonu
        self.cikis_buton = ttk.Button(buton_frame,
                                     text="Çıkış",
                                     style='Custom.TButton',
                                     command=self.cikis)
        self.cikis_buton.pack(side=tk.LEFT, padx=5)

        # Kamera başlatma
        try:
            self.kamera = cv2.VideoCapture(0)
            if not self.kamera.isOpened():
                raise Exception("Kamera başlatılamadı!")
        except Exception as e:
            messagebox.showerror("Hata", str(e))
            self.pencere.destroy()
            return

        # Yüz tespiti için cascade sınıflandırıcı
        self.yuz_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # Video akışını başlat
        self.video_akisi()

    def video_akisi(self):
        if not self.calisiyor:
            return

        ret, frame = self.kamera.read()
        if ret:
            # BGR'den RGB'ye dönüştürme
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Yüz tespiti
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            yuzler = self.yuz_cascade.detectMultiScale(gray, 1.1, 4)

            for (x, y, w, h) in yuzler:
                # Yüz çerçevesi çizme
                cv2.rectangle(frame_rgb, (x, y), (x+w, y+h), (255, 0, 0), 2)
                try:
                    # Duygu analizi
                    analiz = DeepFace.analyze(frame_rgb, 
                                            actions=['emotion'], 
                                            enforce_detection=False)
                    duygu = analiz[0]['dominant_emotion']
                    guven = analiz[0]['emotion'][duygu]
                    
                    # Türkçe duygu karşılıkları
                    duygular = {
                        'angry': 'Kızgın',
                        'disgust': 'İğrenmiş',
                        'fear': 'Korkmuş',
                        'happy': 'Mutlu',
                        'sad': 'Üzgün',
                        'surprise': 'Şaşkın',
                        'neutral': 'Nötr'
                    }
                    
                    self.duygu_label.config(
                        text=f"Duygu: {duygular.get(duygu, duygu)}")
                    self.guven_label.config(
                        text=f"Güven Skoru: %{guven:.1f}")
                except:
                    pass

            # Görüntüyü yeniden boyutlandır
            frame_rgb = cv2.resize(frame_rgb, (640, 480))
            
            # Görüntüyü Tkinter'da göstermek için dönüştürme
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # Her 10ms'de bir güncelle
        self.pencere.after(10, self.video_akisi)

    def baslat_durdur(self):
        self.calisiyor = not self.calisiyor
        if self.calisiyor:
            self.baslat_buton.config(text="Durdur")
            self.video_akisi()
        else:
            self.baslat_buton.config(text="Başlat")

    def cikis(self):
        if messagebox.askokcancel("Çıkış", "Programdan çıkmak istiyor musunuz?"):
            self.calisiyor = False
            if self.kamera.isOpened():
                self.kamera.release()
            self.pencere.destroy()

    def baslat(self):
        self.pencere.protocol("WM_DELETE_WINDOW", self.cikis)
        self.pencere.mainloop()

if __name__ == "__main__":
    uygulama = YuzIfadesiTanima()
    uygulama.baslat()
