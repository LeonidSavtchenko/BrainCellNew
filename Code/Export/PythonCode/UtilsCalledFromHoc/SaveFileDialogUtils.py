
import os
import tkinter as tk
from tkinter import filedialog, messagebox


root = tk.Tk()
root.withdraw()


class SaveFileDialogUtils:

    isBusy = False
    top = None
    
    @classmethod
    def showSaveFileDialog(cls, defaultDirPath, defaultFileName):
        
        if cls.isBusy:
            cls.top.lift()
            return ''
            
        cls.isBusy = True
        
        cls.top = tk.Toplevel(root)
        cls.top.withdraw()
        
        try:
            outHocFilePathName = filedialog.asksaveasfilename(
                title='Export brain cell with nanogeometry',
                initialdir=defaultDirPath,
                initialfile=defaultFileName,
                filetypes=[('HOC File', '*.hoc'), ('All Files', '*.*')],
                defaultextension='.hoc',
                parent=cls.top
            )
            
            # !!!! if the folder is not empty, then ask user whether to clean up
            
            return outHocFilePathName
            
        finally:
            cls.top.destroy()
            cls.isBusy = False
            