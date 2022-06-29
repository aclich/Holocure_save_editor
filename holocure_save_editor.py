ABOUT_MSG='''HoloCure bad bad Save Editor
Version: 0.0.1
Date: 2022/06/29
Author: Aclich
Require: python > 3.6, tkinter
Source code: https://github.com/aclich/Holocure_save_editor

Tested Game version
0.3.1656491913
0.3.1656105128'''


import json, base64, pathlib, os
import tkinter as tk
from tkinter import CENTER, DISABLED, messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import List

KEYS = ['HP', 'ATK', 'SPD', 'EXP', 'crit', 'haste',
        'food', 'moneyGain','regen', 'reroll', 'specCDR',
        'pickupRange','specUnlock','holoCoins', 
        'refund', 'challenge','eliminate',
        'randomMoneyKey', 'unlockedCharacters',
        'unlockedWeapons', 'unlockedItems', 'seenCollabs', 'characters' ]
LIST_KEYS = ['unlockedItems', 'unlockedWeapons', 'seenCollabs', 'characters']
CHK_KEYS = ['specUnlock', 'refund', 'challenge']
UNKNOW_KEYS = ['unlockedCharacters', 'eliminate']
NUMB_KEYS = [k for k in KEYS if k not in [*LIST_KEYS, *CHK_KEYS, *UNKNOW_KEYS]]

LIST_MAP = {'unlockedItems': ['BodyPillow', 'FullMeal', 'PikiPikiPiman', 'SuccubusHorn', 'Headphones', 'UberSheep',
                              'HolyMilk', 'Sake', 'FaceMask', 'CreditCard', 'GorillasPaw', 'InjectionAsacoco',
                              'IdolCostume', 'Plushie', 'StudyGlasses', 'SuperChattoTime', 'EnergyDrink'],
            'unlockedWeapons': ['PsychoAxe', 'Glowstick', 'SpiderCooking', 'Tailplug', 'BLBook', 'EliteLava',
                                'HoloBomb', 'HoloLaser', 'CuttingBoard', 'IdolSong'],
            'seenCollabs': ['BreatheInAsacoco', 'DragonBeam', 'EliteCooking', 'FlatBoard',
                            'MiComet', 'BLLover', 'LightBeam', 'IdolConcert']}

class SaveEditor(object):
    def __init__(self, file_path: str) -> None:
        self.load_file(file_path)

    def load_file(self, file_path):
        _data = open(file_path, 'r').read()
        self._decrypt_str = ''.join([chr(b) for b in base64.decodebytes(_data.encode())])
        _trunc_point = self._decrypt_str.find('{ "')
        self._trunc_point = self._decrypt_str.find('{"') if _trunc_point == -1 else _trunc_point
        self.save_js = json.loads(self._decrypt_str[self._trunc_point:-1])
        print(self.save_js)

    def save_file(self, file_path):
        out_str = f"{self._decrypt_str[:self._trunc_point]}{json.dumps(self.save_js)}{self._decrypt_str[-1]}"
        out_en = bytes([ord(s) for s in out_str])
        open(file_path, 'w+').write(base64.encodebytes(out_en).decode().replace('\n', ''))
        

class mainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('HoloCure save editor v0.0.1')
        self.resizable(0, 0)
        self._open_save()
        self._create_component()
        self._layout()

    def _create_component(self):
        self.mskframe = miskFrame(self)
        self.chkframes = [unlockFrame(self, key_name='unlockedItems'),
                          unlockFrame(self, key_name='unlockedWeapons'),
                          unlockFrame(self, key_name='seenCollabs')]
        self.charaframe = charaFrame(self)

        self.frames: List[tk.Frame] = [self.mskframe, *self.chkframes, self.charaframe]
        self.open_btn = tk.Button(self, text='Open', justify=CENTER, command=self._open_save)
        self.save_btn = tk.Button(self, text='Save', justify=CENTER, command=self._save_as)
        self.about_btn = tk.Button(self, text='About', justify=CENTER, 
                                   command=lambda: aboutpop(self))

    def _layout(self):
        t_col = 3
        self.mskframe.grid(column=0, columnspan=t_col, row=0, sticky='news', pady=(0,10))
        for i, frame in enumerate(self.chkframes, 1):
            frame.grid(column=0, columnspan=t_col, row=i, sticky='news', pady=(0,5))
        self.charaframe.grid(column=0, columnspan=t_col, row=4, sticky='nwes', pady=(0,10))
        self.open_btn.grid(column=0, row=5)
        self.save_btn.grid(column=1, row=5, pady=10)
        self.about_btn.grid(column=2, row=5, pady=10)

    def _open_save(self):
        _init_path = os.path.join(pathlib.Path.home(),'AppData', 'Local', 'HoloCure')
        self._init_path = _init_path if os.path.isdir(_init_path) else pathlib.Path.home()
        self.file_path = askopenfilename(title='select save data',
                                         initialdir=_init_path,
                                         filetypes=[['.dat save', '*.dat']])
        print(self.file_path)
        self.editor = SaveEditor(self.file_path)
        if hasattr(self, 'mskframe'):
            for frame in self.frames:
                frame.destroy()
            self._create_component()
            self._layout()

    def _save_as(self):
        save_file_path = asksaveasfilename(defaultextension='.dat',
                                      initialdir=self._init_path,
                                      initialfile='save.dat',
                                      filetypes=[['.dat save', '*.dat']])
        #misk data
        for key, var in self.mskframe.var_map.items():
            self.editor.save_js[key] = float(var.get())
        
        #unlocks data
        for frame in self.chkframes:
            items = []
            for key, val in frame.check_map.items():
                if val.get():
                    items.append(key)
            self.editor.save_js[frame.key_name] = items

        #character level
        chr_list = []
        for chr, lv in self.charaframe.chr_var.items():
            chr_list.append([chr, float(lv.get())])
        self.editor.save_js['characters'] = chr_list

        self.editor.save_file(save_file_path)
        messagebox.showinfo(title='info', message=f"Saved!\n raw_data:\n{self.editor.save_js}")

class miskFrame(tk.Frame):
    def __init__(self, mainapp: mainApp, **kwargs):
        super().__init__(mainapp, **kwargs)
        self.mainapp = mainapp
        self.vcmd = (self.mainapp.register(self._valid_num), '%P')
        self._create_component()
        self._layout()

    def _create_component(self):
        self.title_label = tk.Label(self, text='HoloCure Save Editor', justify=CENTER, bg='#36C6FF')

        self.var_map = {k: tk.IntVar(value=self.mainapp.editor.save_js[k])
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
        for key in self.lb_map:
            self.lb_map[key].grid(column=col, row=row, sticky='e', pady=5)
            self.en_map[key].grid(column=col+1, row=row, sticky='w', padx=(0, 10), pady=5)
            col += 2
            if col > 8:
                row += 1
                col = 0
        row +=1
        col = 0
        for key in self.ck_map:
            self.ck_map[key].grid(column=col, row=row, columnspan=1, sticky='w', ipady=10)
            col += 1
            if col > 6:
                row += 1
                col = 0

    def _valid_num(self, P):
        print(P)
        # return True
        if str.isdigit(P) or P == '':
            return True
        return False

class unlockFrame(tk.Frame):
    def __init__(self, parent: mainApp, key_name:str, **kwargs):
        super().__init__(parent, **kwargs)
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
        for check_box in self.ck_map.values():
            check_box.grid(column=col, row=row, sticky='w', pady=(0,3), padx=(0, 5))
            col += 1
            if col > 5:
                col = 0
                row += 1

class charaFrame(tk.Frame):
    def __init__(self, mainapp:mainApp, **kwargs):
        super().__init__(mainapp, **kwargs)
        self.mainapp = mainapp
        self.chr_list: list = self.mainapp.editor.save_js['characters']
        self._create_component()
        self._layout()

    def _create_component(self):
        self.sub_lb = tk.Label(self, text="Characters LV:")
        self.chr_var = {k: tk.IntVar(value=lv) for k, lv in self.chr_list}
        self.chr_lb = {k:tk.Label(self, text=f"{k}: ") for k, _ in self.chr_list}
        self.chr_ent = {k: tk.Entry(self, width=5,
                                    textvariable=self.chr_var[k]) for k, _ in self.chr_list}

    def _layout(self):
        row = col = 0
        self.sub_lb.grid(column=col, columnspan=3, row=row, sticky='w')
        row += 1
        for chr in self.chr_lb:
            self.chr_lb[chr].grid(column=col, row=row, sticky='w', pady=(0,5))
            self.chr_ent[chr].grid(column=col+1, row=row, sticky='e', pady=(0,5), padx=(0,5))
            col += 2
            if col > 12:
                col = 0
                row += 1

class aboutpop(tk.Toplevel):
    def __init__(self, mainapp):
        super().__init__(mainapp)
        self.title('About')
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
    try:
        mainapp = mainApp()
        mainapp.withdraw()
        mainapp.deiconify()
        mainapp.mainloop()
    except Exception as e:
        messagebox.showerror(title='error', message=f'{e}')
        mainapp.destroy()