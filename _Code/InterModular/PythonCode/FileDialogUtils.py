
import os
import tkinter as tk
from enum import Enum
from tkinter import filedialog, messagebox


root = tk.Tk()
root.withdraw()


class FileDialogUtils:

    class EnumInFileTypes(Enum):
        baseGeometryAny = 0
        baseGeometryHoc = 1
        nanoGeometryHoc = 2
        biophysJson = 3
        binaryResultsBin = 4
        """ !!! in the future, we can add support for:
        distFuncHoc
        distFuncPy
        distFuncTxt
        distFuncXlsx
        diamDistrFile
        """
        
    class EnumOutFileTypes(Enum):
        baseGeometryHoc = 0
        nanoGeometryHoc = 1
        biophysJson = 2
        binaryResultsBin = 3
        textResultsTxt = 4
        """ !!! in the future, we can add support for these files saved to "Text results" folder:
        volumFractionTxt
        cadynamicsTxt
        circularFrapAverageTxt
        timeFRAPTxt
        """
        
    _inFileTypeToArgsDict = {
        EnumInFileTypes.baseGeometryAny: {
            'title': 'Import brain cell base geometry',
            'initialdir': 'Geometry',
            'filetypes': [('All Files', '*.*'), ('HOC File', '*.hoc'), ('SWC File', '*.swc'), ('ZIP Archive from NeuroMorpho.org', '*.zip')]},  # !!! ideally, enlist explicitly each file type supported by NLMorphologyConverter, but need to test first
        EnumInFileTypes.baseGeometryHoc: {
            'title': 'Import external NEURON simulation',
            'initialdir': 'External simulations',
            'filetypes': [('HOC File', '*.hoc'), ('All Files', '*.*')],
            'defaultextension': '.hoc'},
        EnumInFileTypes.nanoGeometryHoc: {
            'title': 'Import brain cell with nanogeometry',
            'initialdir': 'Nanogeometry',
            'filetypes': [('HOC File', '*.hoc'), ('All Files', '*.*')],
            'defaultextension': '.hoc'},
        EnumInFileTypes.biophysJson: {
            'title': 'Import brain cell biophysics',
            'initialdir': 'Biophysics',
            'filetypes': [('JSON File', '*.json'), ('All Files', '*.*')],
            'defaultextension': '.json'},
        EnumInFileTypes.binaryResultsBin: {
            'title': 'Load basket cell GABA diffusion animation',
            'initialdir': 'Binary results',
            'filetypes': [('BIN File', '*.bin'), ('All Files', '*.*')],
            'defaultextension': '.bin'}
    }
    
    _outFileTypeToArgsDict = {
        EnumOutFileTypes.baseGeometryHoc: {
            'title': 'Export brain cell base geometry',
            'initialdir': 'Geometry',
            'filetypes': [('HOC File', '*.hoc'), ('All Files', '*.*')],
            'defaultextension': '.hoc'},
        EnumOutFileTypes.nanoGeometryHoc: {
            'title': 'Export brain cell with nanogeometry',
            'initialdir': 'Nanogeometry',
            'filetypes': [('HOC File', '*.hoc'), ('All Files', '*.*')],
            'defaultextension': '.hoc'},
        EnumOutFileTypes.biophysJson: {
            'title': 'Export brain cell biophysics',
            'initialdir': 'Biophysics',
            'filetypes': [('JSON File', '*.json'), ('All Files', '*.*')],
            'defaultextension': '.json'},
        EnumOutFileTypes.binaryResultsBin: {
            'title': 'Save basket cell GABA diffusion animation',
            'initialdir': 'Binary results',
            'filetypes': [('BIN File', '*.bin'), ('All Files', '*.*')],
            'defaultextension': '.bin'},
        EnumOutFileTypes.textResultsTxt: {
            'title': 'Save basket cell GABA diffusion animation',
            'initialdir': 'Text results',
            'filetypes': [('TXT File', '*.txt'), ('All Files', '*.*')],
            'defaultextension': '.txt'}
    }
    
    # !!! keep these file names in sync with other code
    _reservedHocFileNamesLower = {'params.hoc', 'runner.hoc'}
    _reservedJsonFileNamesLower = {'hide_stoch_btn_for.json', 'diffusible_species.json'}
    
    _isBusy = False
    _top = None
    
    # !!! BUG: import biophysics -> leave dialog open -> export biophysics -> click "Export" -> it puts the old "import" file dialog in focus
    #          the correct behaviour would be to close it once user clicks export biophysics
    #          (the same problem when first clicking export biophysics, then import biophysics)
    
    
    # !!! a lot of code dupl. in two methods below
    
    @classmethod
    def showLoadFileDialog(cls, enumInFileType):
        
        if cls._isBusy:
            cls._top.lift()
            return ''
            
        cls._isBusy = True
        
        cls._top = tk.Toplevel(root)
        cls._top.withdraw()
        
        argsDict = cls._inFileTypeToArgsDict[enumInFileType]
        
        try:
            while True:
                inFilePathName = filedialog.askopenfilename(parent=cls._top, **argsDict)
                
                fileName = os.path.basename(inFilePathName)
                
                cond1 = enumInFileType in [cls.EnumInFileTypes.baseGeometryAny, cls.EnumInFileTypes.nanoGeometryHoc] and \
                   fileName.lower() in cls._reservedHocFileNamesLower       # !! os.path.samefile would be more correct than lower-case comparison
                cond2 = enumInFileType == cls.EnumInFileTypes.biophysJson and \
                   fileName.lower() in cls._reservedJsonFileNamesLower
                if cond1 or cond2:
                    messagebox.showwarning(
                        title='Reserved name',
                        message=f'Cannot import "{fileName}" because it\'s a reserved file name.\n\nPlease use some other name.')
                    # !!! use just selected folder as 'initialdir' when calling filedialog.askopenfilename next time
                else:
                    break
                    
            return inFilePathName
            
        finally:
            cls._top.destroy()
            cls._isBusy = False
            
    @classmethod
    def showSaveFileDialog(cls, enumOutFileType, defaultFileName):
        
        if cls._isBusy:
            cls._top.lift()
            return ''
            
        cls._isBusy = True
        
        cls._top = tk.Toplevel(root)
        cls._top.withdraw()
        
        argsDict = cls._outFileTypeToArgsDict[enumOutFileType]
        
        try:
            while True:
                outFilePathName = filedialog.asksaveasfilename(parent=cls._top, initialfile=defaultFileName, **argsDict)
                
                fileName = os.path.basename(outFilePathName)
                
                cond1 = enumOutFileType in [cls.EnumOutFileTypes.baseGeometryHoc, cls.EnumOutFileTypes.nanoGeometryHoc] and \
                   fileName.lower() in cls._reservedHocFileNamesLower       # !! os.path.samefile would be more correct than lower-case comparison
                cond2 = enumOutFileType == cls.EnumOutFileTypes.biophysJson and \
                   fileName.lower() in cls._reservedJsonFileNamesLower
                if cond1 or cond2:
                    messagebox.showwarning(
                        title='Reserved name',
                        message=f'Cannot export to "{fileName}" because it\'s a reserved file name.\n\nPlease use some other name.')
                    # !!! use just selected folder as 'initialdir' when calling filedialog.asksaveasfilename next time
                else:
                    break
                    
            # !!! for EnumOutFileTypes.nanoGeometryHoc, if the folder is not empty, then ask user whether to clean up
            
            return outFilePathName
            
        finally:
            cls._top.destroy()
            cls._isBusy = False
            