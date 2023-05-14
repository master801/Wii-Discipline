#!/usr/bin/env python3
# Created by Master on 5/11/2023 at 5:07 AM

import argparse
import io
import os
import glob
import csv
import struct

import mdt

MAGIC: bytes = b'\x4D\x53\x47\x44'  # MSGD
JIS_ENCODING = 'shift_jisx0213'  # can't use shift-jis because it can't decode "﨑" properly - WTF


def write_mdt_file(fp_csv: str, fp_mdt: str):
    csv_lines: list = []
    with open(fp_csv, mode='rt+', encoding='utf-8') as io_csv:
        csv_reader = csv.reader(io_csv, quotechar='\"', quoting=csv.QUOTE_NONNUMERIC)
        for i in csv_reader:
            csv_lines.append(i)
            continue
        del i
        csv_lines.pop(0)  # pop header
        del csv_reader
        pass
    del io_csv

    lines: list[bytes] = [b'']
    for i in range(1, len(csv_lines)):  # skip first entry
        if len(csv_lines[i][1]) > 0:  # has eng translation
            csv_line = csv_lines[i][1]
            pass
        else:  # default to jap
            csv_line = csv_lines[i][0]
            pass
        print(f'Read csv line \"{csv_line}\"')
        line_bytes = csv_line.encode(encoding=JIS_ENCODING).replace(b'<NULL>', b'\x00')
        print(f'Read csv line bytes {line_bytes}')
        if line_bytes[-4:] == b'\x0A\x00\x00\x00':  # episodeendroll.mdt - last string - \n should be \r - intentional?
            line_bytes = bytes(line_bytes[:-4] + b'\x0D\x00\x00\x00')
            print('Fixed weird endline bug')
            pass
        lines.append(line_bytes)
        print()
        continue
    del i
    del csv_lines

    if os.path.exists(fp_mdt):
        mode_mdt = 'w+'
        pass
    else:
        mode_mdt = 'x+'
        pass
    print(f'Writing MDT to \"{fp_mdt}\"...')
    with open(fp_mdt, mode=f'b{mode_mdt}') as io_mdt:
        io_mdt.write(MAGIC)  # +4
        io_mdt.write(struct.pack('>I', len(lines) - 1))  # +4

        for i in range(0, len(lines)-1):  # write len header table
            if i == 0:
                io_mdt.write(struct.pack('>I', len(lines[i])))  # 0, +4
                pass
            else:
                # wack-ass calculation
                text_len = len(lines[i])
                io_mdt.seek(-4, io.SEEK_CUR)
                last_len = struct.unpack('>I', io_mdt.read(0x04))[0]
                actual_len = last_len + text_len
                io_mdt.write(struct.pack('>I', actual_len))
                print(f'Wrote length 0x{actual_len:04X}...')
                del actual_len
                del last_len
                del text_len
                pass
            continue
        del i

        print()

        for line in lines:
            io_mdt.write(line)
            print(f'Wrote line bytes {line}')
            continue
        del line
        pass
    print('Done writing!')
    del lines
    del fp_mdt
    del mode_mdt
    del io_mdt
    return


def write_mdt_files(dir_csv: str, dir_mdt: str):
    csv_files: list[str] = []
    mdt_files: list[str] = []

    for i in glob.glob1(dir_csv, '*.csv'):
        csv_files.append(os.path.join(dir_csv, i))
        continue
    if os.path.exists(dir_mdt):
        for i in glob.glob1(dir_mdt, '*.mdt'):
            mdt_files.append(os.path.join(dir_mdt, i))
            continue
        pass
    else:
        for i in csv_files:
            if i.endswith('.csv'):
                trimmed = i[:i.rindex('.csv')]
                if os.path.sep in trimmed:
                    trimmed = trimmed[trimmed.rindex(os.path.sep)+1:]
                    pass
                mdt_files.append(os.path.join(dir_mdt, trimmed))
                pass
            else:
                raise NotImplementedError('I don\'t know what happened, I swear!')
            continue
        pass

    if len(mdt_files) != len(csv_files):
        print(f'Unequal file listings!')
        print(f'MDT: {len(mdt_files)}')
        print(f'CSV: {len(csv_files)}')
        return

    if os.path.exists(dir_mdt) and not os.path.isdir(dir_mdt):
        print(f'Selected CSV \"{dir_mdt}\" is not a directory!')
        return
    elif not os.path.exists(dir_mdt):
        print(f'Directory \"{dir_mdt}\" does not existing. Making...')
        os.makedirs(dir_mdt)
        print('Done making directory')
        pass

    for i in range(len(csv_files)):
        print(f'Inserting text to \"{mdt_files[i]}\" from CSV \"{csv_files[i]}\"...')
        write_mdt_file(csv_files[i], mdt_files[i])
        print('Done inserting!\n\n')
        continue
    return


