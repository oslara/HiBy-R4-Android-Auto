# Verification Guide

Use this guide after installing the HiBy R4 Android Auto module.

The goal is simple: **prove that Android Auto is in the expected
privileged state before treating the installation as successful.**

> **Safety classification: 🟢 READ-ONLY**
>
> The commands in this guide inspect Android package state and save
> diagnostic text to the computer. They do not flash partitions, modify
> the Magisk module, or grant privileged permissions.

------------------------------------------------------------------------

# Known-Good State

The successfully tested R4 used:

``` text
HiBy R4 firmware: 1.80
Android: 12 / API 31
Magisk: 30.7
Android Auto: 17.5.663214-release
Android Auto versionCode: 175663214
```

After the Google Play update, Android Auto was expected to be:

``` text
SYSTEM
UPDATED_SYSTEM_APP
PRIVILEGED
PRODUCT
MANAGE_USB granted
```

The underlying systemless factory-style stub remained present under:

``` text
/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

while the active updated Android Auto package ran from:

``` text
/data/app/...
```

That combination is intentional.

------------------------------------------------------------------------

# 1. Confirm the R4 Booted Normally

**Risk: 🟢 READ-ONLY**

Connect the R4 to the computer and run:

``` bat
adb devices
```

The device should appear as authorized.

If the R4 is sitting in Android Recovery or repeatedly rebooting, do not
continue with normal verification.

See:

`RECOVERY.md`

------------------------------------------------------------------------

# 2. Confirm Magisk Root Still Works

**Risk: 🟢 READ-ONLY**

Run:

``` bat
adb shell su -c id
```

A working rooted shell should report UID 0.

The known-good development R4 included:

``` text
uid=0
context=u:r:magisk:s0
```

If `su` no longer works after a firmware update, the patched boot image
may have been replaced and the Android Auto module may therefore not be
active.

Do not reinstall or flash anything until you determine why root
disappeared.

------------------------------------------------------------------------

# 3. Confirm the Magisk Module Is Present

**Risk: 🟢 READ-ONLY**

Run:

``` bat
adb shell "su -c 'ls -la /data/adb/modules/r4_androidauto_enabler'"
```

You should see the installed module directory.

Then inspect its files:

``` bat
adb shell "su -c 'find /data/adb/modules/r4_androidauto_enabler -maxdepth 8 -type f'"
```

Expected important files include:

``` text
/data/adb/modules/r4_androidauto_enabler/module.prop
/data/adb/modules/r4_androidauto_enabler/system/product/etc/permissions/privapp-permissions-r4-androidauto.xml
/data/adb/modules/r4_androidauto_enabler/system/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

If the module is missing or disabled, stop and investigate before
testing Android Auto.

------------------------------------------------------------------------

# 4. Confirm the Systemless Stub Is Visible

**Risk: 🟢 READ-ONLY**

Check the expected product path:

``` bat
adb shell ls -l /product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

The file should exist.

You can also query Android's package manager:

``` bat
adb shell pm path com.google.android.projection.gearhead
```

There are two important states depending on whether the Google Play
update has been installed.

## Before the Google Play Update

The package path may point directly to:

``` text
/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

## After the Google Play Update

The active package should normally point to one or more files under:

``` text
/data/app/...
```

For example:

``` text
package:/data/app/.../base.apk
package:/data/app/.../split_config.arm64_v8a.apk
package:/data/app/.../split_config.en.apk
package:/data/app/.../split_config.xhdpi.apk
```

Seeing `/data/app` after the update is **not a failure**.

The important question is whether Android still recognizes that update
as an updated privileged system/product application.

------------------------------------------------------------------------

# 5. Save a Full Android Auto Package Dump

**Risk: 🟢 READ-ONLY**

In Windows CMD:

``` bat
adb shell dumpsys package com.google.android.projection.gearhead > gearhead_verify.txt
```

This creates a local diagnostic file on the computer.

Do not paste example output back into CMD as though it were a command.

Now extract the most useful fields:

``` bat
findstr /I "codePath versionCode versionName SYSTEM UPDATED_SYSTEM_APP PRIVILEGED PRODUCT MANAGE_USB" gearhead_verify.txt
```

------------------------------------------------------------------------

# 6. Verify the Active Android Auto Version

For the known-good development installation, the Play Store version was:

``` text
versionCode=175663214
versionName=17.5.663214-release
```

Your Android Auto version may be newer.

A newer version is not automatically a problem.

The important architectural state is:

``` text
updated Play Store package
+
underlying privileged product stub
+
privileged permission policy
```

If a newer Android Auto release preserves that state and Android Auto
works, document it as a newly tested version.

------------------------------------------------------------------------

# 7. Verify SYSTEM / UPDATED_SYSTEM_APP

After the Play Store update, the package should identify as a system app
and an updated system app.

