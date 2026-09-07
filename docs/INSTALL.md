# Installation Guide

This guide covers the **Android Auto enablement portion** of the
project.

It assumes your HiBy R4 is already rooted with Magisk.

If your R4 is not rooted yet, stop here and read:

`docs/ROOTING.md`

Rooting the R4 involves Qualcomm EDL access and an actual boot-partition
write. That is deliberately documented separately because it carries a
much higher risk than installing the Android Auto module itself.

------------------------------------------------------------------------

# Supported / Tested Configuration

Known-good test configuration:

-   HiBy R4
-   Firmware 1.80
-   Android 12
-   Magisk 30.7
-   Android Auto 17.5.663214-release
-   2023 Nissan Rogue SV
-   Wired Android Auto
-   Wireless Android Auto through a third-party wireless AA adapter

Other firmware versions, Android Auto versions, vehicle manufacturers,
and head units may also work but have not yet been verified.

------------------------------------------------------------------------

# What This Installation Does

The HiBy R4 already contains the USB capability required to communicate
with an Android Auto head unit.

The stock problem is that Android Auto is installed as a normal user
application and therefore does not receive the privileged Android
permission:

`android.permission.MANAGE_USB`

This project reproduces the factory-style Android Auto system-app
architecture using a Magisk systemless overlay.

The module provides:

`/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk`

and:

`/product/etc/permissions/privapp-permissions-r4-androidauto.xml`

Android Auto can then be installed or updated normally through Google
Play.

Android recognizes the Play Store version as an updated privileged
system application and grants the permissions required for Android Auto
USB projection.

------------------------------------------------------------------------

# Requirements

You will need:

-   Rooted HiBy R4
-   Magisk installed and working
-   Android SDK Platform-Tools / ADB
-   A compatible `AndroidAutoStub.apk` extracted from a device you own
-   This project's module files
-   Google Play access on the R4
-   A compatible Android Auto vehicle or head unit

Official Android Platform-Tools:

https://developer.android.com/tools/releases/platform-tools

Official Magisk project:

https://github.com/topjohnwu/Magisk

Android Auto:

https://www.android.com/auto/

------------------------------------------------------------------------

# Step 1 --- Obtain AndroidAutoStub.apk

This project does not redistribute Google's proprietary Android Auto
stub.

You must obtain it yourself from a compatible Android Auto phone.

See:

`docs/ANDROID-AUTO-STUB.md`

The known-good reference stub used during development was extracted from
a Samsung device.

Reference version:

`1.2.558700-stub`

Reference size:

`3,953,532 bytes`

Reference SHA-256:

`57EA6D176178E52FEDB8B351441141AEFAF8B6E98CFBED10A9FA1B006A608072`

A different stub may still work, but should be considered untested until
verified.

------------------------------------------------------------------------

# Step 2 --- Build the Magisk Module

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

-   verify that `AndroidAutoStub.apk` exists
-   calculate the APK SHA-256
-   report whether it matches the known-good reference
-   build the Magisk ZIP
-   use POSIX `/` paths inside the archive
-   verify the resulting archive structure

Do not use a ZIP tool that creates literal Windows `\` archive paths.

During development, this caused Magisk to extract invalid filenames
instead of the intended directory hierarchy.

------------------------------------------------------------------------

# Step 3 --- Copy the Module to the R4

Connect the R4 to your computer with USB debugging enabled.

Confirm ADB sees the device:

``` bat
adb devices
```

Copy the generated module ZIP to the R4:

``` bat
adb push R4-AndroidAuto-Enabler-v1.1.zip /sdcard/Download/
```

This step only copies the ZIP to user storage.

It does not modify Android system partitions.

------------------------------------------------------------------------

# Step 4 --- Install the Module with Magisk

Install the module:

``` bat
adb shell su -c "magisk --install-module /sdcard/Download/R4-AndroidAuto-Enabler-v1.1.zip"
```

At this point, Magisk stages the module.

The systemless overlay does not become active until reboot.

Before rebooting, verify that the staged paths are correct.

``` bat
adb shell "su -c 'find /data/adb/modules_update/r4_androidauto_enabler -maxdepth 8 -type f'"
```

You should see normal Unix-style directory paths similar to:

``` text
/data/adb/modules_update/r4_androidauto_enabler/module.prop
/data/adb/modules_update/r4_androidauto_enabler/system/product/etc/permissions/privapp-permissions-r4-androidauto.xml
/data/adb/modules_update/r4_androidauto_enabler/system/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

If you see filenames containing literal backslashes such as:

``` text
system\product\priv-app\...
```

**DO NOT REBOOT.**

The module ZIP is malformed. Remove the staged module and rebuild it
correctly.

------------------------------------------------------------------------

# Step 5 --- Reboot to Activate

Reboot the R4 normally:

``` bat
adb reboot
```

The module becomes active during boot.

If the R4 boots normally, continue to verification.

