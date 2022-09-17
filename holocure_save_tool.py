VERSION = '0.0.3-Beta'
ABOUT_MSG=f'''HoloCure bad bad Save Tool
Version: {VERSION}
Date: 2022/09/17
Author: Aclich
Require: python > 3.6, tkinter
Source code: https://github.com/aclich/Holocure_save_editor

Change Log:
 - Add vertical scrollbar in editor for fixing toooooo long content 😵

Tested Game version
0.4.1662728581

Known issue:
Not compatible with older version of save file. 
'''


import json, base64, os
import tkinter as tk
from tkinter import CENTER, DISABLED, messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import List, Tuple

LVL_KEYS = [] #['characters', 'tears']
CHK_KEYS = ['specUnlock', 'refund', 'challenge', 'GROff', 'growth']
UNKNOW_KEYS = ['unlockedCharacters', 'eliminate']
NUMB_KEYS = []

LIST_MAP = {'unlockedItems': ['BodyPillow', 'FullMeal', 'PikiPikiPiman', 'SuccubusHorn', 'Headphones', 'UberSheep',
                              'HolyMilk', 'Sake', 'FaceMask', 'CreditCard', 'GorillasPaw', 'InjectionAsacoco',
                              'IdolCostume', 'Plushie', 'StudyGlasses', 'SuperChattoTime', 'EnergyDrink', 'Halu',
                              'Membership', 'GWSPill', 'ChickensFeather', 'Bandaid', 'Limiter', 'PiggyBank'],
            'unlockedWeapons': ['PsychoAxe', 'Glowstick', 'SpiderCooking', 'Tailplug', 'BLBook', 'EliteLava',
                                'HoloBomb', 'HoloLaser', 'CuttingBoard', 'IdolSong', 'CEOTears', 'WamyWater',
                                'XPotato'],
            'seenCollabs': ['BreatheInAsacoco', 'DragonBeam', 'EliteCooking', 'FlatBoard',
                            'MiComet', 'BLLover', 'LightBeam', 'IdolConcert', 'StreamOfTears',
                            'MariLamy', 'BrokenDreams', 'RapDog'],
            'unlockedStages': ['STAGE 1', 'STAGE 2', 'STAGE 1 (HARD)'],
            'unlockedOutfits': ['default', 'ameAlt1', 'kiaraAlt1', 'ameAlt1', 'inaAlt1', 'guraAlt1', 'calliAlt1',
                                'kiaraAlt1', 'irysAlt1', 'baeAlt1', 'sanaAlt1', 'faunaAlt1', 'mumeiAlt1', 'kroniiAlt1',
                                'kurokami']
            }

GEOMETRY='+600+200'
InitPath = os.path.join(os.environ['LOCALAPPDATA'], 'HoloCure')
AskSavePath = lambda init_path=InitPath: askopenfilename(title='select save data',
                                                initialdir=init_path,
                                                filetypes=[['.dat save', '*.dat']])

def PopError(func):
    def wrap(self: tk.Toplevel, *args, **kwargs):
        try:
            _return = None
            _return = func(*args, **kwargs)
        except Exception as e:
            messagebox.showerror(title=e.__class__.__name__, message=f'{e}')
        self.deiconify()
        return _return
    return wrap

