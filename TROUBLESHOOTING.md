# Troubleshooting

This guide covers common problems with the HiBy R4 Android Auto
implementation.

Start with the symptom that most closely matches what you are seeing.
**Do not escalate a package, permission, USB, audio, or application
problem into a partition write.**

For boot failures or Android Recovery, use:

`RECOVERY.md`

For rooting/EDL problems, use:

`ROOTING.md`

For the expected working package state, use:

`VERIFY.md`

------------------------------------------------------------------------

# Golden Rule

The known-good architecture is:

``` text
HiBy R4
  ↓
Magisk root
  ↓
systemless /product overlay
  ↓
AndroidAutoStub as privileged PRODUCT app
  ↓
Google Play Android Auto update
  ↓
SYSTEM + UPDATED_SYSTEM_APP + PRIVILEGED + PRODUCT
  ↓
android.permission.MANAGE_USB = granted
  ↓
Android Auto projection
```

Troubleshoot the first layer that is wrong.

Do not compensate for a broken upper layer by rewriting a lower one.

------------------------------------------------------------------------

# 1. Android Auto Says It Was Not Preinstalled

## Symptom

Android Auto connects to the vehicle/accessory but fails with an error
similar to:

``` text
Android Auto was not preinstalled on this device
```

Development logs identified:

``` text
NO_MANAGE_USB_PERMISSION_ERROR(22)
```

and showed that Android Auto lacked:

``` text
android.permission.MANAGE_USB
```

## Cause

On the stock R4, Android Auto installed from Google Play behaved as an
ordinary `/data/app` application.

`MANAGE_USB` is a privileged Android permission.

It cannot be solved by treating it as a normal runtime permission.

## Check

``` bat
adb shell dumpsys package com.google.android.projection.gearhead > gearhead.txt
findstr /I "SYSTEM UPDATED_SYSTEM_APP PRIVILEGED PRODUCT MANAGE_USB" gearhead.txt
```

The working installation should ultimately show:

``` text
SYSTEM
UPDATED_SYSTEM_APP
PRIVILEGED
PRODUCT
android.permission.MANAGE_USB: granted=true
```

## Do Not Do This

Do not attempt to solve the problem with:

``` bat
adb shell pm grant com.google.android.projection.gearhead android.permission.MANAGE_USB
```

On the stock R4 this fails because `MANAGE_USB` is not an ordinary
changeable runtime permission.

Follow `INSTALL.md` and `VERIFY.md` instead.

------------------------------------------------------------------------

# 2. MANAGE_USB Is Still False or Missing

## Check the Stub

``` bat
adb shell ls -l /product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

Then:

``` bat
adb shell pm path com.google.android.projection.gearhead
```

If the module is active but Android does not recognize the package as
privileged/product, inspect:

``` bat
adb shell dumpsys package com.google.android.projection.gearhead > gearhead.txt
findstr /I "codePath versionName SYSTEM UPDATED_SYSTEM_APP PRIVILEGED PRODUCT MANAGE_USB" gearhead.txt
```

Also verify the module files:

``` bat
adb shell "su -c 'find /data/adb/modules/r4_androidauto_enabler -maxdepth 8 -type f'"
```

Expected important paths:

``` text
system/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
system/product/etc/permissions/privapp-permissions-r4-androidauto.xml
```

If the stub or XML is missing, solve the module problem first.

Do not add random privileged permissions.

------------------------------------------------------------------------

# 3. Android Auto Is Under /data/app --- Is That Wrong?

No.

After Google Play updates Android Auto, the **active** package is
expected to live under:

``` text
/data/app/...
```

The important part is that Android recognizes it as an **updated system
app** backed by the underlying privileged product stub.

Expected post-update state:

``` text
active codePath = /data/app/...
SYSTEM
UPDATED_SYSTEM_APP
PRIVILEGED
PRODUCT
MANAGE_USB = true
```

The `/data/app` path alone is not evidence of failure.

See `VERIFY.md`.

------------------------------------------------------------------------

# 4. Android Auto Is Only Showing the Stub Version

If:

``` bat
adb shell pm path com.google.android.projection.gearhead
```

points directly to:

``` text
/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

and the package version is:

``` text
1.2.558700-stub
```

then the factory-style stub is present, but the current Google Play
Android Auto update may not yet be installed.

Open Google Play on the R4 and install/update Android Auto normally.

Afterward, verify again.

Do not replace the stub with the full Play Store APK manually.

The stub and the updated app serve different roles.

------------------------------------------------------------------------

# 5. The Module Installed but the Paths Look Wrong

A development ZIP created with a Windows-oriented archive method
contained literal backslashes:

``` text
system\product\priv-app\AndroidAutoStub\AndroidAutoStub.apk
```

Magisk interpreted those as malformed filenames rather than Unix
directory paths.

## Before Reboot

