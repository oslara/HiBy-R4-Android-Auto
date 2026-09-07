# Obtaining AndroidAutoStub.apk

This project does **not** redistribute Google's proprietary
`AndroidAutoStub.apk`.

Instead, users extract the stub from a compatible Android device they
own and use the project builder to create the HiBy R4 Magisk module
locally.

> **Safety classification: READ-ONLY DONOR DEVICE OPERATION**
>
> The extraction procedure below reads package information and copies an
> APK from the donor phone. It does not root, flash, modify, uninstall,
> disable, or otherwise change the donor device.

------------------------------------------------------------------------

# Why the Stub Is Needed

On a phone where Android Auto is factory-integrated, Android Auto may
exist as a privileged system/product application.

During development, a Samsung phone provided the reference architecture:

``` text
/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

The Play Store could then install a newer Android Auto package under
`/data/app/`, while Android continued to treat it as an updated
privileged system application.

That behavior became the model for the R4 implementation:

``` text
Factory-style privileged stub
        ↓
Magisk systemless /product overlay
        ↓
Google Play Android Auto update
        ↓
UPDATED_SYSTEM_APP + PRIVILEGED + PRODUCT
        ↓
android.permission.MANAGE_USB granted
```

This is what resolved Android Auto error:

``` text
NO_MANAGE_USB_PERMISSION_ERROR(22)
```

on the development R4.

------------------------------------------------------------------------

# Known-Good Reference Stub

The stub used successfully during development had:

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
57EA6D176178E52FEDB8B351441141AEFAF8B6E98CFBED10A9FA1B006A608072
```

It was extracted from a compatible Samsung Android device.

The reference path was:

``` text
/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

A different stub version **may** work.

A different hash does not automatically mean the file is bad. It means
that particular stub has not been validated by this project unless
somebody has independently tested and documented it.

------------------------------------------------------------------------

# Donor Device Requirements

A useful donor device should have Android Auto integrated as a factory
system/product application.

Samsung devices are known to use the architecture tested during this
project, but this documentation does **not** claim that every Samsung
model, firmware, region, or Android release contains the same stub.

Other manufacturers may use different paths or integration methods.

Do not assume a file is compatible merely because its filename contains
`AndroidAuto`.

------------------------------------------------------------------------

# Step 1 --- Connect the Donor Phone

**Risk: 🟢 READ-ONLY**

Enable USB debugging on the donor phone and connect it to the computer.

Verify ADB:

``` bat
adb devices
```

Authorize the computer on the phone if prompted.

------------------------------------------------------------------------

# Step 2 --- Inspect the Android Auto Package

**Risk: 🟢 READ-ONLY**

Run:

``` bat
adb shell pm path com.google.android.projection.gearhead
```

If Android Auto has been updated through Google Play, this may show the
currently active package under:

``` text
/data/app/...
```

That is **not necessarily the factory stub we want**.

Save the complete package information:

``` bat
adb shell dumpsys package com.google.android.projection.gearhead > donor_gearhead.txt
```

You can inspect useful fields in Windows CMD with:

``` bat
findstr /I "codePath versionName versionCode SYSTEM UPDATED_SYSTEM_APP PRIVILEGED PRODUCT" donor_gearhead.txt
```

We are looking for evidence that Android Auto has an underlying
system/product package, not merely an ordinary `/data/app` installation.

------------------------------------------------------------------------

# Step 3 --- Look for the Factory Stub

**Risk: 🟢 READ-ONLY**

On the known-good Samsung donor, the stub existed here:

``` text
/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

Check whether that exact file exists:

``` bat
adb shell ls -l /product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

If the file exists, continue.

If it does not exist:

**STOP and investigate the donor's Android Auto architecture.**

Do not start copying random APKs from `/system`, `/product`,
`/system_ext`, or `/data/app` and assume they are interchangeable.

The project builder can validate a candidate against the known-good
reference, but it cannot prove an unknown proprietary APK is compatible.

------------------------------------------------------------------------

# Step 4 --- Pull the Stub

**Risk: 🟢 READ-ONLY**

Copy the factory stub from the donor phone to your computer:

``` bat
adb pull /product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

This copies the APK.

It does not remove or modify the donor copy.

After the command completes, you should have:

``` text
AndroidAutoStub.apk
```

on your computer.

------------------------------------------------------------------------

# Step 5 --- Calculate SHA-256

**Risk: 🔵 LOCAL / PC ONLY**

In Windows CMD:

``` bat
certutil -hashfile AndroidAutoStub.apk SHA256
```

