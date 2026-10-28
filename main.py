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
PRESETS = {'Original del flyer': None, 'Story / Reels 9:16': (1080,1920), 'Instagram 4:5': (1080,1350), 'Cuadrado 1:1': (1080,1080), 'Horizontal 16:9': (1920,1080), 'Full HD 9:16': (1080,1920), '4K 9:16': (2160,3840)}

class MotionStudio:
    def __init__(self, root):
        self.root=root; root.title('Motion Studio'); root.geometry('1360x900'); root.minsize(1050,720); root.configure(bg=BG)
        self.layers=[]; self.selected=None; self.playing=True; self.t=0.0
        self.duration=tk.DoubleVar(value=15.0); self.speed=tk.IntVar(value=50); self.intensity=tk.IntVar(value=50)
        self.motion=tk.StringVar(value='Float / Flotar'); self.preset=tk.StringVar(value='Original del flyer')
        self.project_w=1080; self.project_h=1920; self.fps=tk.IntVar(value=30)
        self._build_ui(); self._tick()

    def _build_ui(self):
        top=tk.Frame(self.root,bg='#0b131a',height=56); top.pack(fill='x')
        tk.Label(top,text='🪶',fg=GREEN,bg=top['bg'],font=('Segoe UI',23)).pack(side='left',padx=(18,5))
        tk.Label(top,text='Motion ',fg=TEXT,bg=top['bg'],font=('Segoe UI',19,'bold')).pack(side='left')
        tk.Label(top,text='Studio',fg=GREEN,bg=top['bg'],font=('Segoe UI',19,'bold')).pack(side='left')
        tk.Label(top,text='●  Modo Offline',fg=GREEN,bg=top['bg'],font=('Segoe UI',10)).pack(side='right',padx=18)
        body=tk.Frame(self.root,bg=BG); body.pack(fill='both',expand=True,padx=10,pady=10)
        left=tk.Frame(body,bg=PANEL,width=245); left.pack(side='left',fill='y',padx=(0,8)); left.pack_propagate(False)
        self._heading(left,'HERRAMIENTAS')
        self._btn(left,'＋  Importar flyer / capa',self.import_layer)
        self._btn(left,'＋  Importar elemento PNG',self.import_layer)
        self._btn(left,'▶  Reproducir / Pausar',self.toggle_play)
        self._btn(left,'↺  Reiniciar vista previa',self.reset_preview)
        self._heading(left,'CAPAS')
        self.layer_list=tk.Listbox(left,bg=CARD,fg=TEXT,selectbackground='#006d43',relief='flat',font=('Segoe UI',10),height=10)
        self.layer_list.pack(fill='both',expand=True,padx=12,pady=(0,8)); self.layer_list.bind('<<ListboxSelect>>',self.select_layer)
        self._btn(left,'−  Eliminar capa',self.remove_layer)
        self._heading(left,'TAMAÑO DEL PROYECTO')
        self.preset_box=ttk.Combobox(left,textvariable=self.preset,values=list(PRESETS),state='readonly'); self.preset_box.pack(fill='x',padx=12,pady=4); self.preset_box.bind('<<ComboboxSelected>>',self.change_preset)
        self.size_label=tk.Label(left,text='1080 × 1920',bg=PANEL,fg=TEXT); self.size_label.pack(anchor='w',padx=12)
        self._btn(left,'↔  Tamaño personalizado',self.custom_size)
        center=tk.Frame(body,bg=PANEL); center.pack(side='left',fill='both',expand=True,padx=(0,8))
        bar=tk.Frame(center,bg=PANEL); bar.pack(fill='x')
        tk.Label(bar,text='VISTA PREVIA',bg=PANEL,fg=GREEN,font=('Segoe UI',11,'bold')).pack(side='left',padx=14,pady=12)
        self.preview=tk.Canvas(center,bg='#020406',highlightthickness=1,highlightbackground='#20313d'); self.preview.pack(fill='both',expand=True,padx=10,pady=10)
        self.preview.bind('<Configure>',lambda e:self.draw_preview())
        self.time_label=tk.Label(center,text='00:00 / 00:15',bg=PANEL,fg=TEXT,font=('Segoe UI',10)); self.time_label.pack(pady=(0,6))
        self.seek=tk.Scale(center,from_=0,to=15,resolution=.05,orient='horizontal',variable=tk.DoubleVar(value=0),command=self.seek_time,bg=PANEL,fg=GREEN,troughcolor='#263743',highlightthickness=0,showvalue=False); self.seek.pack(fill='x',padx=15,pady=(0,8))
        right=tk.Frame(body,bg=PANEL,width=270); right.pack(side='right',fill='y'); right.pack_propagate(False)
        self._heading(right,'PROPIEDADES')
        tk.Label(right,text='Efecto de movimiento',bg=PANEL,fg=TEXT,font=('Segoe UI',10,'bold')).pack(anchor='w',padx=14,pady=(8,4))
        self.motion_box=ttk.Combobox(right,textvariable=self.motion,values=['Ninguno','Float / Flotar','Zoom in','Zoom out','Deslizar desde izquierda','Deslizar desde derecha','Rebote','Rotación','Fade in/out','Shake / Temblor','Parallax'],state='readonly')
        self.motion_box.pack(fill='x',padx=14); self.motion_box.bind('<<ComboboxSelected>>',lambda e:self.apply_settings())
        self._scale(right,'Velocidad',self.speed); self._scale(right,'Intensidad',self.intensity)
        tk.Label(right,text='Duración (segundos)',bg=PANEL,fg=TEXT).pack(anchor='w',padx=14,pady=(12,2))
        tk.Spinbox(right,from_=1,to=120,textvariable=self.duration,bg=CARD,fg=TEXT,insertbackground=TEXT,relief='flat',command=self.duration_changed).pack(fill='x',padx=14)
        self._heading(right,'TRANSICIÓN')
        self.transition=tk.StringVar(value='Fade')
        ttk.Combobox(right,textvariable=self.transition,values=['Ninguna','Fade','Zoom','Slide izquierda','Slide derecha','Glitch (simulado)'],state='readonly').pack(fill='x',padx=14)
        tk.Label(right,text='Aplicar a la capa seleccionada',bg=PANEL,fg=MUTED,font=('Segoe UI',9)).pack(anchor='w',padx=14,pady=3)
        self._btn(right,'✦  Aplicar transición',self.apply_transition)
        self._heading(right,'EXPORTACIÓN')
        self.export_info=tk.Label(right,text='MP4 · 1080 × 1920 · 30 FPS',bg=PANEL,fg=TEXT); self.export_info.pack(anchor='w',padx=14,pady=4)
        self._btn(right,'⚙  Ajustes de exportación',self.export_settings)
        self.export_btn=tk.Button(right,text='⇧  Exportar video MP4',command=self.export_video,bg=GREEN,fg='#04130b',activebackground='#5affad',relief='flat',font=('Segoe UI',10,'bold'),pady=10); self.export_btn.pack(fill='x',padx=14,pady=14)
        self._heading(self.root,'LÍNEA DE TIEMPO')
        self.timeline=tk.Frame(self.root,bg='#0b131a',height=120); self.timeline.pack(fill='x',side='bottom'); self.timeline.pack_propagate(False)
        self.timeline_canvas=tk.Canvas(self.timeline,bg='#0b131a',height=90,highlightthickness=0); self.timeline_canvas.pack(fill='both',expand=True,padx=12,pady=4)
        self.timeline_canvas.bind('<Configure>',lambda e:self.draw_timeline())
        self.status=tk.Label(self.root,text='Listo · Importa un flyer para comenzar',bg='#0b131a',fg=MUTED,anchor='w',padx=14); self.status.pack(fill='x',side='bottom')

    def _heading(self,parent,text):
        tk.Label(parent,text=text,bg=PANEL,fg=GREEN,font=('Segoe UI',10,'bold')).pack(anchor='w',padx=14,pady=(13,7))
    def _btn(self,parent,text,command):
        tk.Button(parent,text=text,command=command,bg=CARD,fg=TEXT,activebackground='#1d3b2e',activeforeground=GREEN,relief='flat',anchor='w',padx=12,pady=8).pack(fill='x',padx=12,pady=3)
    def _scale(self,parent,label,var):
        tk.Label(parent,text=label,bg=PANEL,fg=TEXT).pack(anchor='w',padx=14,pady=(10,0))
        tk.Scale(parent,from_=0,to=100,orient='horizontal',variable=var,bg=PANEL,fg=GREEN,troughcolor='#263743',highlightthickness=0,activebackground=GREEN,command=lambda _v:self.draw_preview()).pack(fill='x',padx=12)

    def import_layer(self):
        path=filedialog.askopenfilename(title='Importar flyer o elemento',filetypes=[('Imágenes','*.png *.jpg *.jpeg *.webp'),('Todos los archivos','*.*')])
        if not path:return
        try:
            img=Image.open(path).convert('RGBA')
            layer={'name':os.path.basename(path),'path':path,'image':img,'x':0.0,'y':0.0,'motion':'Float / Flotar','transition':'Fade','start':0.0,'end':float(self.duration.get()),'photo':None}
            if not self.layers:
                self.project_w,self.project_h=img.size; self.preset.set('Original del flyer'); self.size_label.config(text=f'{self.project_w} × {self.project_h}')
            self.layers.append(layer); self.layer_list.insert('end',layer['name']); self.layer_list.selection_clear(0,'end'); self.layer_list.selection_set('end'); self.selected=len(self.layers)-1
            self.status.config(text=f'Importado: {layer["name"]} · Tamaño original {img.width} × {img.height}'); self.draw_preview(); self.draw_timeline()
        except Exception as e:messagebox.showerror('Motion Studio',f'No se pudo abrir la imagen:\n{e}')

    def select_layer(self,_event=None):
        sel=self.layer_list.curselection()
        if sel:
            self.selected=sel[0]; layer=self.layers[self.selected]; self.motion.set(layer.get('motion','Ninguno')); self.transition.set(layer.get('transition','Fade')); self.draw_timeline()
    def remove_layer(self):
        sel=self.layer_list.curselection()
        if not sel:return
        idx=sel[0]; self.layers.pop(idx); self.layer_list.delete(idx); self.selected=None; self.draw_preview(); self.draw_timeline()
    def apply_settings(self):
        if self.selected is not None and self.selected<len(self.layers): self.layers[self.selected]['motion']=self.motion.get()
        self.draw_preview(); self.draw_timeline()
    def apply_transition(self):
        if self.selected is None:return
        self.layers[self.selected]['transition']=self.transition.get(); self.status.config(text=f'Transición {self.transition.get()} aplicada a {self.layers[self.selected]["name"]}'); self.draw_preview()
    def change_preset(self,_event=None):
        val=PRESETS.get(self.preset.get())
        if val:self.project_w,self.project_h=val
        elif self.layers:self.project_w,self.project_h=self.layers[0]['image'].size
        self.size_label.config(text=f'{self.project_w} × {self.project_h}'); self.export_info.config(text=f'MP4 · {self.project_w} × {self.project_h} · {self.fps.get()} FPS'); self.draw_preview()
    def custom_size(self):
        win=tk.Toplevel(self.root); win.title('Tamaño personalizado'); win.configure(bg=PANEL); win.resizable(False,False)
        tk.Label(win,text='Ancho',bg=PANEL,fg=TEXT).grid(row=0,column=0,padx=12,pady=10); w=tk.Entry(win); w.insert(0,str(self.project_w)); w.grid(row=0,column=1,padx=12)
        tk.Label(win,text='Alto',bg=PANEL,fg=TEXT).grid(row=1,column=0,padx=12,pady=10); h=tk.Entry(win); h.insert(0,str(self.project_h)); h.grid(row=1,column=1,padx=12)
        def save():
            try:
                ww,hh=int(w.get()),int(h.get())
                if not(64<=ww<=7680 and 64<=hh<=7680):raise ValueError()
                self.project_w,self.project_h=ww,hh; self.preset.set('Original del flyer'); self.size_label.config(text=f'{ww} × {hh}'); self.export_info.config(text=f'MP4 · {ww} × {hh} · {self.fps.get()} FPS'); self.draw_preview(); win.destroy()
            except:messagebox.showerror('Motion Studio','Ingresa valores entre 64 y 7680.')
        tk.Button(win,text='Aplicar',command=save,bg=GREEN,fg=BG).grid(row=2,column=0,columnspan=2,pady=12)
    def duration_changed(self):
        for layer in self.layers:layer['end']=min(layer.get('end',self.duration.get()),float(self.duration.get()))
        self.seek.configure(to=max(0,float(self.duration.get()))); self.draw_timeline()
    def seek_time(self,value):
        try:self.t=float(value); self.draw_preview(); self.draw_timeline()
        except:pass
    def toggle_play(self):self.playing=not self.playing
    def reset_preview(self):self.t=0; self.seek.set(0); self.draw_preview(); self.draw_timeline()

    def _render_frame(self,width=None,height=None,t=None):
        width=width or self.project_w; height=height or self.project_h; t=self.t if t is None else t
        frame=Image.new('RGBA',(width,height),(3,6,9,255))
        for i,layer in enumerate(self.layers):
            img=layer['image'].copy(); base_scale=min(width/img.width,height/img.height)
            img=img.resize((max(1,int(img.width*base_scale)),max(1,int(img.height*base_scale))),Image.Resampling.LANCZOS)
            motion=layer.get('motion','Ninguno'); p=max(0,min(1,t/max(0.01,float(self.duration.get())))); sp=.5+self.speed.get()/50; amp=self.intensity.get()/100
            dx=dy=0; scale=1; angle=0; alpha=255
            if motion in ('Float / Flotar','Parallax'):dy=math.sin(t*sp+i*.7)*amp*height*.018
            elif motion=='Zoom in':scale=1+p*amp*.35
            elif motion=='Zoom out':scale=1.35-p*amp*.35
            elif motion=='Deslizar desde izquierda':dx=-(1-p)*width*.65
            elif motion=='Deslizar desde derecha':dx=(1-p)*width*.65
            elif motion=='Rebote':dy=abs(math.sin(t*sp*2))*amp*height*.04
            elif motion=='Rotación':angle=math.sin(t*sp)*amp*8
            elif motion=='Shake / Temblor':dx=math.sin(t*sp*16)*amp*width*.008; dy=math.cos(t*sp*13)*amp*height*.008
            if motion=='Fade in/out':
                alpha=int(255*min(1,p*5,(1-p)*5))
            if layer.get('transition')=='Fade':
                alpha=min(alpha,int(255*min(1,p*5)))
            if scale!=1 or angle:img=img.resize((max(1,int(img.width*scale)),max(1,int(img.height*scale))),Image.Resampling.LANCZOS).rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
            if alpha<255:img.putalpha(img.getchannel('A').point(lambda a:int(a*alpha/255)))
            x=(width-img.width)//2+int(layer['x']+dx); y=(height-img.height)//2+int(layer['y']+dy)
            frame.alpha_composite(img,(x,y))
        return frame.convert('RGB')

    def draw_preview(self):
        if not hasattr(self,'preview'):return
        w=max(1,self.preview.winfo_width()); h=max(1,self.preview.winfo_height())
        if not self.layers:
            self.preview.delete('all'); self.preview.create_text(w//2,h//2,text='Importa tu flyer para comenzar',fill=MUTED,font=('Segoe UI',15)); return
        frame=self._render_frame(min(w,850),min(h,1100)); frame.thumbnail((w-20,h-20),Image.Resampling.LANCZOS)
        self._preview_photo=ImageTk.PhotoImage(frame); self.preview.delete('all'); self.preview.create_image(w//2,h//2,image=self._preview_photo)
    def draw_timeline(self):
        if not hasattr(self,'timeline_canvas'):return
        c=self.timeline_canvas; c.delete('all'); w=max(1,c.winfo_width()); h=max(1,c.winfo_height()); dur=max(1,float(self.duration.get()))
        c.create_text(10,8,text='CAPAS / TIEMPO',fill=GREEN,anchor='nw',font=('Segoe UI',9,'bold'))
        left=150; right=w-12; usable=max(1,right-left)
        for sec in range(int(dur)+1):
            x=left+usable*sec/dur; c.create_line(x,22,x,h,fill='#243743'); c.create_text(x,18,text=str(sec),fill=MUTED,font=('Segoe UI',8))
        for i,layer in enumerate(self.layers):
            y=38+i*18
            if y>h:break
            c.create_text(8,y,text=layer['name'][:20],fill=GREEN if i==self.selected else TEXT,anchor='w',font=('Segoe UI',8))
            start=max(0,layer.get('start',0)); end=min(dur,layer.get('end',dur)); x1=left+usable*start/dur; x2=left+usable*end/dur
            c.create_rectangle(x1,y-5,max(x1+3,x2),y+5,fill='#006d43' if i==self.selected else '#2b5368',outline='')
        px=left+usable*min(1,self.t/dur); c.create_line(px,22,px,h,fill='#ffdf6b',width=2)
    def _tick(self):
        if self.playing:
            self.t+=1/max(1,self.fps.get()); dur=max(1,float(self.duration.get()))
            if self.t>=dur:self.t=0
            self.seek.set(self.t); self.time_label.config(text=f'{self.t:05.2f} / {dur:05.2f} s'); self.draw_preview(); self.draw_timeline()
        self.root.after(int(1000/max(1,self.fps.get())),self._tick)
    def export_settings(self):
        win=tk.Toplevel(self.root); win.title('Exportación'); win.configure(bg=PANEL); win.resizable(False,False)
        tk.Label(win,text='FPS',bg=PANEL,fg=TEXT).grid(row=0,column=0,padx=12,pady=12); fps=ttk.Combobox(win,values=[24,25,30,50,60],state='readonly'); fps.set(self.fps.get()); fps.grid(row=0,column=1,padx=12)
        tk.Label(win,text='Resolución del proyecto',bg=PANEL,fg=TEXT).grid(row=1,column=0,padx=12,pady=12); tk.Label(win,text=f'{self.project_w} × {self.project_h}',bg=PANEL,fg=GREEN).grid(row=1,column=1,padx=12)
        def save():self.fps.set(int(fps.get())); self.export_info.config(text=f'MP4 · {self.project_w} × {self.project_h} · {self.fps.get()} FPS'); win.destroy()
        tk.Button(win,text='Guardar',command=save,bg=GREEN,fg=BG).grid(row=2,column=0,columnspan=2,pady=12)
    def export_video(self):
        if not self.layers:messagebox.showinfo('Motion Studio','Importa primero un flyer o una capa.'); return
        path=filedialog.asksaveasfilename(title='Exportar video',defaultextension='.mp4',filetypes=[('Video MP4','*.mp4')],initialfile='MotionStudio.mp4')
        if not path:return
        self.export_btn.config(state='disabled',text='Exportando…'); self.status.config(text='Exportando video, espera…')
        threading.Thread(target=self._export_worker,args=(path,),daemon=True).start()
    def _export_worker(self,path):
        try:
            import imageio.v2 as imageio
            dur=max(1,float(self.duration.get())); fps=max(1,int(self.fps.get()))
            writer=imageio.get_writer(path,fps=fps,codec='libx264',quality=8,macro_block_size=1,ffmpeg_params=['-pix_fmt','yuv420p'])
            try:
                for n in range(int(dur*fps)):writer.append_data(self._render_frame(self.project_w,self.project_h,n/fps))
            finally:writer.close()
            self.root.after(0,lambda:self._export_done(path))
        except Exception as e:self.root.after(0,lambda:self._export_error(str(e)))
    def _export_done(self,path):
        self.export_btn.config(state='normal',text='⇧  Exportar video MP4'); self.status.config(text=f'Exportación completada: {path}'); messagebox.showinfo('Motion Studio',f'Video exportado correctamente:\n{path}')
    def _export_error(self,err):
        self.export_btn.config(state='normal',text='⇧  Exportar video MP4'); self.status.config(text='Error al exportar'); messagebox.showerror('Motion Studio','No se pudo exportar el video.\n'+err)

if __name__=='__main__':
    root=tk.Tk()
    try:ttk.Style().theme_use('clam')
    except Exception:pass
    MotionStudio(root); root.mainloop()
