from tkinter import *
from tkinter import ttk, messagebox, filedialog
from threading import Thread
from os import path
import youtube_dl

class MyLogger(object):
    def debug(self,msg):
        pass
    def warning(self,msg):
        pass
    def error(self,msg):
        messagebox.showerror("Error en la descarga", msg)

def downloadThread(ydl_opts,uri):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([uri])

def rClicker(e):
    try:
        def rClick_Paste(e):
            e.widget.event_generate('<Control-v>')
        e.widget.focus()
        rmenu = Menu(None, tearoff=0, takefocus=0)
        rmenu.add_command(label="Pegar", command=lambda e=e: rClick_Paste(e))
        rmenu.tk_popup(e.x_root+40, e.y_root+10, entry="0")
    except TclError:
        pass

def getLocalization(language):
    if language == "spanish":
        return {
            "language_spanish": "Español",
            "language_english": "Inglés",
            "language_menu": "Idioma",
            "maintenance_menu": "Mantenimiento",
            "maintenance_update": "Buscar actualizaciones",
            "maintenance_about": "Sobre el programa...",
            "about_msg": "Interfaz de usuario para la extracción de audio de youtube basada en youtube-dl. \nÚltima versión: v1.3, 18/09/2020 @ TempledUX \nRepositorio oficial: repo",
            "video_url_label": "Url del video",
            "full_playlists_label": "Descargar listas de reproducción completas",
            "audio_extraction_button": "Extraer audio",
            "messagebox_completed_title": "Extracción de audio",
            "messagebox_completed_desc": "Descarga completada",
            "messagebox_progresswarning_title": "Advertencia",
            "messagebox_progresswarning_desc": "No se pudo leer el progreso en bytes de la transferencia. La descarga continuará, pero sin información de estado. Pulsa aceptar para continuar.",
            "messagebox_inputerror_title": "Error en los datos",
            "messagebox_error_nourl": "Introduce una url de video antes de comenzar la descarga.",
            "messagebox_error_outputdir": "No se ha seleccionado ningún directorio de salida.",
            "filedialog_outdir_title": "Seleccionar directorio de salida"
        }
    elif language == "english":
        return {
            "language_spanish": "Spanish",
            "language_english": "English",
            "language_menu": "Language",
            "maintenance_menu": "Maintenance",
            "maintenance_update": "Search for updates",
            "maintenance_about": "About...",
            "about_msg": "Youtube audio extractor GUI based in youtube-dl. \nLastest version: v1.3, 18/09/2020 @ TempledUX \nOfficial repository: repo",
            "video_url_label": "Video Url",
            "full_playlists_label": "Download full playlists",
            "audio_extraction_button": "Extract audio",
            "messagebox_completed_title": "Audio extraction",
            "messagebox_completed_desc": "Download completed",
            "messagebox_progresswarning_title": "Warning",
            "messagebox_progresswarning_desc": "Error while reading byte progress of the transference. Download will continue, but without state information. Press ok to continue.",
            "messagebox_inputerror_title": "Input error",
            "messagebox_error_nourl": "Input a video url before starting the download.",
            "messagebox_error_outputdir": "No output directory was selected.",
            "filedialog_outdir_title": "Select an output directory"
        }

def initLocalization() -> str:
    try:
        if not (path.exists('youtubeGUI_settings.txt')):
            infile = open('youtubeGUI_settings.txt','w')
            infile.write('localization=english')
            infile.close()
            raise Exception
        infile = open('youtubeGUI_settings.txt','r')
        data = infile.read()
        idx = data.find('=')
        locsetting = data[idx+1:]
    except Exception:
        return 'spanish'
    return locsetting

def saveLocalization(locsetting: str, app):
    try:
        outfile = open('youtubeGUI_settings.txt','w')
        outfile.write(f"localization={locsetting}")
        outfile.close()
    except Exception:
        return 'error'
    app.destroy()
    Aplicacion()


