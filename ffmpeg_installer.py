import os
import shutil
import winreg
import subprocess
import sys
from pathlib import Path
import ctypes
from tkinter import messagebox, Tk, filedialog, ttk, Label, Button
import threading

def is_admin():
    """
    Programın yönetici haklarıyla çalışıp çalışmadığını kontrol eder
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin_rights():
    """
    Programı yönetici haklarıyla yeniden başlatır
    """
    try:
        if not is_admin():
            # Geçerli Python yorumlayıcısının yolunu al
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([script] + sys.argv[1:])
            
            # ShellExecute ile yönetici olarak başlat
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas",
                sys.executable,
                params,
                None, 
                1
            )
            
            # Eğer başarılı olduysa mevcut programı kapat
            if ret > 32:
                sys.exit(0)
            else:
                raise Exception("Yönetici hakları alınamadı!")
    except Exception as e:
        messagebox.showerror(
            "Hata",
            f"Yönetici hakları alınırken hata oluştu:\n{str(e)}\n"
            "Lütfen programı manuel olarak yönetici olarak çalıştırın."
        )
        sys.exit(1)

class FFmpegKurulumGUI:
    def __init__(self):
        # Yönetici hakları kontrolü
        if not is_admin():
            request_admin_rights()
            return
            
        self.window = Tk()
        self.window.title("FFmpeg Kurulum Aracı")
        self.window.geometry("600x400")
        self.window.resizable(False, False)
        
        # Pencereyi ekranın ortasına konumlandır
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 400) // 2
        self.window.geometry(f"600x400+{x}+{y}")
        
        # Stil tanımlama
        style = ttk.Style()
        style.configure('Custom.TButton', padding=10)
        style.configure('Custom.TLabel', padding=10, font=('Helvetica', 10))
        
        # Ana frame
        self.main_frame = ttk.Frame(self.window, padding="20")
        self.main_frame.pack(fill='both', expand=True)
        
        # Başlık
        self.title_label = ttk.Label(
            self.main_frame,
            text="FFmpeg Kurulum Aracı",
            style='Custom.TLabel',
            font=('Helvetica', 14, 'bold')
        )
        self.title_label.pack(pady=20)
        
        # Açıklama
        self.info_label = ttk.Label(
            self.main_frame,
            text="Lütfen FFmpeg klasörünü seçin.\nBu klasör 'bin' dizinini içermelidir.",
            style='Custom.TLabel',
            justify='center'
        )
        self.info_label.pack(pady=10)
        
        # Seçilen klasör yolu
        self.path_label = ttk.Label(
            self.main_frame,
            text="Seçilen klasör: Henüz seçim yapılmadı",
            style='Custom.TLabel',
            wraplength=500
        )
        self.path_label.pack(pady=10)
        
        # Klasör seçme butonu
        self.select_button = ttk.Button(
            self.main_frame,
            text="FFmpeg Klasörünü Seç",
            command=self.select_folder,
            style='Custom.TButton'
        )
        self.select_button.pack(pady=10)
        
        # Kurulum butonu
        self.install_button = ttk.Button(
            self.main_frame,
            text="Kurulumu Başlat",
            command=self.start_installation,
            style='Custom.TButton',
            state='disabled'
        )
        self.install_button.pack(pady=10)
        
        # İlerleme çubuğu
        self.progress = ttk.Progressbar(
            self.main_frame,
            orient="horizontal",
            length=400,
            mode="indeterminate"
        )
        self.progress.pack(pady=20)
        
        # Durum mesajı
        self.status_label = ttk.Label(
            self.main_frame,
            text="",
            style='Custom.TLabel',
            wraplength=500
        )
        self.status_label.pack(pady=10)
        
        self.selected_path = None
    
    def select_folder(self):
        """Kullanıcının FFmpeg klasörünü seçmesini sağlar"""
        folder_path = filedialog.askdirectory(
            title="FFmpeg Klasörünü Seçin"
        )
        if folder_path:
            path = Path(folder_path)
            
            # FFmpeg exe dosyalarını ara
            ffmpeg_files = list(path.glob("**/*.exe"))
            
            if ffmpeg_files:
                # FFmpeg exe dosyalarını içeren klasörü bul
                exe_folder = ffmpeg_files[0].parent
                self.selected_path = exe_folder
                self.path_label.config(text=f"Seçilen klasör: {exe_folder}")
                self.install_button.config(state='normal')
                self.status_label.config(text="Klasör geçerli. Kurulumu başlatabilirsiniz.")
            else:
                messagebox.showerror(
                    "Hata",
                    "Seçilen klasörde FFmpeg dosyaları bulunamadı!\n"
                    "Lütfen FFmpeg'in çıkartıldığı klasörü seçin."
                )
    
    def start_installation(self):
        """Kurulum işlemini başlatır"""
        self.progress.start()
        self.install_button.config(state='disabled')
        self.select_button.config(state='disabled')
        self.status_label.config(text="Kurulum başlatılıyor...")
        
        # Kurulumu arka planda çalıştır
        threading.Thread(target=self.install_ffmpeg, daemon=True).start()
    
    def install_ffmpeg(self):
        """FFmpeg kurulum işlemini gerçekleştirir"""
        try:
            target_dir = Path("C:/ffmpeg")
            bin_dir = target_dir / "bin"
            
            # Hedef klasörleri oluştur
            os.makedirs(str(target_dir), exist_ok=True)
            os.makedirs(str(bin_dir), exist_ok=True)
            
            # Dosyaları kopyala
            self.update_status("Dosyalar kopyalanıyor...")
            
            # Mevcut dosyaları temizle
            for file in bin_dir.glob("*"):
                os.remove(str(file))
            
            # Gerekli exe dosyalarını kopyala
            required_files = ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
            files_found = False
            
            for file in self.selected_path.glob("*.exe"):
                if file.name.lower() in required_files:
                    shutil.copy2(str(file), str(bin_dir))
                    files_found = True
                    self.update_status(f"{file.name} kopyalandı...")
            
            if not files_found:
                raise Exception("FFmpeg exe dosyaları bulunamadı!")
            
            # PATH'e ekle
            self.update_status("Sistem PATH değişkeni güncelleniyor...")
            if self.add_to_path(str(bin_dir)):
                self.update_status("PATH güncellendi.")
            
            # Kurulumu test et
            self.update_status("Kurulum test ediliyor...")
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.installation_complete(True, "FFmpeg başarıyla kuruldu!")
            else:
                raise Exception("FFmpeg kurulumu test edilemedi!")
                
        except Exception as e:
            self.installation_complete(False, f"Kurulum hatası: {str(e)}")
    
    def update_status(self, message):
        """Durum mesajını günceller"""
        self.window.after(0, lambda: self.status_label.config(text=message))
    
    def installation_complete(self, success, message):
        """Kurulum tamamlandığında çağrılır"""
        self.window.after(0, lambda: self.progress.stop())
        self.window.after(0, lambda: self.status_label.config(
            text=message,
            foreground="green" if success else "red"
        ))
        
        if success:
            messagebox.showinfo("Başarılı", message)
        else:
            messagebox.showerror("Hata", message)
        
        self.window.after(0, lambda: self.select_button.config(state='normal'))
    
    def add_to_path(self, new_path):
        """Sistem PATH değişkenine yeni yol ekler"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_ALL_ACCESS
            )
            path = winreg.QueryValueEx(key, "Path")[0]
            
            if new_path not in path:
                new_path_value = path + ";" + new_path
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path_value)
            
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"PATH güncelleme hatası: {str(e)}")
            return False

def main():
    """
    Ana program fonksiyonu
    """
    try:
        app = FFmpegKurulumGUI()
        if hasattr(app, 'window'):  # Pencere oluşturulduysa
            app.window.mainloop()
    except Exception as e:
        messagebox.showerror(
            "Hata",
            f"Program başlatılırken hata oluştu:\n{str(e)}"
        )

if __name__ == "__main__":
    main() 