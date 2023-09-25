
import os
import tkinter as tk
from tkinter import filedialog, messagebox


root = tk.Tk()
root.withdraw()


# !!!! a lot of code dupl. in two methods below

class FileDialogUtils:

    reservedFileNamesLower = {'params.hoc', 'runner.hoc'}
    
    isBusy = False
    top = None
    
    # !!!! BUG: import biophysics -> leave dialog open -> export biophysics -> click "Export" -> it puts the old "import" file dialog in focus
    #           the correct behaviour would be to close it once user clicks export biophysics
    #           (the same problem when first clicking export biophysics, then import biophysics)
    
    @classmethod
    def showLoadFileDialog(cls, theTitle, defaultDirPath):
        
        if cls.isBusy:
            cls.top.lift()
            return ''
            
        cls.isBusy = True
        
        cls.top = tk.Toplevel(root)
        cls.top.withdraw()
        
        try:
            while True:
                inHocFilePathName = filedialog.askopenfilename(
                    title=theTitle,
                    initialdir=defaultDirPath,
                    filetypes=[('HOC File', '*.hoc'), ('All Files', '*.*')],    # !!! should be different when loading the base geometry
                    defaultextension='.hoc',                                    # !!!
                    parent=cls.top)
                    
                fileName = os.path.basename(inHocFilePathName)
                
                if fileName.lower() in cls.reservedFileNamesLower:  # !! os.path.samefile would be more correct than lower-case comparison
                    messagebox.showwarning(
                        title='Reserved name',
                        message=f'Cannot import "{fileName}" because it\'s a reserved file name.\n\nPlease use some other name.')   # !!!???
                else:
                    break
                    
            return inHocFilePathName
            
        finally:
            cls.top.destroy()
            cls.isBusy = False
            
    @classmethod
    def showSaveFileDialog(cls, theTitle, defaultDirPath, defaultFileName):
        
        if cls.isBusy:
            cls.top.lift()
            return ''
            
        cls.isBusy = True
        
        cls.top = tk.Toplevel(root)
        cls.top.withdraw()
        
        try:
            while True:
                outHocFilePathName = filedialog.asksaveasfilename(
                    title=theTitle,
                    initialdir=defaultDirPath,
                    initialfile=defaultFileName,
                    filetypes=[('HOC File', '*.hoc'), ('All Files', '*.*')],
                    defaultextension='.hoc',
                    parent=cls.top)
                    
                fileName = os.path.basename(outHocFilePathName)
                
                if fileName.lower() in cls.reservedFileNamesLower:  # !! os.path.samefile would be more correct than lower-case comparison
                    messagebox.showwarning(
                        title='Reserved name',
                        message=f'Cannot export to "{fileName}" because it\'s a reserved file name.\n\nPlease use some other name.')    # !!!???
                else:
                    break
                    
            # !! if the folder is not empty, then ask user whether to clean up
            
            return outHocFilePathName
            
        finally:
            cls.top.destroy()
            cls.isBusy = False
            