def read_mdt_file(fp_mdt: str, fp_csv: str):
    lines: list[str] = []
    with open(fp_mdt, mode='rb+') as io_mdt:
        io_mdt.seek(0, io.SEEK_END)
        eof: int = io_mdt.tell()
        io_mdt.seek(0, io.SEEK_SET)

        _mdt: mdt.MDT = mdt.MDT.from_io(io_mdt)
        for i in range(len(_mdt.text_lens)):
            text_len = _mdt.text_lens[i]
            if i > 0:
                prev_len = _mdt.text_lens[i-1]
                pass
            else:
                prev_len = 0
                pass

            print(f'Found text at 0x{io_mdt.tell():04X}')

            actual_len = text_len - prev_len
            text_bytes: bytes = io_mdt.read(actual_len).replace(b'\x00', b'<NULL>')
            decoded: str = text_bytes.decode(encoding=JIS_ENCODING)
            print(f'Found \"{decoded}\"\n')
            lines.append(decoded)

            del decoded
            del text_bytes
            del actual_len
            del prev_len
            del text_len
            continue
        del i

        if io_mdt.tell() < eof:  # last string isn't in the header table for w/e reason
            last_str_len = eof - io_mdt.tell()
            print(f'Found unlisted string at 0x{io_mdt.tell():04X}')
            text_bytes: bytes = io_mdt.read(last_str_len).replace(b'\x00', b'<NULL>')
            decoded: str = text_bytes.decode(encoding=JIS_ENCODING)
            print(f'Found \"{decoded}\"')
            lines.append(decoded)
            pass

        del _mdt
        pass

    if os.path.exists(fp_csv):
        mode_csv = 'w+'
        pass
    else:
        mode_csv = 'x'
        pass
    with open(fp_csv, mode=f'{mode_csv}t', encoding='utf-8', newline='') as io_csv:
        csv_writer = csv.writer(io_csv, quotechar='\"', quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(['jap', 'eng'])
        for i in lines:
            csv_writer.writerow([i, ''])
            continue
        del i
        del csv_writer
        pass
    del mode_csv
    del fp_csv
    del io_csv
    return


def read_mdt_files(dir_mdt: str, dir_csv: str):
    mdt_files: list[str] = []
    for i in glob.glob1(dir_mdt, '*.mdt'):
        mdt_files.append(os.path.join(dir_mdt, i))
        continue

    if os.path.exists(dir_csv) and not os.path.isdir(dir_csv):
        print(f'Selected CSV \"{dir_csv}\" is not a directory!')
        return
    elif not os.path.exists(dir_csv):
        print(f'Directory \"{dir_csv}\" does not existing. Making...')
        os.makedirs(dir_csv)
        print('Done making directory')
        pass

    for mdt_file in mdt_files:
        if os.path.sep in mdt_file:
            fp_csv = os.path.join(dir_csv, mdt_file[mdt_file.rindex(os.path.sep)+1:] + '.csv')
            pass
        else:
            raise RuntimeError('Something bad happened!')  # TODO IDK :shrug:
        print(f'Reading MDT file \"{mdt_file}\"...')
        read_mdt_file(mdt_file, fp_csv)
        print('Done read MDT file\n\n')
        continue
    return


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--mode', required=True, type=str.lower, choices=['dump', 'insert'])
    arg_parser.add_argument('--csv', required=True)
    arg_parser.add_argument('--mdt', required=True)
    args = arg_parser.parse_args()

    if args.mode == 'dump':
        if os.path.exists(args.mdt):
            if os.path.isdir(args.mdt):
                if os.path.exists(args.csv) and not os.path.isdir(args.csv):
                    print(f'Selected \"directory\" \"{args.csv}\" is not a directory like \"{args.mdt}\"!')
                    return
                read_mdt_files(args.mdt, args.csv)
                pass
            elif os.path.isfile(args.mdt):
                if os.path.exists(args.csv) and not os.path.isfile(args.csv):
                    print(f'Selected \"file\" \"{args.csv}\" is not a file like \"{args.mdt}\"!')
                    return
                read_mdt_file(args.mdt, args.csv)
                pass
            else:
                print(f'Selected mdt \"{args.mdt}\" is not a directory nor file?! This should not have happened!')
                pass
            pass
        else:
            print(f'Selected mdt \"{args.mdt}\" does not exist?!')
            pass
        pass
    elif args.mode == 'insert':
        if os.path.exists(args.csv):
            if os.path.isdir(args.csv):
                if os.path.exists(args.mdt) and not os.path.isdir(args.mdt):
                    print(f'Selected \"directory\" \"{args.mdt}\" is not a directory like \"{args.csv}\"!')
                    return
                write_mdt_files(args.csv, args.mdt)
                pass
            elif os.path.isfile(args.csv):
                if os.path.exists(args.mdt) and not os.path.isfile(args.mdt):
                    print(f'Selected \"file\" \"{args.mdt}\" is not a file like \"{args.csv}\"!')
                    return
                write_mdt_file(args.csv, args.mdt)
                pass
            else:
                print(f'Selected csv \"{args.csv}\" is not a directory nor file?! This should not have happened!')
                pass
            pass
        else:
            print(f'Selected csv \"{args.csv}\" does not exist?!')
            pass
        pass
    return


if __name__ == '__main__':
    main()
    pass
