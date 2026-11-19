"""Generated fixtures only; no vendor files needed."""
import gzip
import struct
import tempfile
import unittest
from pathlib import Path

import vendor_touch as vt


PATH = 'vendor/firmware/panel-x.bin'


def pad(b, n):
    return b + bytes(-len(b) % n)


def entry(name, data, mode=0o100644):
    name = name.encode() + b'\0'
    fields = [1, mode, 0, 0, 1, 0, len(data), 0, 0, 0, 0, len(name), 0]
    return pad(b'070701' + ''.join(f'{i:08x}' for i in fields).encode() + name, 4) + pad(data, 4)


def image(payload, page=8192, extra=b''):
    r = entry(PATH, payload) + extra + entry('elsewhere', b'unchanged') + entry('TRAILER!!!', b'', 0)
    z = gzip.compress(pad(r, 512), mtime=0)
    h = bytearray(page)
    h[:8] = b'VNDRBOOT'
    struct.pack_into('<II', h, 8, 3, page)
    struct.pack_into('<I', h, 24, len(z))
    struct.pack_into('<II', h, 2096, 2112, 8)
    return bytes(h) + pad(z, page) + b'DTB-test' + bytes(page-8) + b'partition-tail'


class Tests(unittest.TestCase):
    def test_roundtrip(self):
        b = image(b'new'); result = vt.replace(b, PATH, b'older')
        self.assertEqual(vt.payload(result, PATH), b'older')
        self.assertEqual(b[16384:], result[16384:])
        self.assertEqual(len(result), len(b))

    def test_duplicate(self):
        with self.assertRaises(ValueError):
            vt.payload(image(b'a', extra=entry(PATH, b'b')), PATH)

    def test_v4_refused(self):
        b = bytearray(image(b'a')); b[8] = 4
        with self.assertRaises(ValueError):
            vt.payload(bytes(b), PATH)

    def test_missing(self):
        with self.assertRaises(ValueError):
            vt.payload(image(b'a'), 'vendor/firmware/other.bin')

    def test_symlink_refused(self):
        with self.assertRaises(ValueError):
            vt.payload(image(b'a', extra=entry('vendor/firmware/link.bin', b'target', 0o120777)), 'vendor/firmware/link.bin')

    def test_capacity(self):
        import random
        with self.assertRaises(ValueError):
            vt.replace(image(b'a'), PATH, random.Random(0).randbytes(32768))

    def test_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'original'; p.write_bytes(b'original')
            with self.assertRaises(FileExistsError):
                vt.save(p, b'new')
            self.assertEqual(p.read_bytes(), b'original')


if __name__ == '__main__':
    unittest.main()
