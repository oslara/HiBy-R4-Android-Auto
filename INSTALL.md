# Installation Guide

This guide covers the **Android Auto enablement portion** of the project.

It assumes your HiBy R4 is already rooted with Magisk.

If your R4 is not rooted yet, stop here and read:

`docs/ROOTING.md`

Rooting the R4 involves Qualcomm EDL access and an actual boot-partition write. That is deliberately documented separately because it carries a much higher risk than installing the Android Auto module itself.

---

# Supported / Tested Configuration

Known-good test configuration:

- HiBy R4
- Firmware 1.80
- Android 12
- Magisk 30.7
- Android Auto 17.5.663214-release
- 2023 Nissan Rogue SV
- Wired Android Auto
- Wireless Android Auto through a third-party wireless AA adapter

Other firmware versions, Android Auto versions, vehicle manufacturers, and head units may also work but have not yet been verified.

---

# What This Installation Does

The HiBy R4 already contains the USB capability required to communicate with an Android Auto head unit.

The stock problem is that Android Auto is installed as a normal user application and therefore does not receive the privileged Android permission:

`android.permission.MANAGE_USB`

This project reproduces the factory-style Android Auto system-app architecture using a Magisk systemless overlay.

The module provides:

`/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk`

and:

`/product/etc/permissions/privapp-permissions-r4-androidauto.xml`

Android Auto can then be installed or updated normally through Google Play.

Android recognizes the Play Store version as an updated privileged system application and grants the permissions required for Android Auto USB projection.

---

# Requirements

You will need:

- Rooted HiBy R4
- Magisk installed and working
- Android SDK Platform-Tools / ADB
- A compatible `AndroidAutoStub.apk` extracted from a device you own
- This project's module files
- Google Play access on the R4
- A compatible Android Auto vehicle or head unit

Official Android Platform-Tools:

https://developer.android.com/tools/releases/platform-tools

Official Magisk project:

https://github.com/topjohnwu/Magisk

Android Auto:

https://www.android.com/auto/

---

# Step 1 — Obtain AndroidAutoStub.apk

This project does not redistribute Google's proprietary Android Auto stub.

You must obtain it yourself from a compatible Android Auto phone.

See:

`docs/ANDROID-AUTO-STUB.md`

The known-good reference stub used during development was extracted from a Samsung device.

Reference version:

`1.2.558700-stub`

Reference size:

`3,953,532 bytes`

Reference SHA-256:

`57EA6D176178E52FEDB8B351441141AEFAF8B6E98CFBED10A9FA1B006A608072`

A different stub may still work, but should be considered untested until verified.

---

# Step 2 — Build the Magisk Module

Place your extracted:

`AndroidAutoStub.apk`

into:

`module/system/product/priv-app/AndroidAutoStub/`

The final directory should contain:

`module/system/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk`

The module should also contain:

`module/module.prop`

and:

`module/system/product/etc/permissions/privapp-permissions-r4-androidauto.xml`

Use the project builder:

`tools/build-module.py`

The builder should:

- verify that `AndroidAutoStub.apk` exists
- calculate the APK SHA-256
- report whether it matches the known-good reference
- build the Magisk ZIP
- use POSIX `/` paths inside the archive
- verify the resulting archive structure

Do not use a ZIP tool that creates literal Windows `\` archive paths.

During development, this caused Magisk to extract invalid filenames instead of the intended directory hierarchy.

---

# Step 3 — Copy the Module to the R4

Connect the R4 to your computer with USB debugging enabled.

Confirm ADB sees the device:

```bat
adb devices
