# Vendor ramdisk touch tools

Move one known-working touchscreen firmware file from an older **same-hardware** build into a copy of the current `vendor_boot`. Use this when boot logs show that the driver loads an incompatible firmware file from the **early vendor ramdisk**. A touchscreen that stopped working after an update is not, by itself, enough evidence to use this method.

**Start here:** [Galaxy S21 Ultra SM-G998B: worked example, commands and reference hashes](examples/SM-G998B.md).

## Samsung Galaxy touchscreen not working after a One UI update?

[Find your model in the sourced touchscreen report index](docs/galaxy-touchscreen-after-update.md). It covers Galaxy S21, S21+, S21 Ultra and S21 FE, plus reports for S22 Ultra, S23, S23 Ultra, Galaxy A-series and selected M-series, Z Fold and Z Flip devices. The index distinguishes loss of finger touch, S Pen-only input and intermittent or charging-only symptoms. **Only the SM-G998B/HZA6 release has a physical repair test here.**

## License

Copyright © 2026 Majed-allababedi. The project's original code and documentation are licensed under Ojuba's **Waqf General Public License 2.0**. The [Arabic original](LICENSE) is authoritative; the [English translation](LICENSE.en.txt) is provided for convenience. Both texts come from [Ojuba's license repository](https://github.com/ojuba-org/waqf/tree/fda6cd52912125e05162316edc305567fbdb7c97/2.0).

This change does not revoke MIT permissions already granted for earlier copies. Third-party dependencies and Samsung firmware, including firmware in release assets, are not relicensed by this project.

## What is portable?

The Python CLI has no model table, controller address, panel filename or per-device offset. It reads the header and archive entries, then uses the exact firmware path and hashes you supply. **Format support is not universal device support.** Only the SM-G998B case below was physically tested. Matching filenames alone do not establish controller compatibility.

| Input or layout | Support |
|---|---|
| Raw `vendor_boot.img`, a single standard LZ4 frame, or an uncompressed AP `.tar` / `.tar.md5` with one root `vendor_boot.img[.lz4]` | Yes |
| Android vendor boot header v3, one gzip ramdisk, one `070701` newc CPIO, single-link regular `.bin` under a `firmware` directory | Yes, if geometry and size checks pass |
| v4 fragment tables, other ramdisk codecs, firmware in `super` / vendor modules rather than the early ramdisk | Not implemented; do not rename or force an input |
| Hardware identification, flashing, signing, locked-boot support | Not provided |

The tool operates on trusted local stock packages, not a USB device. Inputs are never overwritten. Keep a known-good recovery package: modifying `vendor_boot` invalidates its original signed digest. **Do not relock a bootloader with a modified image installed.** No proprietary firmware files are distributed here.

## Install and inspect

Use Python 3.11+ on the workstation, preferably in a virtual environment:

```sh
python -m pip install -r requirements.txt
python -m unittest -v
python vendor_touch.py --help
```

Obtain the current and older stock inputs for the **same model, board and touchscreen controller**. First identify the firmware requested by the failing touch driver from existing diagnostic logs or reliable device documentation. Then inventory both images. The first column is the SHA-256 of the **uncompressed member**, not of the AP, TAR or raw partition.

```sh
python vendor_touch.py list current.img
python vendor_touch.py list known-working.img
```

## Extract or build

The following is a command template: substitute the exact path listed for your controller, input files and two full member hashes. `--expect-base` is the current file; `--expect-donor` is the working replacement. The tool does not choose an older binary just because its name matches.

```sh
python vendor_touch.py extract known-working.img vendor/firmware/PANEL.bin extracted.bin
python vendor_touch.py build current.img vendor/firmware/PANEL.bin patched.img --donor known-working.img --expect-base CURRENT_MEMBER_SHA256 --expect-donor DONOR_MEMBER_SHA256
```

Extraction is optional. `build` independently reads the member from the donor image or AP. Choose a fresh `.img` output for a raw partition image or `.tar` for a one-member `vendor_boot.img.lz4` archive. The printed build digest is always for the raw image, not the TAR. Existing output files are refused.

## How the replacement works

1. Read the base and donor separately. In an AP, read only `vendor_boot.img[.lz4]`; never substitute the entire older partition. Decode the outer LZ4 if present. Read page size and compressed ramdisk length from the `VNDRBOOT` header.
2. Decompress the inner gzip. Traverse CPIO by the encoded name and payload lengths and four-byte alignment, rather than scanning for a version string. Select one regular file by exact path and verify both expected hashes.
3. Replace the complete base file payload. Adjust its eight-character ASCII-hex CPIO size and padding, recompress, then update the binary little-endian ramdisk length in the image header. The new stream must end in the **same aligned page extent**; otherwise the tool refuses instead of moving the DTB or partition tail.
4. Reopen the result, compare the CPIO namespace, replacement payload, and all other entries against the base. Read back the saved image/TAR and compare its raw partition bytes to the verified image. These checks establish file correctness, **not** a successful hardware boot.

## Evaluating another model

Before treating a second device as supported, record the exact variant and both builds, the failure and success probe logs, the requested firmware path, both member hashes and the resulting image hash. Verify first-probe success and finger input after a fresh boot without a late rebind. Share redacted observations, not serial numbers, personal logs or vendor binaries.

**Background:** [AOSP vendor boot partitions](https://source.android.com/docs/core/architecture/partitions/vendor-boot-partitions) · [XDA discussion of the earlier root/rebind workaround](https://xdaforums.com/t/solved-with-root-one-ui-6-1-touchscreen-not-working-issue.4679358/). The offline early-ramdisk replacement documented here is distinct from the runtime workaround.