Look for package flags containing:

``` text
SYSTEM
UPDATED_SYSTEM_APP
```

The known-good development state included both.

If Android Auto exists only as an ordinary user application with no
system/update relationship, the factory-style stub architecture has not
been established correctly.

Stop before vehicle testing.

------------------------------------------------------------------------

# 8. Verify PRIVILEGED / PRODUCT

Look for private flags containing:

``` text
PRIVILEGED
PRODUCT
```

Both were present in the known-good development state.

This is important because the R4 module deliberately places the stub
under the product privileged-app hierarchy:

``` text
/product/priv-app/AndroidAutoStub/
```

If `PRIVILEGED` is missing, investigate the module mount/package
reconciliation before continuing.

------------------------------------------------------------------------

# 9. Verify MANAGE_USB

This is the critical permission that originally prevented native Android
Auto projection on the R4.

Search the dump:

``` bat
findstr /I "MANAGE_USB" gearhead_verify.txt
```

The desired result is equivalent to:

``` text
android.permission.MANAGE_USB: granted=true
```

## Why This Matters

Before the privileged stub implementation, the R4 successfully entered
Android Open Accessory / Android Auto USB mode, but Android Auto
terminated with:

``` text
NO_MANAGE_USB_PERMISSION_ERROR(22)
```

Android Auto reported that it lacked:

``` text
android.permission.MANAGE_USB
```

The permission is privileged and cannot be fixed by treating it like an
ordinary runtime permission.

Do **not** attempt:

``` bat
adb shell pm grant com.google.android.projection.gearhead android.permission.MANAGE_USB
```

as a workaround.

The correct solution is for Android Auto to inherit privileged
system-app status and receive the permission through the product
privileged-permission policy.

If `MANAGE_USB` is not granted:

**STOP. Do not modify random permissions or flash anything. Investigate
the package/module state.**

------------------------------------------------------------------------

# 10. Verify the Underlying System Stub

After the Play Store update, Android keeps information about both the
active updated package and the underlying system package.

The active package should normally use:

``` text
/data/app/...
```

while the underlying system package should still correspond to:

``` text
/product/priv-app/AndroidAutoStub
```

Known-good underlying stub:

``` text
versionName=1.2.558700-stub
versionCode=12558700
SYSTEM
PRIVILEGED
PRODUCT
MANAGE_USB granted
```

The exact formatting of `dumpsys package` can vary, so inspect the
surrounding Gearhead sections rather than relying on one exact line
layout.

The key concept is:

``` text
The Play update did not replace the privileged architecture.
It updated the application while preserving it.
```

------------------------------------------------------------------------

# 11. Verify Runtime Permissions

**Risk: 🟢 READ-ONLY**

Normal runtime permissions are separate from privileged permissions.

Useful checks in the package dump include:

``` text
BLUETOOTH_CONNECT
BLUETOOTH_SCAN
READ_PHONE_STATE
ACCESS_COARSE_LOCATION
ACCESS_FINE_LOCATION
RECORD_AUDIO
```

During successful development testing, these were granted after Android
Auto package reconciliation/onboarding:

``` text
BLUETOOTH_CONNECT = true
BLUETOOTH_SCAN = true
READ_PHONE_STATE = true
ACCESS_COARSE_LOCATION = true
ACCESS_FINE_LOCATION = true
RECORD_AUDIO = true
```

Other Android Auto versions may request a somewhat different set.

Runtime permissions can be granted through the normal Android UI.

Do not confuse a missing runtime permission with a missing privileged
permission such as `MANAGE_USB`.

------------------------------------------------------------------------

# 12. Compact Verification Checklist

Before connecting to the vehicle, confirm:

-   [ ] R4 boots normally.
-   [ ] ADB works.
-   [ ] Magisk root works.
-   [ ] `r4_androidauto_enabler` module is present.
-   [ ] `AndroidAutoStub.apk` is visible under
    `/product/priv-app/AndroidAutoStub/`.
-   [ ] Android Auto package exists.
-   [ ] Google Play update is installed if applicable.
-   [ ] Active updated package is allowed to live under `/data/app/...`.
-   [ ] Package has `SYSTEM`.
-   [ ] Updated package has `UPDATED_SYSTEM_APP`.
-   [ ] Package has `PRIVILEGED`.
-   [ ] Package has `PRODUCT`.
-   [ ] `android.permission.MANAGE_USB` is granted.
-   [ ] Required normal runtime permissions are granted or can be
    granted during onboarding.

If all of those are true, the R4 is in the same architectural state that
produced successful Android Auto projection during development.

------------------------------------------------------------------------

# 13. Vehicle Test

**Risk: LIVE EXTERNAL TEST**

Once the package state is correct, connect the R4 to a compatible
Android Auto vehicle/head unit.

The development test vehicle was:

``` text
2023 Nissan Rogue SV
```

