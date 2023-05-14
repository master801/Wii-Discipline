meta:
  id: mdt
  file-extension: mdt
  endian: be
seq:
  - id: magic
    contents: [ 0x4D, 0x53, 0x47, 0x44 ]
  - id: amnt_text_len
    type: u4be
  - id: text_lens
    type: u4be
    repeat: expr
    repeat-expr: amnt_text_len