Check staged files:

``` bat
adb shell "su -c 'find /data/adb/modules_update/r4_androidauto_enabler -maxdepth 8 -type f'"
```

Correct:

``` text
system/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

Wrong:

``` text
system\product\priv-app\AndroidAutoStub\AndroidAutoStub.apk
```

If you see literal backslashes:

**DO NOT REBOOT.**

Remove the staged module and rebuild the ZIP with the repository
builder.

The public builder uses POSIX `/` archive paths specifically to prevent
this failure.

------------------------------------------------------------------------

# 6. Android Recovery Appears After Module Activation

Do not factory reset.

Do not flash `system`, `product`, `super`, or `vbmeta`.

An early development module caused this exact situation and the R4 was
recovered without a factory reset.

See:

`RECOVERY.md`

The first recovery target should be the most recent Magisk module
change.

------------------------------------------------------------------------

# 7. Android Auto Connects but the Vehicle Never Launches Projection

First verify the package state with `VERIFY.md`.

If all privileged state is correct, check the USB connection.

During development, the R4 successfully entered Android Open Accessory
mode and identified the Android Auto accessory before the permission
issue was solved. This established that the physical USB/projection path
itself was viable.

Try:

-   the vehicle's known Android Auto USB port;
-   a known-good data cable;
-   disconnect/reconnect;
-   completing all Android Auto onboarding prompts on the R4;
-   checking the vehicle for a new-device approval prompt.

Do not assume every USB port in a vehicle supports Android Auto.

------------------------------------------------------------------------

# 8. First Connection Gets Stuck in Permissions / Setup

This happened during the successful Nissan test.

The 2023 Nissan Rogue detected the R4 and Android Auto began setup,
including a request involving Google Maps.

The process initially became stuck around permissions/onboarding.

The successful sequence was:

``` text
connect
→ complete/grant requested permissions
→ disconnect
→ reconnect
→ Android Auto loads
```

A first-session reconnect may therefore be worth trying after
onboarding.

Do not repeatedly reinstall the module merely because the first
connection does not immediately reach the Android Auto launcher.

------------------------------------------------------------------------

# 9. Android Auto Works but There Is No Sound

## Symptom

Projection works.

The media application shows playback.

The vehicle/head unit appears connected.

But there is no audible audio.

## Known Workaround

Operate the R4's volume control once.

During development:

``` text
Android Auto connected
→ playback active
→ silence
→ touch/operate R4 volume
→ audio immediately becomes audible
```

The exact cause has not yet been proven.

The behavior is consistent with an audio-routing or
output-initialization issue.

Do not change the privileged permission XML merely to chase this
symptom.

If the volume-control workaround consistently solves it, report:

-   firmware;
-   Android Auto version;
-   vehicle/head unit;
-   wired or wireless;
-   media app.

That may help isolate the routing behavior.

------------------------------------------------------------------------

# 10. Poweramp Works --- Will Other Music Apps Work?

Poweramp was successfully tested through Android Auto.

The module is not designed specifically for Poweramp.

Once Android Auto projection is functioning, other applications that
legitimately support Android Auto should normally be handled by Android
Auto itself.

However:

**"expected to work" is not the same as "tested on this project."**

When reporting compatibility, distinguish between:

``` text
TESTED
```

and:

``` text
EXPECTED / UNTESTED
```

This repository should not claim application compatibility that nobody
has actually verified.

------------------------------------------------------------------------

# 11. Google Maps Opens but Location Is Completely Wrong

This is a known limitation of the current R4 implementation.

During development, Google Maps could launch, but location data was
wildly incorrect, including a position in the Pacific.

The following did **not** solve it:

-   granting location permission;
-   enabling precise location;
-   enabling Wi-Fi;
-   enabling Android location assistance.

## What We Know

Android Auto projection works.

Google Maps launches.

Normal Android location permissions can be granted.

## What We Do NOT Yet Know

We have not proven whether the failure is caused by:

-   absent GNSS hardware;
-   inaccessible or absent GNSS HAL/provider;
-   HiBy firmware configuration;
-   Android framework integration;
-   another location-source issue.

Those are investigation targets, not established causes.

## Important

Do not modify the known-good v1.1 Android Auto module to chase GPS.

The module solved the Android Auto privilege/projection problem.

Location should be investigated separately and initially with
**read-only diagnostics**.

------------------------------------------------------------------------

# 12. Wireless Android Auto

Wireless Android Auto was successfully tested using a third-party
wireless Android Auto adapter/dongle.

This does not mean the R4 itself suddenly gained a manufacturer-native
wireless Android Auto implementation.

The external adapter handles the wireless bridge to the vehicle.

The useful conclusion is:

``` text
R4 Android Auto projection
+
compatible wireless AA adapter
=
working wireless vehicle connection
```

Adapter compatibility can vary by vehicle and firmware.

A working wired installation is the best baseline before troubleshooting
wireless behavior.

------------------------------------------------------------------------

# 13. Wired Works but Wireless Does Not

If wired Android Auto works, the core R4 privileged Android Auto
architecture is already functioning.

That shifts troubleshooting toward:

-   the wireless adapter;
-   adapter firmware;
-   Bluetooth/Wi-Fi pairing;
-   vehicle compatibility;
-   adapter power/USB behavior.

Do not rebuild the R4 module solely because a particular wireless dongle
fails.

Test wired again to preserve a known-good baseline.

------------------------------------------------------------------------

# 14. Wireless Works but Audio Is Silent

Try the same known audio workaround:

**operate the R4 volume control once.**

If audio then activates, note whether the symptom occurs:

-   wired only;
-   wireless only;
-   both.

That distinction is useful for future diagnosis.

------------------------------------------------------------------------

# 15. Android Auto Lost Privileged State After a Reboot

The known-good installation survived a normal reboot.

Run:

``` bat
adb shell su -c id
```

Then:

``` bat
adb shell dumpsys package com.google.android.projection.gearhead > gearhead_reboot.txt
findstr /I "codePath versionName SYSTEM UPDATED_SYSTEM_APP PRIVILEGED PRODUCT MANAGE_USB" gearhead_reboot.txt
```

Also check:

``` bat
adb shell ls -l /product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

