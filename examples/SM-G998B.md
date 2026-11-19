# Worked example: Galaxy S21 Ultra, SM-G998B (EGY)

| Role | Build | Early firmware |
|---|---|---|
| Current system / image to modify | `G998BXXSJHZA6` (Android 15) | `28.20.1.26`, 215,824 bytes |
| Donor of one file | `G998BXXSAFXCO` (Android 14) | `28.20.1.25`, 215,568 bytes |

Both archives contained `vendor/firmware/y792_p3.bin` in the gzip ramdisk inside `vendor_boot.img`. On this unit, `slsi_ts` at `6-0048` tried three times to enter firmware update mode with `.26`, then failed hardware initialization. A late rebind using `.25` worked. The goal was to make that working file available at the **first** probe. This observation does not identify the cause of the controller's refusal or prove anything about screen authenticity.

## Reproduce from the original APs

In PowerShell, run from the repository directory. Copy the two local stock AP archives there under the example names below, or set `$base` and `$donor` to their actual paths. Extract AP archives from any outer download ZIP first. Do not commit firmware to Git.

```powershell
$base  = 'AP_HZA6.tar.md5'
$donor = 'AP_FXCO.tar.md5'
$member = 'vendor/firmware/y792_p3.bin'
$baseHash  = '3ea249c913b18990d8bd831f9d7c24de9fb031b9c186bbdd27ea4b8668e8a027'
$donorHash = '968592bef9e5728c9fde5aacf07e3aed11ad75e5de4cfd32638805ce04358b16'
python vendor_touch.py list $base
python vendor_touch.py list $donor
python vendor_touch.py extract $donor $member y792_p3.bin
python vendor_touch.py build $base $member HZA6_touch25.tar --donor $donor --expect-base $baseHash --expect-donor $donorHash
```

With Python 3.11.15, zlib 1.3.1 and lz4 4.4.5, the public CLI reproduced the previously tested raw partition image. Both stock and modified raw images were 67,108,864 bytes. These are **raw image** hashes; do not compare them to the TAR hash:

| Image | SHA-256 |
|---|---|
| Stock HZA6 | `0275af71e5dcc18f177b67764f4acde65c2f916be0ca48545b2d88793c363c2b` |
| HZA6 with FXCO touch firmware | `93043e6679969cdf277e782cc5c789ddf54c1bd4cfb7f00078fc84b875c9151b` |

## Evidence and limits

The modified image's first probe selected `.25`, skipped the controller firmware update, and completed at about 2.91 seconds. A later reboot with the startup script disabled also completed its first probe. After Magisk removal, Android registered `sec_touchscreen` and the owner confirmed finger input. This was **root-free, not stock-signed**: the bootloader was unlocked. No other variant or build is certified by this example. Keep the original HZA6 AP for recovery; restoring it restores `.26` too.