Successful tests included:

-   wired Android Auto projection;
-   Android Auto UI on the Nissan head unit;
-   media playback;
-   Poweramp through Android Auto;
-   wireless Android Auto through a third-party wireless AA adapter;
-   persistence after a normal R4 reboot.

During first-time setup, the Nissan/R4 combination required
permission/onboarding interaction and one disconnect/reconnect before
Android Auto fully loaded.

That behavior should not be interpreted as proof of failure during the
first connection attempt.

------------------------------------------------------------------------

# 14. Known Audio Quirk

Android Auto may connect successfully and playback may appear active
while no audio is audible.

On the development R4, operating the R4 volume control once caused audio
to begin immediately.

Current workaround:

``` text
Android Auto connected + playback active + silence
→ touch/operate R4 volume once
→ audio becomes active
```

The cause has not yet been conclusively established.

It appears consistent with an audio-routing/output-initialization issue
rather than an Android Auto projection failure.

Do not modify the known-good privileged permission module solely to
chase this symptom.

------------------------------------------------------------------------

# 15. Known Location / GPS Limitation

Google Maps can launch through Android Auto, but usable location data
was not available on the development R4.

Observed behavior included a wildly incorrect location.

The following were already tested without resolving it:

-   location permission;
-   precise location;
-   Wi-Fi enabled;
-   Android location assistance.

The root cause has not been proven.

Possible areas for future investigation include GNSS hardware
availability, GNSS HAL/provider exposure, firmware configuration, or
system integration.

Those are research directions, **not confirmed causes**.

Do not modify the known-good Android Auto module merely because GPS does
not work.

Android Auto projection and GNSS/location are being treated as separate
problems.

------------------------------------------------------------------------

# 16. Persistence Test

After confirming Android Auto works, reboot normally:

``` bat
adb reboot
```

After Android returns, repeat:

``` bat
adb shell su -c id
adb shell pm path com.google.android.projection.gearhead
adb shell dumpsys package com.google.android.projection.gearhead > gearhead_persistence_test.txt
```

Then:

``` bat
findstr /I "codePath versionName SYSTEM UPDATED_SYSTEM_APP PRIVILEGED PRODUCT MANAGE_USB ACCESS_FINE_LOCATION BLUETOOTH_CONNECT RECORD_AUDIO" gearhead_persistence_test.txt
```

The development R4 retained:

``` text
active Android Auto under /data/app/...
SYSTEM
UPDATED_SYSTEM_APP
PRIVILEGED
PRODUCT
MANAGE_USB = true
ACCESS_FINE_LOCATION = true
BLUETOOTH_CONNECT = true
RECORD_AUDIO = true
```

The underlying product stub also remained present.

This established that the working state survived a normal reboot.

------------------------------------------------------------------------

# 17. Optional Diagnostic Bundle

If asking for help in a GitHub issue or community thread, useful
read-only information includes:

``` bat
adb shell getprop ro.build.fingerprint > r4_build.txt
adb shell getprop ro.boot.slot_suffix >> r4_build.txt
adb shell magisk -v >> r4_build.txt
adb shell pm path com.google.android.projection.gearhead > gearhead_paths.txt
adb shell dumpsys package com.google.android.projection.gearhead > gearhead_package.txt
```

Also include:

-   R4 firmware version;
-   Android Auto version;
-   whether wired or wireless was tested;
-   vehicle/head-unit model;
-   whether `MANAGE_USB` is granted;
-   whether the problem occurs before or after Android Auto UI appears;
-   whether the issue survives a reboot.

Before publishing logs, review them yourself and remove information you
do not want to share.

Do not post device identifiers merely because somebody asks for "all
logs."

------------------------------------------------------------------------

# 18. Expected Architecture at a Glance

A successful installation should conceptually look like this:

``` text
HiBy R4 firmware 1.80
        │
        ├── Magisk
        │
        └── systemless product overlay
              │
              ├── /product/priv-app/AndroidAutoStub/
              │       └── AndroidAutoStub.apk
              │
              └── /product/etc/permissions/
                      └── privapp-permissions-r4-androidauto.xml
                              │
                              ▼
                   Android package manager
                              │
                              ▼
              Google Play Android Auto update
                              │
                              ▼
                  /data/app/.../gearhead
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
           SYSTEM         PRIVILEGED         PRODUCT
             │
             └──── UPDATED_SYSTEM_APP ────────┘
                              │
                              ▼
                     MANAGE_USB granted
                              │
                              ▼
                   Android Auto projection
```

------------------------------------------------------------------------

# Verification Rule

If the expected package state is not present:

**do not escalate to partition writes.**

The Android Auto module is systemless.

A package/module problem should be investigated as a package/module
problem.

Unexpected output is evidence.

Capture it, compare it, and determine what changed before changing
anything else.