If root is gone, investigate Magisk/boot state.

If root exists but the module is absent, investigate Magisk module
state.

If the module exists but package state changed, investigate package
reconciliation.

Do not jump directly to EDL.

------------------------------------------------------------------------

# 16. Android Auto Broke After a HiBy Firmware Update

A firmware OTA may replace the Magisk-patched boot image.

Check:

``` bat
adb shell su -c id
```

If root is gone, the Android Auto module cannot provide its systemless
`/product` overlay.

Do not flash the old patched firmware 1.80 boot image blindly onto a
newer firmware.

Use the new firmware's matching boot image and reassess the rooting
process.

See:

`ROOTING.md`

------------------------------------------------------------------------

# 17. Android Auto Broke After a Google Play Update

The architecture intentionally allows Android Auto to update through
Google Play.

The known-good Play version during development was:

``` text
17.5.663214-release
```

A future Play update should still inherit the underlying
system/privileged identity if package reconciliation succeeds.

Verify:

``` bat
adb shell dumpsys package com.google.android.projection.gearhead > gearhead_update.txt
findstr /I "versionName SYSTEM UPDATED_SYSTEM_APP PRIVILEGED PRODUCT MANAGE_USB" gearhead_update.txt
```

If all expected flags and `MANAGE_USB` remain present, the problem may
be specific to the newer Android Auto version rather than loss of
privilege.

Record the new version and behavior before changing anything.

Do not immediately downgrade, clear everything, or modify the module
until you know what state changed.

------------------------------------------------------------------------

# 18. Runtime Permissions Disappeared

Runtime permissions are different from privileged permissions.

Android Auto may need ordinary permissions such as:

``` text
BLUETOOTH_CONNECT
BLUETOOTH_SCAN
READ_PHONE_STATE
ACCESS_COARSE_LOCATION
ACCESS_FINE_LOCATION
RECORD_AUDIO
```

These can be handled through normal Android permission UI.

If package reconciliation or an app update resets runtime permissions,
grant the requested normal permissions again.

Do not confuse that with:

``` text
MANAGE_USB
```

which is supplied by the privileged architecture.

------------------------------------------------------------------------

# 19. The Stub Hash Does Not Match

Known-good development stub:

``` text
Version:
1.2.558700-stub

Size:
3,953,532 bytes

SHA-256:
57EA6D176178E52FEDB8B351441141AEFAF8B6E98CFBED10A9FA1B006A608072
```

If your hash differs, the correct label is:

``` text
UNTESTED STUB VERSION
```

not:

``` text
BAD APK
```

A different donor firmware may legitimately contain a different stub.

Before installing it:

-   verify package identity;
-   record version;
-   record size;
-   record SHA-256;
-   understand that you are testing a new variable.

See:

`ANDROID-AUTO-STUB.md`

------------------------------------------------------------------------

# 20. The Stub Matches but the Module Still Fails

A matching APK does not prove the rest of the module is correct.

Verify:

-   module directory hierarchy;
-   POSIX ZIP paths;
-   `module.prop`;
-   privileged permission XML;
-   Magisk installation state;
-   product overlay visibility;
-   Android package flags;
-   `MANAGE_USB`.

Change one variable at a time.

------------------------------------------------------------------------

# 21. Magisk Root Is Gone

Check:

``` bat
adb shell su -c id
```

If `su` is unavailable, determine whether:

-   a firmware OTA occurred;
-   the boot image changed;
-   Magisk was removed;
-   the device changed slots;
-   another boot-related modification occurred.