If Android Recovery appears or Android reports that it cannot load the
system, **DO NOT factory reset.**

Read:

`docs/RECOVERY.md`

------------------------------------------------------------------------

# Step 6 --- Verify the Privileged Stub

After the R4 finishes booting:

``` bat
adb shell pm path com.google.android.projection.gearhead
```

Before the Play Store Android Auto update is installed, the package may
point directly to:

``` text
/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

Inspect the package:

``` bat
adb shell dumpsys package com.google.android.projection.gearhead > gearhead.txt
```

On the computer:

``` bat
findstr /I "versionName codePath SYSTEM PRIVILEGED PRODUCT MANAGE_USB" gearhead.txt
```

The package should show characteristics including:

-   `SYSTEM`
-   `PRIVILEGED`
-   `PRODUCT`
-   `android.permission.MANAGE_USB: granted=true`

If `MANAGE_USB` is not granted, stop and troubleshoot before connecting
to a vehicle.

------------------------------------------------------------------------

# Step 7 --- Install or Update Android Auto from Google Play

Open Google Play on the R4.

Install or update Android Auto normally.

Do not sideload a modified Android Auto APK for this procedure.

After installation/update:

``` bat
adb shell pm path com.google.android.projection.gearhead
```

The active package should now normally be under:

``` text
/data/app/...
```

while still inheriting its privileged system status from the underlying
product stub.

Inspect again:

``` bat
adb shell dumpsys package com.google.android.projection.gearhead > gearhead_after_update.txt
```

Then:

``` bat
findstr /I "versionName codePath SYSTEM UPDATED_SYSTEM_APP PRIVILEGED PRODUCT MANAGE_USB" gearhead_after_update.txt
```

Known-good behavior includes:

-   active `codePath=/data/app/...`
-   `SYSTEM`
-   `UPDATED_SYSTEM_APP`
-   `PRIVILEGED`
-   `PRODUCT`
-   `android.permission.MANAGE_USB: granted=true`

This is the desired state.

------------------------------------------------------------------------

# Step 8 --- Grant Runtime Permissions

Android Auto may require normal user/runtime permissions after the
stub/update reconciliation.

The R4 should normally prompt for these during Android Auto onboarding.

During development, the following permissions were granted:

-   Nearby Bluetooth access
-   Location
-   Microphone
-   Phone access

These are ordinary Android runtime permissions.

Exact requirements may vary by Android Auto version.

Do not attempt to manually grant privileged permissions such as:

`android.permission.MANAGE_USB`

with `pm grant`.

That permission is handled by the privileged system-app configuration.

------------------------------------------------------------------------

# Step 9 --- Connect to the Vehicle

Connect the R4 to the vehicle's Android Auto USB port.

The first session may involve:

-   Android Auto onboarding
-   vehicle approval prompts
-   runtime permission prompts
-   application setup
-   a disconnect/reconnect during initial setup

On the tested 2023 Nissan Rogue SV, Android Auto successfully launched
after permissions were approved and the R4 was reconnected.

The same R4 also worked through a third-party wireless Android Auto
adapter.

------------------------------------------------------------------------

# Known Issues

## Audio Starts Silent

Android Auto may connect and begin playback with no audible sound.

**Current workaround:** operate the volume control on the R4 once.

Audio immediately becomes active.

This is currently believed to be an audio-routing or initialization
issue. It does not appear to indicate Android Auto connection failure.

## Location / GPS

Google Maps launches, but usable location data is not currently
available on the tested R4.

The following have already been tested without resolving it:

-   location permission
-   precise location
-   Wi-Fi enabled
-   Android location assistance

The cause is not yet known.

The Android Auto module should not be modified solely to investigate
this issue. Location/GNSS is being treated as a separate research
problem.

------------------------------------------------------------------------

# Persistence

The known-good installation has been verified to survive a normal R4
reboot.

After reboot:

-   the Magisk module remained active
-   the product Android Auto stub remained present
-   the Play Store Android Auto package remained an updated system app
-   `PRIVILEGED` status remained present
-   `PRODUCT` status remained present
-   `MANAGE_USB` remained granted
-   normal runtime permissions remained granted

A future HiBy firmware update may replace the Magisk-patched boot image
and therefore disable root/module loading.

Do not assume this setup will survive a firmware OTA.

------------------------------------------------------------------------

# Do Not Flash the Project Author's Boot Image

The Android Auto module is intended to be reproducible.

The boot image is not.

Do not use another person's:

`boot_a.img`

`boot_b.img`

or Magisk-patched boot image.

Dump and patch your own firmware-matching boot image.

See:

`docs/ROOTING.md`

------------------------------------------------------------------------

# Verification

For the full post-install verification procedure, see:

`docs/VERIFY.md`

# Recovery

If the module causes a boot problem, do not immediately factory reset.

See:

`docs/RECOVERY.md`
