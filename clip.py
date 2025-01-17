import win32clipboard
from charset_normalizer import detect

class ClipboardContext:
    def __enter__(self):
        win32clipboard.OpenClipboard()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        win32clipboard.CloseClipboard()
        
    def enum(self, format):
        return win32clipboard.EnumClipboardFormats(format)

    def get(self, format):
        return win32clipboard.GetClipboardData(format)

    def set(self, format, data):
        win32clipboard.SetClipboardData(format, data)

    def clear(self):
        win32clipboard.EmptyClipboard()
        
    def set_html(self):
        win32clipboard.RegisterClipboardFormat("HTML Format")



class ExtBytes(bytes):
    def __new__(cls, arg):
        instance = super().__new__(cls, arg)
        return instance

    def __init__(self, arg):
        self.encoding, self.confidence = self.pred_encode()

    def replace(self, old, new, count=-1, varbose=False):
        if isinstance(self, bytes):
            if varbose:
                print(f"encoding: {self.encoding}, confidence: {self.confidence}")
            return ExtBytes(self.decode().replace(old, new, count).encode(self.encoding))
        else:
            raise TypeError("Unsupported data type for replace")
    
    def decode(self):
        return super().decode(self.encoding)
        
    def pred_encode(self):
        result = detect(self)
        encoding = result["encoding"]
        confidence = result["confidence"]

        return encoding, confidence

    def __repr__(self):
        return super().__repr__()
    
    def __str__(self):
        if self.encoding is None:
            return super().__repr__()
        else:
            # return self.decode()
            return f"=== encoding: {self.encoding}, confidence: {self.confidence}\n{self.decode()}"


class NotionType(ExtBytes):
    def pred_encode(self):
        encoding = "utf-16-le"
        confidence = 1
        
        return encoding, confidence
        

class Clip(dict):
    def __init__(self, datas=None, autofetch=True):
        super().__init__()
        if datas is None:
            if autofetch:
                with ClipboardContext() as clipboard:
                    format = 0
                    while (format := clipboard.enum(format)):
                        self[format] = clipboard.get(format)
        else:
            self.update(datas)
            
    def set_clipboard(self):
        with ClipboardContext() as clipboard:
            clipboard.clear()
            for format, data in self.items():
                clipboard.set(format, data)
    
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
    
    def __setitem__(self, key, value):
        if key in range(49700, 49800):    # Notion
            value = NotionType(value)
        elif isinstance(value, bytes):
            value = ExtBytes(value)
        super().__setitem__(key, value)