class Aplicacion():
    def __init__(self):
        self.localization = getLocalization(initLocalization())

        self.principal = Tk()
        self.principal.resizable(False,False)
        self.principal.title("Youtube mp3 extractor - v1.3")
        self.principal.geometry("450x170")
        #Icon from Flaticon.com - Pixel perfect
        self.principal.iconbitmap('yt.ico')

        self.progressOk = True

        #Menu bar
        menubar = Menu(self.principal)
        configmenu = Menu(menubar, tearoff=0)
        configmenu.add_command(label=self.localization['maintenance_update'], command=self.check_update)
        configmenu.add_command(label=self.localization['maintenance_about'], command=self.about)
        menubar.add_cascade(label=self.localization['maintenance_menu'], menu=configmenu)
        languagemenu = Menu(menubar, tearoff=0)
        languagemenu.add_command(label=self.localization['language_spanish'], command=lambda s="spanish", app=self.principal:saveLocalization(s,app))
        languagemenu.add_command(label=self.localization['language_english'], command=lambda s="english", app=self.principal:saveLocalization(s,app))
        menubar.add_cascade(label=self.localization['language_menu'], menu=languagemenu)
        self.principal.config(menu=menubar)

        self.uripanel = ttk.Frame(self.principal)
        self.urilabel = ttk.Label(self.uripanel, text=self.localization['video_url_label'])
        self.uriedit = ttk.Entry(self.uripanel, width=40)
        self.uriclear = ttk.Button(self.uripanel, text="X", width=5, command=lambda self=self: self.uriedit.delete('0','end'))
        self.uriedit.bind('<Button-3>', rClicker, add='')
        self.checkboxlistvar = BooleanVar(self.principal)
        self.checkboxlistvar.set(False)
        self.checkboxlist = ttk.Checkbutton(self.principal, text=self.localization['full_playlists_label'], variable=self.checkboxlistvar)

        self.pbar = ttk.Progressbar(self.principal)
        self.downloadBtn = ttk.Button(self.principal, text=self.localization['audio_extraction_button'], command=self.startDownload)

        self.uripanel.pack(side=TOP,fill=BOTH,expand=True,padx=5,pady=(5,0))
        self.urilabel.pack(side=LEFT,fill=None,expand=True,padx=0,pady=0)
        self.uriedit.pack(side=LEFT,fill=X,expand=True,padx=0,pady=0)
        self.uriclear.pack(side=LEFT,fill=None,expand=False,padx=(5,15),pady=0)
        self.checkboxlist.pack(side=TOP,fill=X,expand=True,padx=(18,5),pady=0,anchor='w')
        self.pbar.pack(side=TOP,fill=X,expand=True,padx=20,pady=0)
        self.downloadBtn.pack(side=TOP,fill=Y,expand=True,padx=5,pady=(0,10),ipadx=20)

        self.principal.mainloop()

    def hook(self,d):
        if d['status'] == 'finished':
            if not self.progressOk:
                self.pbar.stop()
                self.pbar.config(mode="determinate")
                self.principal.update()
            messagebox.showinfo(self.localization['messagebox_completed_title'], self.localization['messagebox_completed_desc'])
            self.pbar.config(value=0)
            self.principal.update()
            self.downloadBtn.config(state=NORMAL)
            self.progressOk = True
        elif d['status'] == 'downloading':
            if self.progressOk:
                try:
                    dwnl_progress = (d['downloaded_bytes']/d['total_bytes'])*100
                    self.pbar.config(value=dwnl_progress)
                except KeyError:
                    messagebox.showwarning(self.localization['messagebox_progresswarning_title'],self.localization['messagebox_progresswarning_desc'])
                    self.pbar.config(mode="indeterminate")
                    self.pbar.start()
                    self.progressOk = False
            self.principal.update()

    def startDownload(self):
        if (self.uriedit.get() == ""):
            messagebox.showerror(self.localization['messagebox_inputerror_title'], self.localization['messagebox_error_nourl'])
            return
        outfolder = filedialog.askdirectory(title=self.localization['filedialog_outdir_title']) + '/'
        if (outfolder == '/'):
            messagebox.showerror(self.localization['messagebox_inputerror_title'], self.localization['messagebox_error_outputdir'])
            return
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': outfolder + '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }],
            'logger': MyLogger(),
            'progress_hooks': [self.hook],
            'noplaylist': not self.checkboxlistvar.get()
        }
        self.downloadBtn.config(state=DISABLED)
        self.principal.update()
        Thread(target=downloadThread, args=[ydl_opts, self.uriedit.get()]).run()

    def check_update(self):
        pass

    def about(self):
        messagebox.showinfo(self.localization['maintenance_about'], self.localization['about_msg'])
        
Aplicacion()
