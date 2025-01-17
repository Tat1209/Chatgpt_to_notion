import win32clipboard

class ClipboardHandler:
    def __enter__(self):
        win32clipboard.OpenClipboard()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        win32clipboard.CloseClipboard()
        
    def enum(self, format):
        return win32clipboard.EnumClipboardFormats(format)
    
    def get_formats(self):
        formats = []
        format = 0
        while (format := self.enum(format)):
            formats.append(format)
        return formats
    
    def get_formatname(self, format):
        try:
            return win32clipboard.GetClipboardFormatName(format)
        except Exception:
            return "standard_format"

    def get_formatnames(self):
        names = {}
        for format in self.get_formats():
            names[format] = self.get_formatname(format)
        return names

    def get(self, format):
        return win32clipboard.GetClipboardData(format)

    # Clip型には非対応
    def get_all(self):
        datas = {}
        for format in self.get_formats():
            datas[format] = self.get(format)
        return datas

    def set(self, format, data):
        win32clipboard.SetClipboardData(format, data)

    def set_all(self, datas):
        for format, data in datas.items():
            self.set(format, data)

    def clear(self):
        win32clipboard.EmptyClipboard()
        
    def register_format(self, name):
        return win32clipboard.RegisterClipboardFormat(name)
        # return win32clipboard.RegisterClipboardFormat("HTML Format")


class Clip(dict):
    def __init__(self, datas=None, autofetch=True):
        super().__init__()
        if datas is None:
            if autofetch:
                with ClipboardHandler() as clipboard:
                    for format in clipboard.get_formats():
                        self[format] = clipboard.get(format)
        else:
            self.update(datas)
            
    def _set(self, clipboard, format):
        clipboard.set(format, self[format])
            
    def set_clipboard(self):
        with ClipboardHandler() as clipboard:
            clipboard.clear()
            for format in self.keys():
                self._set(clipboard, format)
            # for format, data in self.items():
                # clipboard.set_all(self)
    
    def get_formats(self):
        return list(self.keys())

    def datas_sel(self, formats):
        return Clip({format: self[format] for format in formats})

    def datas_copy(self):
        return Clip(self.copy())
    
    def disp(self):
        for format in self.get_formats():
            print(f"=== format: {format}")
            print(self[format])
            print()
            
    