class SaveEditor(object):
    def __init__(self) -> None:
        pass

    def _update_keys(self) -> None:
        global NUMB_KEYS, LVL_KEYS, LIST_MAP
        NUMB_KEYS, LVL_KEYS = [], []
        for k, v in self.save_js.items():
            LVL_KEYS += [k] if isinstance(v, list) and len(v) > 0 and \
                               all([isinstance(l, list) and isinstance(l[1], float) for l in v]) else []
            NUMB_KEYS += [k] if k not in [*LIST_MAP.keys(), *CHK_KEYS, *UNKNOW_KEYS, *LVL_KEYS] and isinstance(v, float) else []
            if isinstance(v, list) and k not in LVL_KEYS and k not in LIST_MAP:
                LIST_MAP.update({k:v})

        for rm_key in [k for k in LIST_MAP if k not in self.save_js]:
            _ = LIST_MAP.pop(rm_key, None)
        
        for rm_key in [k for k in CHK_KEYS if k not in self.save_js]:
            _ = CHK_KEYS.remove(rm_key)

    def load_file(self, file_path: str) -> Tuple[str, int, dict]:
        self._decrypt_str = ''.join([chr(b) for b in base64.b64decode(open(file_path, 'rb').read())])
        self._trunc_point = self._decrypt_str.find('{"') if self._decrypt_str.find('{ "') == -1 else self._decrypt_str.find('{ "')
        self.save_js = json.loads(self._decrypt_str[self._trunc_point:self._decrypt_str.rfind('}')+1])
        self._update_keys()
        return self._decrypt_str, self._trunc_point, self.save_js

    def save_file(self, file_path: str):
        out_str = f"{self._decrypt_str[:self._trunc_point]}{json.dumps(self.save_js)}"
        open(file_path, 'wb+').write(base64.b64encode(bytes([ord(s) for s in out_str])))

    def inerit_save(self, orig_path: str, curr_path: str):
        _, _, orig_save_js = self.load_file(orig_path)
        self._decrypt_str, self._trunc_point, _ = self.load_file(curr_path)
        self.save_js = orig_save_js
        self.save_file(curr_path)

class mainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f'HoloCure Save Tool {VERSION}')
        self.resizable(0, 0)
        self.geometry(GEOMETRY)
        self._create_component()
        self._layout()

    def _create_component(self):
        self.editor_btn = tk.Button(self, text="Save Editor", command=lambda: editorPage(self))
        self.inherit_btn = tk.Button(self, text="Save Inheritance", command=lambda: saveInheritPage(self))
        self.about_btn = tk.Button(self, text='About', command=lambda: aboutpop(self))

    def _layout(self):
        for btn in (self.editor_btn, self.inherit_btn, self.about_btn):
            btn.pack(padx=120, pady=(10, 10))

