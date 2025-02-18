import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class YuzAnonimlestirme:
    def __init__(self, root):
        self.root = root
        self.root.title("Yüz Anonimleştirme Uygulaması")
        self.root.geometry("800x600")
        
        # Ana çerçeve
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)
        
        # Resim gösterme alanı
        self.canvas = tk.Canvas(self.frame, width=600, height=400)
        self.canvas.pack()
        
        # Butonlar
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(pady=20)
        
        self.btn_yukle = tk.Button(self.btn_frame, text="Resim Yükle", 
                                  command=self.resim_yukle, width=15)
        self.btn_yukle.pack(side=tk.LEFT, padx=10)
        
        self.btn_anonimlestir = tk.Button(self.btn_frame, text="Yüzleri Anonimleştir", 
                                         command=self.yuzleri_anonimlestir, width=15)
        self.btn_anonimlestir.pack(side=tk.LEFT, padx=10)
        
        self.btn_kaydet = tk.Button(self.btn_frame, text="Resmi Kaydet", 
                                   command=self.resmi_kaydet, width=15)
        self.btn_kaydet.pack(side=tk.LEFT, padx=10)
        
        # Değişkenler
        self.yuklenen_resim = None
        self.islenmis_resim = None
        self.yuz_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def resim_yukle(self):
        dosya_yolu = filedialog.askopenfilename(
            filetypes=[("Resim Dosyaları", "*.png *.jpg *.jpeg *.bmp *.gif")])
        
        if dosya_yolu:
            self.yuklenen_resim = cv2.imread(dosya_yolu)
            self.islenmis_resim = self.yuklenen_resim.copy()
            self.resim_goster(self.yuklenen_resim)
    
    def resim_goster(self, resim):
        if resim is not None:
            # OpenCV BGR'den RGB'ye dönüştürme
            rgb_resim = cv2.cvtColor(resim, cv2.COLOR_BGR2RGB)
            
            # Resmi canvas boyutuna uygun şekilde yeniden boyutlandırma
            h, w = rgb_resim.shape[:2]
            canvas_w, canvas_h = 600, 400
            
            # En-boy oranını koru
            oran = min(canvas_w/w, canvas_h/h)
            yeni_w, yeni_h = int(w*oran), int(h*oran)
            
            rgb_resim = cv2.resize(rgb_resim, (yeni_w, yeni_h))
            
            # PIL Image'e dönüştürme
            pil_resim = Image.fromarray(rgb_resim)
            self.tk_resim = ImageTk.PhotoImage(pil_resim)
            
            # Canvas'ı temizle ve yeni resmi göster
            self.canvas.delete("all")
            self.canvas.create_image(canvas_w//2, canvas_h//2, image=self.tk_resim)

    def yuzleri_anonimlestir(self):
        if self.yuklenen_resim is None:
            messagebox.showwarning("Uyarı", "Lütfen önce bir resim yükleyin!")
            return
        
        # Orijinal resmin bir kopyasını oluştur
        self.islenmis_resim = self.yuklenen_resim.copy()
        
        # Yüz tespiti için resmi gri tonlamaya çevir
        gri_resim = cv2.cvtColor(self.yuklenen_resim, cv2.COLOR_BGR2GRAY)
        
        # Yüz tespiti yap (scaleFactor ve minNeighbors parametreleri optimize edildi)
        # scaleFactor: Her ölçeklendirme adımında görüntünün ne kadar küçültüleceğini belirtir
        # minNeighbors: Yüz olarak kabul edilmesi için gereken minimum komşu sayısı
        yuzler = self.yuz_cascade.detectMultiScale(
            gri_resim,
            scaleFactor=1.2,  # Daha hassas tespit için değer düşürüldü
            minNeighbors=6,   # Yanlış tespitleri azaltmak için arttırıldı
            minSize=(30, 30)  # Minimum yüz boyutu
        )
        
        # Her tespit edilen yüz için işlem yap
        for (x, y, w, h) in yuzler:
            # Yüz bölgesini biraz genişlet (saç ve çene bölgelerini de kapsaması için)
            genisletme_orani = 0.1
            yeni_x = max(0, int(x - w * genisletme_orani))
            yeni_y = max(0, int(y - h * genisletme_orani))
            yeni_w = min(self.islenmis_resim.shape[1] - yeni_x, int(w * (1 + 2 * genisletme_orani)))
            yeni_h = min(self.islenmis_resim.shape[0] - yeni_y, int(h * (1 + 2 * genisletme_orani)))
            
            # Genişletilmiş yüz bölgesini al
            yuz_bolge = self.islenmis_resim[yeni_y:yeni_y+yeni_h, yeni_x:yeni_x+yeni_w]
            
            # Pikselleştirme efekti uygula
            # 1. Görüntüyü küçült
            kucultme_orani = 0.1
            kucuk_yuz = cv2.resize(yuz_bolge, 
                                 (max(1, int(yeni_w * kucultme_orani)), 
                                  max(1, int(yeni_h * kucultme_orani))),
                                 interpolation=cv2.INTER_LINEAR)
            
            # 2. Görüntüyü orijinal boyutuna getir (pikselleştirme efekti)
            piksel_yuz = cv2.resize(kucuk_yuz, (yeni_w, yeni_h), 
                                  interpolation=cv2.INTER_NEAREST)
            
            # 3. Kenarları yumuşat
            bulanik_yuz = cv2.GaussianBlur(piksel_yuz, (3, 3), 0)
            
            # 4. İşlenmiş yüz bölgesini orijinal resme yerleştir
            self.islenmis_resim[yeni_y:yeni_y+yeni_h, yeni_x:yeni_x+yeni_w] = bulanik_yuz
        
        # İşlenmiş resmi göster
        self.resim_goster(self.islenmis_resim)
        
        # Kullanıcıya bilgi ver
        if len(yuzler) == 0:
            messagebox.showinfo("Bilgi", "Resimde yüz tespit edilemedi!")
        else:
            messagebox.showinfo("Bilgi", f"{len(yuzler)} adet yüz tespit edildi ve anonimleştirildi!")

    def resmi_kaydet(self):
        if self.islenmis_resim is None:
            messagebox.showwarning("Uyarı", "Kaydedilecek işlenmiş resim bulunamadı!")
            return
            
        dosya_yolu = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Tüm Dosyalar", "*.*")])
        
        if dosya_yolu:
            cv2.imwrite(dosya_yolu, self.islenmis_resim)
            messagebox.showinfo("Başarılı", "Resim başarıyla kaydedildi!")

if __name__ == "__main__":
    root = tk.Tk()
    app = YuzAnonimlestirme(root)
    root.mainloop()
