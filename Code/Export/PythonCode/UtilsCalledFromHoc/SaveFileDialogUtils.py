
import os
import tkinter as tk
from tkinter import filedialog, messagebox


root = tk.Tk()
root.withdraw()


class SaveFileDialogUtils:

    reservedFileNamesLower = {'params.hoc', 'runner.hoc'}
    
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
            while True:
                outHocFilePathName = filedialog.asksaveasfilename(
                    title='Export brain cell with nanogeometry',
                    initialdir=defaultDirPath,
                    initialfile=defaultFileName,
                    filetypes=[('HOC File', '*.hoc'), ('All Files', '*.*')],
                    defaultextension='.hoc',
                    parent=cls.top)
                    
                fileName = os.path.basename(outHocFilePathName)
                
                if fileName.lower() in cls.reservedFileNamesLower:  # !! os.path.samefile would be more correct than lower-case comparison
                    messagebox.showwarning(
                        title='Reserved name',
                        message=f'Cannot export to "{fileName}" because it\'s a reserved file name.\n\nPlease use some other name.')
                else:
                    break
                    
            # !! if the folder is not empty, then ask user whether to clean up
            
            return outHocFilePathName
            
        finally:
            cls.top.destroy()
            cls.isBusy = False
            