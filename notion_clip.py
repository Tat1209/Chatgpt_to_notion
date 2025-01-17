from charset_normalizer import detect
from clip import ClipboardHandler, Clip
    
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
    format_name = "Chromium Web Custom MIME Data Format"
    format_key = "Notion"
    
    def pred_encode(self):
        encoding = "utf-16-le"
        confidence = 1
        
        return encoding, confidence

class HTMLType(ExtBytes):
    format_name = "HTML Format"
    format_key = "HTML_bin"


class NotionClip(Clip):
    def __init__(self, datas=None, autofetch=True):
        self.type_list = [NotionType, HTMLType] # Notionみがあるのはここだけ 継承でもっと汎用的になるはず
        self.trans_fr, self.trans_rf = self.make_trans()
        super().__init__(datas, autofetch)
        # converted_dict = {self.trans_rf[k]: v for k, v in self.items()}
        # self.clear()  # 既存のキーと値を削除
        # self.update(converted_dict)  # 変換後のキーと値を追加
        # print("aaaaa")

    def make_trans(self):
        trans_fr = {}
        trans_rf = {}
        with ClipboardHandler() as ch:
            for key, value in ch.get_formatnames().items():
                format_key = key
                for type_cls in self.type_list:
                    if value == type_cls.format_name:
                        format_key = type_cls.format_key
                        break
                trans_fr[format_key] = key
                trans_rf[key] = format_key

        return trans_fr, trans_rf

    def _set(self, clipboard, format):
        if format in [type_cls.format_key for type_cls in self.type_list]:
            format = self.trans_fr[format]
        clipboard.set(format, self[format])

    def __setitem__(self, key, value):
        key = self.trans_rf.get(key, key) # ここの配置が一番丸い initのときに呼ばれるとき以外は例外処理として第2引数が返される
        is_processed = False
        for type_cls in self.type_list:
            if key == type_cls.format_key:
                value = type_cls(value)
                is_processed = True
                break

        if not is_processed and isinstance(value, bytes):
            value = ExtBytes(value)
        
        super().__setitem__(key, value)
        return self