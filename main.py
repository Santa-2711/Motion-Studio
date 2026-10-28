import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import math, os, threading

APP_NAME = 'Motion Studio'
GREEN = '#00e879'
BG = '#080d12'
PANEL = '#101a22'
CARD = '#15232d'
TEXT = '#e8f1f7'
MUTED = '#8fa6b5'

class MotionStudio:
    def __init__(self, root):
        self.root = root
        root.title('Motion Studio')
        root.geometry('1280x800')
        root.configure(bg=BG)
        self.layers = []
        self.selected = None
        self.playing = True
        self.t = 0.0
        self.duration = tk.DoubleVar(value=15.0)
        self.speed = tk.IntVar(value=50)
        self.intensity = tk.IntVar(value=50)
        self.motion = tk.StringVar(value='Float (Flotar suavemente)')
        self._build_ui()
        self._tick()

    def _build_ui(self):
        top = tk.Frame(self.root, bg='#0b131a', height=56)
        top.pack(fill='x')
        tk.Label(top, text='🪶', fg=GREEN, bg=top['bg'], font=('Segoe UI', 23)).pack(side='left', padx=(18,5))
        tk.Label(top, text='Motion ', fg=TEXT, bg=top['bg'], font=('Segoe UI', 19, 'bold')).pack(side='left')
        tk.Label(top, text='Studio', fg=GREEN, bg=top['bg'], font=('Segoe UI', 19, 'bold')).pack(side='left')
        tk.Label(top, text='●  Modo Offline', fg=GREEN, bg=top['bg'], font=('Segoe UI', 10)).pack(side='right', padx=18)
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill='both', expand=True, padx=10, pady=10)
        left = tk.Frame(body, bg=PANEL, width=260)
        left.pack(side='left', fill='y', padx=(0,8)); left.pack_propagate(False)
        tk.Label(left, text='HERRAMIENTAS', bg=PANEL, fg=GREEN, font=('Segoe UI', 11, 'bold')).pack(anchor='w', padx=14, pady=12)
        self._btn(left, '＋  Importar flyer / capa', self.import_layer)
        self._btn(left, '✥  Movimiento Float', self.apply_float)
        self._btn(left, '▶  Reproducir / Pausar', self.toggle_play)
        self._btn(left, '↺  Reiniciar vista previa', self.reset_preview)
        tk.Label(left, text='CAPAS', bg=PANEL, fg=GREEN, font=('Segoe UI', 11, 'bold')).pack(anchor='w', padx=14, pady=(20,8))
        self.layer_list = tk.Listbox(left, bg=CARD, fg=TEXT, selectbackground='#006d43', relief='flat', font=('Segoe UI', 10), height=12)
        self.layer_list.pack(fill='both', expand=True, padx=12, pady=(0,10))
        self.layer_list.bind('<<ListboxSelect>>', self.select_layer)
        self._btn(left, '−  Eliminar capa seleccionada', self.remove_layer)

        center = tk.Frame(body, bg=PANEL)
        center.pack(side='left', fill='both', expand=True, padx=(0,8))
        bar = tk.Frame(center, bg=PANEL); bar.pack(fill='x')
        tk.Label(bar, text='VISTA PREVIA', bg=PANEL, fg=GREEN, font=('Segoe UI', 11, 'bold')).pack(side='left', padx=14, pady=12)
        self.preview = tk.Canvas(center, bg='#020406', highlightthickness=1, highlightbackground='#20313d')
        self.preview.pack(fill='both', expand=True, padx=10, pady=10)
        self.preview.bind('<Configure>', lambda e: self.draw_preview())
        self.time_label = tk.Label(center, text='00:00 / 00:15', bg=PANEL, fg=TEXT, font=('Segoe UI', 10))
        self.time_label.pack(pady=(0,10))

        right = tk.Frame(body, bg=PANEL, width=285)
        right.pack(side='right', fill='y'); right.pack_propagate(False)
        tk.Label(right, text='PROPIEDADES', bg=PANEL, fg=GREEN, font=('Segoe UI', 11, 'bold')).pack(anchor='w', padx=14, pady=12)
        tk.Label(right, text='Animación', bg=PANEL, fg=TEXT, font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=14, pady=(8,4))
        ttk.Combobox(right, textvariable=self.motion, values=['Float (Flotar suavemente)'], state='readonly').pack(fill='x', padx=14)
        self._scale(right, 'Velocidad', self.speed)
        self._scale(right, 'Intensidad', self.intensity)
        tk.Label(right, text='Duración (segundos)', bg=PANEL, fg=TEXT).pack(anchor='w', padx=14, pady=(12,2))
        tk.Spinbox(right, from_=1, to=60, textvariable=self.duration, bg=CARD, fg=TEXT, insertbackground=TEXT, relief='flat').pack(fill='x', padx=14)
        tk.Label(right, text='Exportación', bg=PANEL, fg=GREEN, font=('Segoe UI', 11, 'bold')).pack(anchor='w', padx=14, pady=(25,8))
        tk.Label(right, text='Formato: MP4 · 1080 × 1920', bg=PANEL, fg=TEXT).pack(anchor='w', padx=14, pady=4)
        tk.Label(right, text='Calidad: Alta', bg=PANEL, fg=TEXT).pack(anchor='w', padx=14, pady=4)
        self.export_btn = tk.Button(right, text='⇧  Exportar video MP4', command=self.export_video, bg=GREEN, fg='#04130b', activebackground='#5affad', relief='flat', font=('Segoe UI', 10, 'bold'), pady=10)
        self.export_btn.pack(fill='x', padx=14, pady=14)
        self.status = tk.Label(self.root, text='Listo · Importa una imagen PNG o JPG para comenzar', bg='#0b131a', fg=MUTED, anchor='w', padx=14)
        self.status.pack(fill='x', side='bottom')

    def _btn(self, parent, text, command):
        tk.Button(parent, text=text, command=command, bg=CARD, fg=TEXT, activebackground='#1d3b2e', activeforeground=GREEN, relief='flat', anchor='w', padx=12, pady=9).pack(fill='x', padx=12, pady=3)

    def _scale(self, parent, label, var):
        tk.Label(parent, text=label, bg=PANEL, fg=TEXT).pack(anchor='w', padx=14, pady=(12,0))
        tk.Scale(parent, from_=0, to=100, orient='horizontal', variable=var, bg=PANEL, fg=GREEN, troughcolor='#263743', highlightthickness=0, activebackground=GREEN).pack(fill='x', padx=12)

    def import_layer(self):
        path = filedialog.askopenfilename(title='Importar flyer o elemento', filetypes=[('Imágenes', '*.png *.jpg *.jpeg *.webp'), ('Todos los archivos', '*.*')])
        if not path: return
        try:
            img = Image.open(path).convert('RGBA')
            layer = {'name': os.path.basename(path), 'path': path, 'image': img, 'x': 0.0, 'y': 0.0, 'float': True, 'photo': None}
            self.layers.append(layer)
            self.layer_list.insert('end', layer['name'])
            self.layer_list.selection_clear(0, 'end'); self.layer_list.selection_set('end')
            self.selected = len(self.layers)-1
            self.status.config(text=f'Importado: {layer["name"]} · Puedes agregar elementos PNG transparentes como capas separadas')
            self.draw_preview()
        except Exception as e:
            messagebox.showerror('Motion Studio', f'No se pudo abrir la imagen:\n{e}')

    def select_layer(self, _event=None):
        sel = self.layer_list.curselection()
        if sel: self.selected = sel[0]

    def remove_layer(self):
        sel = self.layer_list.curselection()
        if not sel: return
        idx = sel[0]
        self.layers.pop(idx); self.layer_list.delete(idx); self.selected = None; self.draw_preview()

    def apply_float(self):
        if not self.layers:
            messagebox.showinfo('Motion Studio', 'Primero importa un flyer o una capa PNG.')
            return
        for layer in self.layers: layer['float'] = True
        self.status.config(text='Float aplicado · Movimiento suave vertical independiente por capa')

    def toggle_play(self): self.playing = not self.playing
    def reset_preview(self): self.t = 0; self.draw_preview()

    def _render_frame(self, width=540, height=960, t=None):
        t = self.t if t is None else t
        frame = Image.new('RGBA', (width, height), (3, 6, 9, 255))
        for i, layer in enumerate(self.layers):
            img = layer['image'].copy()
            scale = min(width/img.width, height/img.height)
            size = (max(1,int(img.width*scale)), max(1,int(img.height*scale)))
            img = img.resize(size, Image.Resampling.LANCZOS)
            x = (width-size[0])//2 + int(layer['x'])
            offset = math.sin(t * (0.7 + self.speed.get()/100) + i*0.7) * (self.intensity.get()/100) * 28 if layer.get('float') else 0
            y = (height-size[1])//2 + int(layer['y'] + offset)
            frame.alpha_composite(img, (x,y))
        return frame.convert('RGB')

    def draw_preview(self):
        if not hasattr(self, 'preview'): return
        w = max(1,self.preview.winfo_width()); h = max(1,self.preview.winfo_height())
        if not self.layers:
            self.preview.delete('all'); self.preview.create_text(w//2,h//2, text='Importa tu flyer para comenzar', fill='#8fa6b5', font=('Segoe UI', 15)); return
        frame = self._render_frame(min(w,700), min(h,900))
        frame.thumbnail((w-20,h-20), Image.Resampling.LANCZOS)
        self._preview_photo = ImageTk.PhotoImage(frame)
        self.preview.delete('all'); self.preview.create_image(w//2,h//2,image=self._preview_photo)

    def _tick(self):
        if self.playing:
            self.t += 1/30
            dur = max(1,float(self.duration.get()))
            if self.t >= dur: self.t = 0
            self.time_label.config(text=f'{int(self.t//60):02d}:{int(self.t%60):02d} / {int(dur//60):02d}:{int(dur%60):02d}')
            self.draw_preview()
        self.root.after(33, self._tick)

    def export_video(self):
        if not self.layers:
            messagebox.showinfo('Motion Studio', 'Importa primero un flyer o una capa.')
            return
        path = filedialog.asksaveasfilename(title='Exportar video', defaultextension='.mp4', filetypes=[('Video MP4','*.mp4')], initialfile='MotionStudio.mp4')
        if not path: return
        self.export_btn.config(state='disabled', text='Exportando…')
        self.status.config(text='Exportando video, espera…')
        threading.Thread(target=self._export_worker, args=(path,), daemon=True).start()

    def _export_worker(self, path):
        try:
            import imageio.v2 as imageio
            dur = max(1,float(self.duration.get()))
            fps = 30
            writer = imageio.get_writer(path, fps=fps, codec='libx264', quality=8, macro_block_size=1, ffmpeg_params=['-pix_fmt','yuv420p'])
            try:
                for n in range(int(dur*fps)):
                    frame = self._render_frame(1080,1920,n/fps)
                    writer.append_data(frame)
            finally: writer.close()
            self.root.after(0, lambda: self._export_done(path))
        except Exception as e:
            self.root.after(0, lambda: self._export_error(str(e)))

    def _export_done(self, path):
        self.export_btn.config(state='normal', text='⇧  Exportar video MP4')
        self.status.config(text=f'Exportación completada: {path}')
        messagebox.showinfo('Motion Studio', f'Video exportado correctamente:\n{path}')

    def _export_error(self, err):
        self.export_btn.config(state='normal', text='⇧  Exportar video MP4')
        self.status.config(text='Error al exportar')
        messagebox.showerror('Motion Studio', 'No se pudo exportar el video.\n'+err)

if __name__ == '__main__':
    root = tk.Tk()
    try: ttk.Style().theme_use('clam')
    except Exception: pass
    MotionStudio(root)
    root.mainloop()
