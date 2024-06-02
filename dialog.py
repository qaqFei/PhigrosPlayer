import win32ui

def _base_dialog(
    bFileOpen:bool,
    Filter:str = "",
    fn:str = ""
) -> str:
    dlg = win32ui.CreateFileDialog(
        bFileOpen,
        None,
        fn,
        0,
        Filter
    )
    dlg.DoModal()
    return dlg.GetPathName()

def openfile(**kwargs) -> str:
    return _base_dialog(1,**kwargs)

def savefile(**kwargs) -> str:
    return _base_dialog(0,**kwargs)