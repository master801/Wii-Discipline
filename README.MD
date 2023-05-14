# Wii-Discipline

Discipline: Teikoku no Tanjou (ディシプリン＊帝国の誕生)<br/>
<Would have cover art here, but none really exist...>

---

## main.py
Text dumper and inserter.

### Usage:
* `--mode`
  * `dump`
  * `insert`
* `--csv`
  * Directory containing CSV files, or CSV file
    * `dump` - May not exist
    * `insert` - Must exist
* `--mdt`
  * Directory containing MDT files, or MDT file
    * `dump` - Must exist
    * `insert` - May not exist


### Examples:

#### Dumping
```batch
python main.py --mode=dump --mdt=mdt --csv=csv
```
Dumps text from mdt files in a folder to specified csv directory.<br/>
`mdt` is a folder containing `.mdt` files<br/>
`csv` does not exist. This folder will be created automatically.

#### Inserting
```batch
python main.py --mode=insert --csv=csv --mdt=new_mdt
```
Creates `.mdt` files from text in dumped csv directory.<br/>
`csv` is the folder containing dumped `.csv` files<br/>
`new_mdt` does not exist. This folder will be created automatically.

### Requirements:
* [Python 3.11.0](https://www.python.org/downloads/release/python-3110/)
* [kaitaistruct 0.10](https://pypi.org/project/kaitaistruct/0.10/)


---

## CSV file standards:
* Encoding should be UTF-8. Always.
  * Tool expects the file to be saved in UTF-8 encoding since it's a universal encoding.
* Second row (below the header -first- row) should always be blank.
  * Don't ask. I don't understand why either, but that's how the original file is set up. 
* Newlines (`\n`) used in a CSV row will literally be used in the actual script.
  * What you give is what you will see in-game.
  * **Do not use *carelessly*.**
* Word `<NULL>` signifies when the string ends.
  * **Do *NOT* remove. I am not responsible if any unexpected behavior occurs if this is removed.**
* Lines should not exceed 20 characters. 
  * Don't know what will happen otherwise, but probably not good things.

## Weird unexpected behavior (or bug):
So, in file `episodeendroll.mdt`, the last string in the file ends with `0x0D` (`\r`).
However, when this tool recreates the same file via its dumped `.csv` file, `0x0D` (`\r`) turns into `0x0A` (`\n`).<br/>
**I have no idea if the original `episodeendroll.mdt` uses `\r` intentionally or not.**

---

## Built with:
 - [Kaitai Struct](https://kaitai.io/)
 - [PyCharm](https://www.jetbrains.com/pycharm/) 2023.1.2 RC (Community Edition)