class editorPage(tk.Toplevel):
    def __init__(self, mainapp:mainApp, **kwargs):
        super().__init__(mainapp, **kwargs)
        self.title('Holocure Save Editor')
        self.editor = SaveEditor()
        self._open_save(self)
        if self.file_path == '':
            self.destroy()
            return
        self.geometry(f"690x750{GEOMETRY}")
        self.resizable(0, 100)

    ### Mousewheel Events 
    def _bind_mouse_wheel(self, event):
        self.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _unbind_mouse_wheel(self, event):
        self.canvas.unbind_all('<MouseWheel>')

    def _on_mouse_wheel(self, event):
        self.canvas.yview_scroll(-1 * int((event.delta / 120)), "units")
    ### End of Mousewheel Events

    def _create_component(self):
        ###Create Scrollable Frame
        self.ground_frame = tk.Frame(self)
        self.ground_frame.pack(fill=tk.BOTH, expand=1)

        self.canvas = tk.Canvas(self.ground_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.vertical_bar = tk.Scrollbar(self.ground_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.vertical_bar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.vertical_bar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

        self.scroll_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.scroll_frame, anchor='nw')

        self.canvas.bind('<Enter>', self._bind_mouse_wheel)
        self.canvas.bind('<Leave>', self._unbind_mouse_wheel)
        ###End of Create Scrollable Frame

        self.mskframe = miskFrame(self)
        self.chkframes = [unlockFrame(self, key_name=k) for k in LIST_MAP.keys()]
        self.LevelFrames = [LevelFrame(self, key_name=k) for k in LVL_KEYS] 

        self.open_btn = tk.Button(self.scroll_frame, text='Open', justify=CENTER, command=lambda: self._open_save(self))
        self.save_btn = tk.Button(self.scroll_frame, text='Save', justify=CENTER, command=lambda: self._save_as(self))

    def _layout(self):
        t_col, _row = 2, 0
        self.mskframe.grid(column=0, columnspan=t_col, row=_row, sticky='news', pady=(0,10))
        for _row, frame in enumerate(self.chkframes, 1):
            frame.grid(column=0, columnspan=t_col, row=_row, sticky='news', pady=(0,5))
        for _row, frame in enumerate(self.LevelFrames, _row+1):
            frame.grid(column=0, columnspan=t_col, row=_row, sticky='news', pady=(0,10))
        self.open_btn.grid(column=0, row=_row+1)
        self.save_btn.grid(column=1, row=_row+1, pady=10)
        self.withdraw()
        self.deiconify()

    @PopError
    def _open_save(self):
        self.file_path = AskSavePath()
        if self.file_path == '':
            return
        self.editor.load_file(self.file_path)
        if hasattr(self, 'ground_frame'):
            self.ground_frame.destroy()
            # for frame in self.frames:
            #     frame.destroy()
        self._create_component()
        self._layout()

    @PopError
    def _save_as(self):
        save_file_path = asksaveasfilename(defaultextension='.dat',
                                    initialdir=os.path.dirname(os.path.abspath(self.file_path)),
                                    initialfile='save.dat',
                                    filetypes=[['.dat save', '*.dat']])
        #misk data
        self.editor.save_js.update({key: float(var.get()) for key, var in self.mskframe.var_map.items()})

        #unlocks data
        self.editor.save_js.update({frame.key_name: [key for key, val in frame.check_map.items() if val.get()]
                                    for frame in self.chkframes})

        #Levels data
        self.editor.save_js.update({frame.key_name: [[chr, float(lv.get())] for chr, lv in frame.chr_var.items()]
                                    for frame in self.LevelFrames})

        self.editor.save_file(save_file_path)
        messagebox.showinfo(title='info', message=f"Saved!\n raw_data:\n{self.editor.save_js}")

class miskFrame(tk.Frame):
    def __init__(self, parent: editorPage, **kwargs):
        super().__init__(parent.scroll_frame, **kwargs)
        self.parent = parent
        self.vcmd = (self.register(self._valid_num), '%P')
        self._create_component()
        self._layout()

    def _create_component(self):
        self.title_label = tk.Label(self, text='HoloCure Save Editor', justify=CENTER, bg='#36C6FF')

        self.var_map = {k: tk.IntVar(value=self.parent.editor.save_js[k])
                        for k in [*NUMB_KEYS, *CHK_KEYS]}
        self.lb_map = {k: tk.Label(self, text=f'{k}: ') for k in NUMB_KEYS}
        self.en_map = {k: tk.Entry(self, textvariable=self.var_map[k],
                                   validatecommand=self.vcmd, width=5) for k in NUMB_KEYS}
        self.ck_map = {k: tk.Checkbutton(self, text=f'{k}',
                                         variable=self.var_map[k], onvalue=1.0, offvalue=0.0) for k in CHK_KEYS}
        
    def _layout(self):
        col = row = 0
        self.title_label.grid(column=col, row=row, columnspan=100, sticky='nwes')
        row += 1
        for i, key in zip(range(0,len(self.lb_map)*2, 2), self.lb_map):
            col, _row = i%10, i//10+row
            self.lb_map[key].grid(column=col, row=_row, sticky='e', pady=5)
            self.en_map[key].grid(column=col+1, row=_row, sticky='w', padx=(0, 10), pady=5)
        col, row = 0, _row+1
        for i, key in enumerate(self.ck_map):
            self.ck_map[key].grid(column=i%6, row=row+i//6, columnspan=1, sticky='w', ipady=10)

    def _valid_num(self, P):
        if str.isdigit(P):
            return True
        return False

class unlockFrame(tk.Frame):
    def __init__(self, parent: editorPage, key_name:str, **kwargs):
        super().__init__(parent.scroll_frame, **kwargs)
        self.key_name = key_name
        self.parent = parent
        self.items_name = LIST_MAP[key_name]
        self._create_component()
        self._layout()
        
    def _create_component(self):
        self.sub_lb = tk.Label(self, text=f"{self.key_name}:")
        self.check_map = {k:tk.IntVar(value=1 if k in self.parent.editor.save_js[self.key_name] else 0)
                          for k in self.items_name}
        self.ck_map = {k:tk.Checkbutton(self, text=k, variable=self.check_map[k], onvalue=1, offvalue=0) for k in self.items_name}
    
    def _layout(self):
        col = row = 0
        self.sub_lb.grid(column=col,columnspan=3 ,row=row, sticky="nsw")
        row += 1
        for i, check_box in enumerate(self.ck_map.values()):
            check_box.grid(column=i%6, row=row+i//6, sticky='w', pady=(0,3), padx=(0, 5))

class LevelFrame(tk.Frame):
    def __init__(self, parent:editorPage, key_name:str, **kwargs):
        super().__init__(parent.scroll_frame, **kwargs)
        self.parent, self.key_name = parent, key_name
        self.chr_list: list = self.parent.editor.save_js[key_name]
        self._create_component()
        self._layout()

    def _create_component(self):
        self.sub_lb = tk.Label(self, text=self.key_name)
        self.chr_var = {k: tk.IntVar(value=lv) for k, lv in self.chr_list}
        self.chr_lb = {k:tk.Label(self, text=f"{k}: ") for k, _ in self.chr_list}
        self.chr_ent = {k: tk.Entry(self, width=5,
                                    textvariable=self.chr_var[k]) for k, _ in self.chr_list}

    def _layout(self):
        row = col = 0
        self.sub_lb.grid(column=col, columnspan=3, row=row, sticky='w')
        row += 1
        for i, chr in zip(range(0,len(self.chr_lb)*2,2), self.chr_lb):
            col, _row = i%14, i//14+row
            self.chr_lb[chr].grid(column=col, row=_row, sticky='w', pady=(0,5))
            self.chr_ent[chr].grid(column=col+1, row=_row, sticky='e', pady=(0,5), padx=(0,5))

class saveInheritPage(tk.Toplevel):
    def __init__(self, mainapp:mainApp, **kwargs):
        super().__init__(mainapp, **kwargs)
        self.title('Save Inheritace')
        self.geometry(GEOMETRY)
        self.resizable(0, 0)
        self.editor = SaveEditor()
        self._create_component()
        self._layout()
    
    def _create_component(self):
        self.var_map = {k: tk.StringVar(value=v)
                        for k, v in {'orig': '',
                                     'curr': os.path.join(InitPath, 'save.dat').replace('\\', '/')
                                     }.items()
                        }
        self.lb_map = {k: tk.Label(self, textvariable=self.var_map[k]) for k in {'orig', 'curr'}}
        self.open_orig_btn = tk.Button(self, text='Select Save From Other PC',
                                       command=lambda: self._select_save('orig'), width=25)
        self.open_curr_btn = tk.Button(self, text='Select Save In This PC',
                                       command=lambda: self._select_save('curr'), width=25)
        self.inherit_btn = tk.Button(self, text='Run', command=lambda: self._run_inherit(self))
        self.btn_map = {
            'orig': self.open_orig_btn,
            'curr': self.open_curr_btn
        }

    def _layout(self):
        for i, k in enumerate(('orig','curr')):
            self.btn_map[k].grid(column=0, row=i, sticky='nsw', pady=(10,0), padx=(10,0))
            self.lb_map[k].grid(column=1, row=i, sticky='nsw', pady=(10,0), padx=(5,10))
        self.inherit_btn.grid(column=0, row=2, sticky='nsw', pady=(10,10), padx=10)

    def _select_save(self, key: str):
        _file_path = AskSavePath(self.var_map[key].get()) if self.var_map[key].get() else AskSavePath()
        self.var_map[key].set(_file_path)
        self.deiconify()

    @PopError
    def _run_inherit(self):
        _orig_save = self.var_map['orig'].get()
        _curr_save = self.var_map['curr'].get()
        self.editor.inerit_save(_orig_save, _curr_save)
        messagebox.showinfo(title='Inheritence success', message=f'Success!\nRaw data:\n{self.editor.save_js}')

class aboutpop(tk.Toplevel):
    def __init__(self, mainapp, **kwargs):
        super().__init__(mainapp, **kwargs)
        self.title('About')
        self.geometry(GEOMETRY)
        self.resizable(0, 0)
        self._create_component()
        self._layout()

    def _create_component(self):
        self.txt = tk.Text(self, wrap='word', height=len(ABOUT_MSG.split('\n')), bg=mainapp.cget('bg'), font=('Arial', 10))
        self.txt.insert('end', ABOUT_MSG)
        self.txt.config(state=DISABLED)
        self.ok_btn = tk.Button(self, text='OK', command=lambda: self.destroy())

    def _layout(self):
        self.txt.pack()
        self.ok_btn.pack(anchor=CENTER)

if __name__ == "__main__":
    mainapp = mainApp()
    mainapp.mainloop()