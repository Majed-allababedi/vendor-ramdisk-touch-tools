"""Offline firmware member inventory, extraction and layout-preserving replacement."""
import argparse
import gzip
import hashlib
import io
from pathlib import Path
import stat
import struct
import tarfile
import zlib

import lz4.frame as lz4

LIMIT = 256 << 20
MEMBERS = {'vendor_boot.img', 'vendor_boot.img.lz4'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def align(n, k):
    return (n + k - 1) // k * k


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, data):
    with path.open('xb') as f:
        f.write(data)
    require(path.read_bytes() == data, 'output readback mismatch')


def read_image(path):
    if path.name.endswith(('.tar', '.tar.md5')):
        with tarfile.open(path, 'r:') as t:
            hits = [m for m in t if m.name in MEMBERS]
            require(len(hits) == 1 and hits[0].isreg() and 0 < hits[0].size <= LIMIT,
                    'need one regular, bounded vendor_boot member at TAR root')
            b = t.extractfile(hits[0]).read()
    else:
        require(path.is_file() and path.stat().st_size <= LIMIT, 'invalid input size')
        b = path.read_bytes()
    if b.startswith(b'\x04\x22\x4d\x18'):
        dec = lz4.LZ4FrameDecompressor()
        b = dec.decompress(b, max_length=LIMIT + 1)
        require(len(b) <= LIMIT and dec.eof and not dec.unused_data, 'unsupported/oversize LZ4 frame')
    return b


def unpack(img):
    require(len(img) >= 2112 and img[:8] == b'VNDRBOOT', 'not a vendor boot image')
    version, page = struct.unpack_from('<II', img, 8)
    require(version == 3 and 2048 <= page <= 65536 and not page & (page - 1),
            'requires a v3 header and a supported power-of-two page size')
    header, dtb = struct.unpack_from('<II', img, 2096)
    require(header == 2112, 'unexpected header size')
    start = align(header, page)
    length, = struct.unpack_from('<I', img, 24)
    end = start + align(length, page)
    require(length and end + dtb <= len(img) and not any(img[start+length:end]), 'invalid layout/padding')
    dec = zlib.decompressobj(31)
    r = dec.decompress(img[start:start+length], LIMIT+1)
    require(len(r) <= LIMIT and dec.eof and not dec.unused_data, 'requires one bounded gzip stream')
    return page, start, end, r


def inventory(r):
    entries = {}
    i = 0
    while True:
        h = i
        require(r[h:h+6] == b'070701' and h+110 <= len(r), 'not a complete newc CPIO header')
        fields = r[h+6:h+110]
        require(all(v in b'0123456789abcdefABCDEF' for v in fields), 'invalid newc hex field')
        mode, links, size, namesize = [int(fields[j*8:j*8+8],16) for j in (1,4,6,11)]
        k = h+110+namesize
        require(0 < namesize <= 4096 and k <= len(r) and r[k-1] == 0, 'invalid name')
        path = r[h+110:k-1].decode('utf-8')
        require(path and '\x00' not in path and path not in entries, 'empty/duplicate/invalid name')
        d = align(k,4); i = align(d+size,4)
        require(i <= len(r) and not any(r[k:d]) and not any(r[d+size:i]), 'bad extent or padding')
        entries[path] = (h,d,size,mode,links)
        if path == 'TRAILER!!!':
            require(size == 0 and not any(r[i:]), 'multiple archives or nonzero trailing data')
            return entries


def select(r, path):
    parts = path.split('/')
    require('firmware' in parts[:-1] and path.endswith('.bin') and '\\' not in path
            and not set(parts) & {'', '.', '..'}, 'select an exact relative firmware/*.bin path')
    row = inventory(r).get(path)
    require(row and stat.S_ISREG(row[3]) and row[4] == 1 and row[2] > 0,
            'member absent, empty, not regular, or hard-linked')
    return row[:3]


def payload(img, path):
    r = unpack(img)[3]
    _, d, size = select(r, path)
    return r[d:d+size]


def replace(img, path, donor):
    page, start, end, r = unpack(img)
    h, d, s = select(r, path)
    require(donor and r[d:d+s] != donor, 'empty or identical donor payload')
    # CPIO sizes are ASCII hex, whereas vendor_boot lengths are binary LE.
    new = (r[:h+54] + f'{len(donor):08x}'.encode() + r[h+62:d] + donor
           + bytes(-len(donor) % 4) + r[align(d+s,4):])
    new += bytes(-len(new) % 512)
    z = gzip.compress(new, compresslevel=6, mtime=0)
    require(align(len(z),page) == end-start, 'recompression shifts later sections; refusing')
    result = img[:24] + struct.pack('<I',len(z)) + img[28:start] + z + bytes(end-start-len(z)) + img[end:]
    got = unpack(result)[3]
    require(got == new and payload(result,path) == donor and len(result) == len(img), 'image verification failed')
    a, b = inventory(r), inventory(got)
    require(list(a) == list(b), 'namespace changed')
    for key in a.keys() - {path}:
        h0,d0,s0,*_ = a[key]; h1,d1,s1,*_ = b[key]
        require(r[h0:d0+s0] == got[h1:d1+s1], 'unselected entry changed')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    cmds = parser.add_subparsers(dest='action', required=True)
    for action in ('list','extract','build'):
        c = cmds.add_parser(action)
        c.add_argument('image', type=Path, help='base AP TAR, raw image, or LZ4 frame')
        if action != 'list':
            c.add_argument('member'); c.add_argument('output', type=Path)
        if action == 'build':
            c.add_argument('--donor', type=Path, required=True, help='known-working AP/image for same hardware')
            c.add_argument('--expect-base', required=True, help='SHA-256 of current member')
            c.add_argument('--expect-donor', required=True, help='SHA-256 of working member')
    args = parser.parse_args()
    try:
        img = read_image(args.image)
        if args.action == 'list':
            r = unpack(img)[3]
            for path, (_,d,s,mode,links) in inventory(r).items():
                if stat.S_ISREG(mode) and links == 1 and 'firmware' in path.split('/')[:-1] and path.endswith('.bin'):
                    print(sha(r[d:d+s]), s, ascii(path))
            return
        current = payload(img,args.member)
        if args.action == 'extract':
            save(args.output,current); print(sha(current), args.output); return
        donor = payload(read_image(args.donor), args.member)
        require(sha(current) == args.expect_base.lower() and sha(donor) == args.expect_donor.lower(),
                'member hash mismatch; check inputs and order')
        result = replace(img,args.member,donor)
        require(args.output.suffix in ('.img','.tar'), 'output must end in .img or .tar')
        if args.output.suffix == '.tar':
            buf = io.BytesIO()
            with tarfile.open(fileobj=buf,mode='w:',format=tarfile.USTAR_FORMAT) as t:
                enc = lz4.compress(result,block_size=lz4.BLOCKSIZE_MAX1MB,block_linked=False,content_checksum=True)
                m = tarfile.TarInfo('vendor_boot.img.lz4'); m.size = len(enc); t.addfile(m,io.BytesIO(enc))
            save(args.output,buf.getvalue())
        else:
            save(args.output,result)
        require(read_image(args.output) == result,'package readback mismatch')
        print('Raw image SHA-256:',sha(result)); print('Saved:',args.output)
    except (OSError, ValueError, RuntimeError, zlib.error, tarfile.TarError) as exc:
        parser.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
