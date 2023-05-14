# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class MDT(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = self._io.read_bytes(4)
        if not self.magic == b"\x4D\x53\x47\x44":
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x53\x47\x44", self.magic, self._io, u"/seq/0")
        self.amnt_text_len = self._io.read_u4be()
        self.text_lens = []
        for i in range(self.amnt_text_len):
            self.text_lens.append(self._io.read_u4be())