Do not reinstall the Android Auto module until root/systemless overlay
functionality is restored.

See:

`ROOTING.md`

and, where appropriate:

`RECOVERY.md`

------------------------------------------------------------------------

# 22. ADB Does Not See the R4

Start with the boring things before invoking Qualcomm.

Check:

-   USB debugging is enabled;
-   the R4 is unlocked;
-   the authorization prompt was accepted;
-   the cable carries data;
-   the selected USB port works;
-   Windows sees the device;
-   `adb kill-server` / `adb start-server` if appropriate.

If the device is actually in EDL, normal ADB will not see it.

If the device is in Android Recovery, ADB behavior/authorization may
differ.

During the development recovery incident, Recovery ADB was unauthorized.

------------------------------------------------------------------------

# 23. R4 Is Showing Qualcomm 9008

Qualcomm 9008 means the device is in EDL mode.

That is not automatically a brick.

If you intentionally ran:

``` bat
adb reboot edl
```

then 9008 is expected.

Do not start writing partitions merely because Windows now shows a
Qualcomm device.

Use the EDL procedure in `ROOTING.md`, and begin with read-only
identification/GPT checks.

If you did **not** intentionally enter EDL, document exactly what
happened before it appeared.

------------------------------------------------------------------------

# 24. Wrong Firehose / Sahara Errors

Do not respond to a Firehose error by cycling through random
programmers.

During development, automatic loader selection chose an incorrect
mdm9x05 NAND loader and failed.

The successful programmer was R4/SM6125-specific and used eMMC.

See the hashes and warnings in:

`ROOTING.md`

A failed loader attempt is a reason to investigate compatibility, not a
reason to escalate to a write.

------------------------------------------------------------------------

# 25. The Car Wants Google Maps

The tested Nissan requested Google Maps during initial Android Auto
setup.

Installing/allowing the requested Android Auto companion applications
may be part of onboarding.

However, Maps navigation remains affected by the R4 location limitation
described above.

Android Auto projection can still work even though usable GPS/location
does not.

------------------------------------------------------------------------

# 26. "It Works, but..."

If Android Auto UI appears on the vehicle display, that is an important
diagnostic boundary.

At that point:

``` text
USB/accessory negotiation works
Android Auto projection works
MANAGE_USB problem is solved
core privileged architecture works
```

Problems that occur **after** the Android Auto UI appears should be
investigated as their own subsystem:

``` text
no audio      → audio routing
bad GPS       → location/GNSS
one app fails → app compatibility
wireless only → adapter/network path
```

Do not keep "fixing Android Auto" after Android Auto itself is already
projecting.

------------------------------------------------------------------------

# 27. Minimum Diagnostic Report

When opening a GitHub issue, include:

``` text
R4 firmware:
Android version:
Magisk version:
Android Auto version:
Stub version:
Stub SHA-256:
Vehicle/head unit:
Wired or wireless:
Wireless adapter, if applicable:
Does Android Auto UI appear:
Does audio work:
Does touching R4 volume fix audio:
Does location work:
MANAGE_USB granted:
SYSTEM present:
UPDATED_SYSTEM_APP present:
PRIVILEGED present:
PRODUCT present:
Last change before failure:
```

Useful command output:

``` bat
adb shell getprop ro.build.fingerprint
adb shell getprop ro.boot.slot_suffix
adb shell su -c id
adb shell pm path com.google.android.projection.gearhead
adb shell dumpsys package com.google.android.projection.gearhead > gearhead_issue.txt
```

Review logs before posting them publicly.

Do not publish identifiers or unrelated personal information simply
because a troubleshooting template asks for logs.

------------------------------------------------------------------------

# 28. Known-Good Reference

``` text
Device:
HiBy R4

Firmware:
1.80

Android:
12 / API 31

Magisk:
30.7

Stub:
1.2.558700-stub

Stub SHA-256:
57EA6D176178E52FEDB8B351441141AEFAF8B6E98CFBED10A9FA1B006A608072

Tested Android Auto:
17.5.663214-release

Test vehicle:
2023 Nissan Rogue SV

Wired projection:
WORKING

Wireless through third-party AA adapter:
WORKING

Poweramp:
WORKING

Normal reboot persistence:
VERIFIED

MANAGE_USB:
GRANTED

Known audio issue:
May start silent until R4 volume is operated once

Known location issue:
Google Maps launches, usable GPS/location not currently working
```

------------------------------------------------------------------------

# Final Troubleshooting Rule

If you can state exactly which layer stopped matching the known-good
state, you are troubleshooting.

If you cannot yet state which layer is wrong and are considering
flashing something anyway, you are gambling.

Collect evidence first.

The R4 has already demonstrated that it can run Android Auto.

There is no need to sacrifice another partition to appease it.