Compare the result with the known-good development reference:

``` text
57EA6D176178E52FEDB8B351441141AEFAF8B6E98CFBED10A9FA1B006A608072
```

If it matches:

``` text
MATCHES KNOWN-GOOD OSCAR/LYRA REFERENCE
```

If it does not match:

``` text
UNTESTED STUB VERSION
```

**A mismatch is a warning, not an instruction to force-install it.**

Research the version and package before proceeding.

------------------------------------------------------------------------

# Step 6 --- Check the File Size

**Risk: 🔵 LOCAL / PC ONLY**

The known-good stub size was:

``` text
3,953,532 bytes
```

You can inspect the local file with:

``` bat
dir AndroidAutoStub.apk
```

A different size combined with a different hash confirms that you have a
different build.

Again, that does not automatically mean the file is invalid. It means it
is not the exact build tested by this project.

------------------------------------------------------------------------

# Step 7 --- Optional Package Inspection

If you have Android SDK build tools available, you may inspect the APK
metadata using tools such as `apkanalyzer` or `aapt`.

At minimum, the candidate should identify as:

``` text
com.google.android.projection.gearhead
```

Do not use an APK whose package identity does not match Android Auto.

The builder included with this project will perform basic
integrity/reference checks before constructing the module.

------------------------------------------------------------------------

# Step 8 --- Place the Stub in the Module Source

**Risk: 🔵 LOCAL / PC ONLY**

Place your extracted APK at:

``` text
module/system/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

The resulting project tree should include:

``` text
module/
├── module.prop
└── system/
    └── product/
        ├── etc/
        │   └── permissions/
        │       └── privapp-permissions-r4-androidauto.xml
        └── priv-app/
            └── AndroidAutoStub/
                └── AndroidAutoStub.apk
```

Then use:

``` text
tools/build-module.py
```

to construct the installable Magisk ZIP.

See:

`INSTALL.md`

------------------------------------------------------------------------

# Why We Do Not Include the APK

`AndroidAutoStub.apk` is Google software.

This project documents how to reproduce the working configuration but
does not need to redistribute Google's proprietary binary to do so.

The repository therefore contains a placeholder/instructions rather than
the APK itself.

The same principle applies to:

-   Android Auto APKs and Play Store splits
-   another user's stock boot image
-   another user's Magisk-patched boot image

> **We provide the implementation, not somebody else's proprietary
> binaries.**

------------------------------------------------------------------------

# What About Downloading the Stub From an APK Website?

That is not the recommended procedure.

There are several problems:

1.  You may obtain a different Android Auto component rather than the
    factory stub.
2.  You may obtain a different version than the one documented here.
3.  You lose the clean provenance of extracting the file from a device
    you own.
4.  Third-party APK mirrors introduce an unnecessary trust problem.

The known-good development procedure used a factory stub extracted
directly from a compatible donor phone.

That remains the recommended method.

------------------------------------------------------------------------

# Do I Need the Same Samsung Phone?

Not necessarily.

What matters is obtaining a compatible factory Android Auto stub with
the expected package identity and architecture.

However, at the time this guide was written, the exact build listed
above is the one that has been successfully tested on the HiBy R4.

Until additional community testing exists, other stub versions should be
described as:

**UNTESTED**

rather than assumed compatible.

------------------------------------------------------------------------

# Do I Need to Keep the Donor Phone Connected?

No.

Once the stub has been copied and verified, module construction happens
locally on the computer.

The donor phone is not involved in the R4 installation.

------------------------------------------------------------------------

# Does This Modify the Samsung / Donor Phone?

No.

The documented donor procedure consists of:

``` text
ADB package inspection → filesystem read → adb pull
```

There is no root requirement and no partition write.

------------------------------------------------------------------------

# Development Reference

Known-good reference:

``` text
Filename:
AndroidAutoStub.apk

Package:
com.google.android.projection.gearhead

Version:
1.2.558700-stub

Version code:
12558700

Size:
3,953,532 bytes

SHA-256:
57EA6D176178E52FEDB8B351441141AEFAF8B6E98CFBED10A9FA1B006A608072

Reference factory path:
/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

------------------------------------------------------------------------

# Next Step

After obtaining and verifying the stub:

1.  Place it in the module source tree.
2.  Build the module using `tools/build-module.py`.
3.  Follow `INSTALL.md`.
4.  Verify the resulting Android Auto package state using `VERIFY.md`.

Do not manually modify the known-good privileged-permission policy
merely because your stub version differs.

A different stub is a new variable.

Change one variable at a time.
