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
    return _base_dialog(True, **kwargs)

def savefile(**kwargs) -> str:
    return _base_dialog(False, **kwargs)