[README.md](https://github.com/user-attachments/files/31922541/README.md)
# HiBy R4 Android Auto

Native Android Auto projection on the HiBy R4 --- implemented with a
systemless Magisk overlay, a user-supplied compatible Android Auto
factory stub, and an R4-specific privileged-permission policy.

> **Status --- September 2026:** Working on the tested HiBy R4
> configuration with both wired Android Auto and a third-party wireless
> Android Auto adapter.

To the best of our knowledge, this is the first publicly documented
working implementation of native Android Auto projection on the HiBy R4.

**This is unofficial.** It is not an OEM-supported HiBy feature and this
project is not affiliated with HiBy, Google, Samsung, Nissan, or Magisk.

------------------------------------------------------------------------

## What works

Tested successfully:

-   Android Auto projection on a **HiBy R4**
-   **Wired USB** connection
-   **Wireless Android Auto through a third-party AA adapter**
-   Vehicle: **2023 Nissan Rogue SV**
-   Google Play Android Auto update
-   Media playback
-   **Poweramp**
-   Normal reboot persistence
-   Android Auto retains:
    -   `SYSTEM`
    -   `UPDATED_SYSTEM_APP`
    -   `PRIVILEGED`
    -   `PRODUCT`
    -   `android.permission.MANAGE_USB`

This is the actual Google Android Auto / Gearhead projection stack.

It is **not** USB audio mirroring, a fake head-unit interface, or simply
Bluetooth playback.

------------------------------------------------------------------------

## Known limitations

### GPS / location

Location is currently **not working correctly** on the tested R4.

Google Maps launches, but positioning is wildly incorrect. Location
permissions, precise location, Wi-Fi, and Android location assistance
did not resolve it.

The cause has not yet been proven. Possible investigation areas include
GNSS hardware, the GNSS HAL/provider, HiBy firmware configuration, and
Android location-framework integration.

This is being treated as a separate subsystem issue. The known-good
Android Auto privilege module should **not** be modified merely to chase
GPS.

### Audio may initially be silent

Android Auto can occasionally connect and begin playback with no audible
output.

On the tested R4, touching/operating the R4 volume control once causes
audio to become audible immediately.

The exact cause is not yet proven.

------------------------------------------------------------------------

# Read this before doing anything

This project involves rooting an Android device.

The Android Auto module itself uses a **systemless Magisk overlay** and
does not physically rewrite `/system` or `/product`.

However, obtaining Magisk root on the tested R4 required modifying the
device's boot environment. That part can involve an **actual partition
write** and can brick the device if performed incorrectly.

Do not blindly copy commands, boot images, partition names, slot
assumptions, or Qualcomm programmers from another person's device.

**Never flash another user's boot image.**

Start here:

-   [Installation](docs/INSTALL.md)
-   [Rooting and boot-image safety](docs/ROOTING.md)
-   [Recovery](docs/RECOVERY.md)

If you are not comfortable verifying your own firmware, active slot,
boot image, hashes, and recovery path, stop before the partition-write
stage.

------------------------------------------------------------------------

# Tested configuration

  Component                Tested value
  ------------------------ --------------------------------------------
  Device                   HiBy R4
  Firmware                 1.80
  Android                  Android 12 / API 31
  Root                     Magisk 30.7
  Android Auto             17.5.663214-release
  Factory stub reference   1.2.558700-stub
  Vehicle                  2023 Nissan Rogue SV
  Wired AA                 Working
  Wireless AA adapter      Working
  Poweramp                 Working
  Reboot persistence       Verified
  GPS/location             Not working correctly
  Audio startup            May require one volume-control interaction

Other firmware, Android Auto releases, donor stubs, vehicles, and
wireless adapters may behave differently.

------------------------------------------------------------------------

# The short version: why this works

Android Auto from Google Play could already be installed on the R4.

That was not enough.

On a stock R4, Gearhead was an ordinary `/data/app` application. When
connected to the Nissan, Android Open Accessory negotiation actually
began successfully, but Android Auto failed with:

``` text
NO_MANAGE_USB_PERMISSION_ERROR(22)
```

The missing permission was:

``` text
android.permission.MANAGE_USB
```

That is a privileged permission. It cannot simply be fixed with a normal
runtime `pm grant`.

A Samsung Android device provided the architectural clue: it ships a
factory Android Auto stub under `/product/priv-app`, while the current
Google Play Android Auto package runs as an **updated privileged system
app**.

This project recreates that package architecture on the R4
**systemlessly**:

``` text
Magisk
  ↓
/product/priv-app/AndroidAutoStub
  +
/product/etc/permissions/ R4 Gearhead policy
  ↓
PackageManager
  ↓
SYSTEM + PRIVILEGED + PRODUCT
  ↓
Google Play Android Auto update
  ↓
UPDATED_SYSTEM_APP
  ↓
MANAGE_USB granted
  ↓
Android Auto projection
```

For the full investigation:

[Technical Notes / How It Works](docs/TECHNICAL.md)

------------------------------------------------------------------------

# Installation path

The intended reproduction path is:

``` text
1. Read ROOTING.md
2. Root your own R4 safely
3. Extract your own compatible AndroidAutoStub.apk
4. Put it into the module source tree
5. Run the local module builder
6. Inspect the generated ZIP
7. Install/stage it with Magisk
8. Verify the staged module BEFORE rebooting
9. Reboot
10. Verify privileged package state
11. Update Android Auto through Google Play
12. Verify UPDATED_SYSTEM_APP + MANAGE_USB
13. Connect to the vehicle
```

Detailed instructions:

[INSTALL.md](docs/INSTALL.md)

------------------------------------------------------------------------

# Documentation

  ---------------------------------------------------------------------------------------
  Document                                            Purpose
  --------------------------------------------------- -----------------------------------
  [INSTALL.md](docs/INSTALL.md)                       Complete installation workflow

  [ROOTING.md](docs/ROOTING.md)                       Rooting, boot-image safety, EDL
                                                      context, and risk boundaries

  [ANDROID-AUTO-STUB.md](docs/ANDROID-AUTO-STUB.md)   Extracting and checking your own
                                                      compatible factory stub

  [VERIFY.md](docs/VERIFY.md)                         Confirming package flags,
                                                      permissions, module state, and
                                                      persistence

  [RECOVERY.md](docs/RECOVERY.md)                     Recovering from bad module
                                                      activation and related failures

  [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)       Symptom-based troubleshooting

  [TECHNICAL.md](docs/TECHNICAL.md)                   Investigation history and technical
                                                      architecture
  ---------------------------------------------------------------------------------------

------------------------------------------------------------------------

# Repository structure

``` text
HiBy-R4-Android-Auto/
├── README.md
├── LICENSE
├── docs/
│   ├── INSTALL.md
│   ├── ROOTING.md
│   ├── ANDROID-AUTO-STUB.md
│   ├── VERIFY.md
│   ├── RECOVERY.md
│   ├── TROUBLESHOOTING.md
│   └── TECHNICAL.md
├── module/
│   ├── module.prop
│   └── system/
│       └── product/
│           ├── etc/
│           │   └── permissions/
│           │       └── privapp-permissions-r4-androidauto.xml
│           └── priv-app/
│               └── AndroidAutoStub/
│                   └── PUT_ANDROID_AUTO_STUB_HERE.txt
└── tools/
    └── build-module.py
```

------------------------------------------------------------------------

# Proprietary binaries are not included

This repository intentionally does **not** distribute:

-   `AndroidAutoStub.apk`
-   Google Play Android Auto APKs/splits
-   stock HiBy boot images
-   Magisk-patched boot images
-   proprietary Qualcomm programmer binaries as project payloads

Users must obtain/extract the binaries they are legally entitled to use.

> **We provide the implementation, not somebody else's proprietary
> binaries.**

In particular, do **not** open a GitHub issue asking for somebody else's
patched boot image.

------------------------------------------------------------------------

# AndroidAutoStub reference

The exact factory stub used during successful development was:

``` text
Package:
com.google.android.projection.gearhead

Version:
1.2.558700-stub

Version code:
12558700

Size:
3,953,532 bytes

SHA-256:
57ea6d176178e52fedb8b351441141aefaf8b6e98cfbed10a9fa1b006a608072
```

A different hash does **not automatically mean the APK is bad**.

It means:

``` text
UNTESTED STUB VERSION
```

The included builder reports this distinction instead of pretending one
binary must remain the only compatible stub forever.

See:

[ANDROID-AUTO-STUB.md](docs/ANDROID-AUTO-STUB.md)

------------------------------------------------------------------------

# Building the Magisk module

After extracting your own `AndroidAutoStub.apk`, place it at:

``` text
module/system/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

From the repository root, run:

``` text
python tools/build-module.py
```

The builder:

-   requires the user-supplied stub;
-   calculates its SHA-256;
-   compares it with the known-good development reference;
-   warns rather than rejects an untested stub version;
-   builds the Magisk ZIP locally;
-   forces POSIX `/` archive paths;
-   rejects ZIP entries containing Windows `\` path separators;
-   verifies the expected module files exist in the finished archive.

Output:

``` text
dist/R4-AndroidAuto-Enabler-v1.1.zip
```

The Windows path check exists for a reason: an early development ZIP
stored literal backslashes and Magisk extracted the tree incorrectly. It
was caught before reboot.

------------------------------------------------------------------------

# Known-good privileged policy

The v1.1 R4 policy grants the privileged permissions required by the
tested package configuration while explicitly denying:

``` text
android.permission.BIND_APPWIDGET
android.permission.SEND_SMS
```

The tested core Android Auto projection/media functionality works
without those two permissions.

The policy source is included here:

[module/system/product/etc/permissions/privapp-permissions-r4-androidauto.xml](module/system/product/etc/permissions/privapp-permissions-r4-androidauto.xml)

Do not assume that granting *more* privileged permissions is
automatically better.

------------------------------------------------------------------------

# Verification target

After the factory stub is recognized, the package should show
system/product privileged state.

After the Google Play update, the active package may correctly live
under:

``` text
/data/app/...
```

That is expected.

The important state is:

``` text
SYSTEM
UPDATED_SYSTEM_APP
PRIVILEGED
PRODUCT
MANAGE_USB = granted
```

The underlying system stub should remain available through:

``` text
/product/priv-app/AndroidAutoStub
```

See:

[VERIFY.md](docs/VERIFY.md)

------------------------------------------------------------------------

# Recovery philosophy

If Android Auto fails, do not immediately escalate to partition writes.

A useful boundary is:

``` text
app problem
≠
permission problem
≠
module problem
≠
boot problem
≠
partition problem
```

During development, an early module caused the R4 to enter Android
Recovery. The device was recovered **without factory reset**.

If a module activation goes wrong:

**Do not immediately factory reset.**

Read:

[RECOVERY.md](docs/RECOVERY.md)

------------------------------------------------------------------------

# OTA warning

A HiBy firmware OTA may replace the Magisk-patched boot image.

If root disappears, the systemless Android Auto module will no longer
mount and the privileged package relationship may disappear with it.

Do not blindly flash a boot image patched from an older firmware onto a
newer firmware.

Dump and patch the boot image that belongs to the firmware actually
installed on your device.

Google Play Android Auto updates are different: the design intentionally
uses Android's updated-system-app behavior, although future releases can
always introduce new compatibility changes.

------------------------------------------------------------------------

# Reporting problems

Before opening an issue, please read:

[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

Useful reports include:

``` text
R4 firmware
Android Auto version
Magisk version
stub version/hash
whether root still works
whether the module is mounted
pm path output
SYSTEM / UPDATED_SYSTEM_APP state
PRIVILEGED / PRODUCT state
MANAGE_USB state
wired or wireless test
vehicle/head-unit model
exact observed symptom/error
```

Please remove serial numbers, account information, and other personal
identifiers before posting logs publicly.

------------------------------------------------------------------------

# Project scope

This project currently proves one specific result:

> A rooted HiBy R4 running firmware 1.80 can be configured systemlessly
> so Google's Android Auto package receives the privileged package state
> required for native Android Auto projection, and that implementation
> has been successfully tested in a 2023 Nissan Rogue SV over wired USB
> and through a third-party wireless Android Auto adapter.

It does **not** claim:

-   official HiBy support;
-   universal vehicle compatibility;
-   universal firmware compatibility;
-   working GPS on the R4;
-   compatibility with every donor stub;
-   compatibility with every future Android Auto version;
-   that rooting or EDL work is risk-free.

------------------------------------------------------------------------

# Credits

This project builds on work and knowledge from multiple communities and
upstream projects, including Android platform behavior, Magisk,
Qualcomm/EDL research, HiBy R4 modding research, and community findings.

Special project credits:

**Oscar Lara** --- hardware work, testing, reverse-engineering workflow,
recovery testing, vehicle validation, wireless validation, and
persistence testing.

**Lyra / ChatGPT** --- research synthesis, diagnostics, architecture
analysis, module design collaboration, tooling, and documentation.

No affiliation with HiBy, Google, Samsung, Nissan, or Magisk is implied.

------------------------------------------------------------------------

# License

Project-authored code and documentation are provided under the
repository's [LICENSE](LICENSE).

Third-party and proprietary binaries are not covered by that license and
are not distributed by this repository.

------------------------------------------------------------------------

*A small step for an audiophile and an AI; a giant leap for DAPkind.*

**Oscar Lara + Lyra / ChatGPT --- September 2026**
