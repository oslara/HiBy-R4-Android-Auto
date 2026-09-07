# Technical Notes

This document explains the technical path that led to working native
Android Auto projection on the HiBy R4.

It is not required reading for installation. It exists to document
**what was observed, what failed, what changed, and why the final
implementation works**.

> **Project claim**
>
> To the best of our knowledge, this is the first publicly documented
> working implementation of native Android Auto projection on the HiBy
> R4.
>
> This is deliberately narrower than claiming an absolute world first.

------------------------------------------------------------------------

# 1. The Original Problem

The HiBy R4 is an Android-based digital audio player, but Android Auto
is not factory-integrated by HiBy.

Installing Android Auto from Google Play produced an ordinary
application under:

``` text
/data/app/...
```

The initial assumption was that the main challenge would be USB support
or Android Open Accessory Protocol compatibility.

That turned out not to be the real blocker.

The R4 could already get surprisingly far.

------------------------------------------------------------------------

# 2. Development Platform

The working development device was:

``` text
Device:
HiBy R4

Firmware:
1.80

Android:
12 / API 31

SoC:
Qualcomm Snapdragon 665 / SM6125 family

Platform:
trinket

RAM:
3 GB

Boot:
A/B

Storage:
eMMC

Bootloader:
unlocked on development device

Verified boot state:
orange

Privileged permission enforcement:
ro.control_privapp_permissions=enforce
```

Known firmware/build reference:

``` text
HiBy/R4/R4:12/SKQ1.211006.001/eng.HiBy.20260807.114134:user/dev-keys
```

The project should not assume every R4 firmware revision has identical
behavior.

------------------------------------------------------------------------

# 3. Android Auto Package on the Stock R4

The Google Play Android Auto package was:

``` text
com.google.android.projection.gearhead
```

During development, the Play-installed version was:

``` text
17.5.663214-release
versionCode 175663214
targetSdk 37
```

Before system integration, it lived as an ordinary application under:

``` text
/data/app/...
```

There was no factory Gearhead/Android Auto stub found under the R4's:

``` text
/system
/product
/system_ext
```

privileged application trees.

This distinction became critical.

------------------------------------------------------------------------

# 4. USB Was Not the Fundamental Problem

The R4 advertises Android USB accessory/host capability.

When connected to the 2023 Nissan Rogue, the R4 successfully
transitioned into an accessory configuration equivalent to:

``` text
accessory,adb
```

Android identified the accessory as:

``` text
Manufacturer:
Android

Model:
Android Auto
```

Android Auto itself received the accessory connection.

That meant several important things had already happened:

``` text
USB physical connection
        ↓
Android Open Accessory negotiation
        ↓
Android Auto accessory recognized
        ↓
Gearhead receives accessory event
```

The R4 was not simply incapable of speaking to an Android Auto head
unit.

The failure occurred later.

------------------------------------------------------------------------

# 5. The Exact Blocker: MANAGE_USB

Logs from Android Auto exposed the decisive error:

``` text
NO_MANAGE_USB_PERMISSION_ERROR(22)
```

Android Auto also reported, in substance, that it was not preinstalled
on the device.

Inspection showed:

``` text
android.permission.MANAGE_USB
```

was not granted to Gearhead.

This was the turning point.

------------------------------------------------------------------------

# 6. Why `pm grant` Could Not Fix It

`MANAGE_USB` is not an ordinary runtime permission.

On this Android build it is protected as a privileged/signature-class
permission.

Attempting to grant it using the normal package manager mechanism failed
because it is not a user-changeable runtime permission.

Conceptually:

``` text
adb shell pm grant ...
```

works for eligible runtime permissions.

It does not transform an ordinary `/data/app` package into a privileged
platform-integrated application.

The solution therefore had to change Android Auto's **package
identity/state**, not merely toggle a runtime permission.

------------------------------------------------------------------------

# 7. R4 Privileged Permission Enforcement

The R4 reports:

``` text
ro.control_privapp_permissions=enforce
```

This matters.

Android's privileged-permission allowlist mechanism is not merely
advisory in this configuration.

A privileged application requesting protected privileged permissions
needs an appropriate allowlist policy.

That also explains why simply dropping an APK into a privileged-looking
path without understanding its requested permissions is dangerous.

The first experimental module demonstrated that rather vividly.

------------------------------------------------------------------------

# 8. The Samsung Reference Architecture

A Samsung S26 Ultra used during development provided the key reference.

Samsung shipped:

``` text
/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

The factory stub identified as:

``` text
Package:
com.google.android.projection.gearhead

Version:
1.2.558700-stub

Version code:
12558700

minSdk:
28

targetSdk:
36

Size:
3,953,532 bytes

SHA-256:
57EA6D176178E52FEDB8B351441141AEFAF8B6E98CFBED10A9FA1B006A608072
```

This was not merely an empty filename placeholder.

It was a real Android package with code/resources and the same Android
Auto package identity.

------------------------------------------------------------------------

# 9. The Important Samsung Behavior

On the Samsung reference device, the currently updated Android Auto
application lived under:

``` text
/data/app/...
```

Yet Android still identified it with system/product privileged state.

Conceptually:

``` text
factory AndroidAutoStub
        │
        ▼
SYSTEM + PRIVILEGED + PRODUCT package identity
        │
        ▼
Google Play installs newer Gearhead
        │
        ▼
/data/app/... active application
        │
        ▼
UPDATED_SYSTEM_APP
        │
        ▼
retains underlying privileged system identity
```

This explained why merely seeing Android Auto under `/data/app` did not
mean Samsung was running it as an ordinary user application.

The underlying factory package relationship mattered.

------------------------------------------------------------------------

# 10. Signing Compatibility

The Samsung factory stub and the Google Play Android Auto update were
compatible as the same package/update lineage.

That allowed PackageManager to treat the Play package as an update to
the underlying system package rather than as an unrelated application.

This is essential.

A random APK named:

``` text
AndroidAutoStub.apk
```

does not gain this relationship by filename.

Package identity, signing/update compatibility, placement, and Android
package policy all matter.

------------------------------------------------------------------------

# 11. Samsung Privileged Permission Policy

The Samsung reference policy granted Gearhead a broad privileged
permission set including:

``` text
ACTIVITY_EMBEDDING
BLUETOOTH_PRIVILEGED
CALL_PRIVILEGED
CHANGE_COMPONENT_ENABLED_STATE
COMPANION_APPROVE_WIFI_CONNECTIONS
CONTROL_INCALL_EXPERIENCE
DUMP
ENTER_CAR_MODE_PRIORITIZED
LOCAL_MAC_ADDRESS
LOCATION_HARDWARE
MANAGE_USB
MANAGE_USERS
MODIFY_AUDIO_ROUTING
MODIFY_DAY_NIGHT_MODE
MODIFY_PHONE_STATE
POWER_SAVER
READ_PRIVILEGED_PHONE_STATE
REQUEST_COMPANION_SELF_MANAGED
SCHEDULE_EXACT_ALARM
START_ACTIVITIES_FROM_BACKGROUND
TETHER_PRIVILEGED
UPDATE_APP_OPS_STATS
```

The R4 implementation does **not** simply redistribute Samsung's
proprietary configuration.

Instead, requested permissions were compared against the R4 package and
a project-specific policy was constructed.

------------------------------------------------------------------------

# 12. R4 Android Auto Requested Privileged Set

The R4 Gearhead package requested the following privileged set during
development:

``` text
ACTIVITY_EMBEDDING
BIND_APPWIDGET
BLUETOOTH_PRIVILEGED
CALL_PRIVILEGED
CHANGE_COMPONENT_ENABLED_STATE
COMPANION_APPROVE_WIFI_CONNECTIONS
CONTROL_INCALL_EXPERIENCE
DUMP
ENTER_CAR_MODE_PRIORITIZED
LOCAL_MAC_ADDRESS
LOCATION_HARDWARE
MANAGE_USB
MANAGE_USERS
MODIFY_AUDIO_ROUTING
MODIFY_DAY_NIGHT_MODE
MODIFY_PHONE_STATE
POWER_SAVER
READ_PRIVILEGED_PHONE_STATE
SEND_SMS
START_ACTIVITIES_FROM_BACKGROUND
TETHER_PRIVILEGED
TOGGLE_AUTOMOTIVE_PROJECTION
UPDATE_APP_OPS_STATS
```

That is 23 requested privileged permissions in the tested package/build
combination.

------------------------------------------------------------------------

# 13. R4 vs Samsung Differences

Permissions observed on the R4 request set but not in the Samsung
reference allowlist included:

``` text
BIND_APPWIDGET
SEND_SMS
TOGGLE_AUTOMOTIVE_PROJECTION
```

Permissions present in the Samsung reference allowlist but not in the R4
requested set included:

``` text
REQUEST_COMPANION_SELF_MANAGED
SCHEDULE_EXACT_ALARM
```

This was another reason not to blindly clone the donor device's policy.

The goal was to build a policy for the R4 package actually being tested.

------------------------------------------------------------------------

# 14. The v1.0 Experiment

The first module prototype attempted the minimum obvious fix.

It systemlessly supplied:

``` text
/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

and an R4 privileged permission XML that allowed only:

``` text
MANAGE_USB
```

The module activated on reboot.

Then the R4 entered splash/reboot cycles and eventually Android Recovery
with:

``` text
Can't load Android system
```

The device was recovered without factory reset.

See:

`RECOVERY.md`

------------------------------------------------------------------------

# 15. What the v1.0 Failure Proved

The exact boot-failure mechanism was not conclusively proven.

However, the recovery boot produced an important PackageManager message
indicating that the system package:

``` text
com.google.android.projection.gearhead
```

had existed during the module-enabled boot and was later considered
absent when RescueParty bypassed the module.

In other words:

**the Magisk product overlay had successfully caused Android to
systemify Gearhead.**

That was a very useful failure.

The architecture was working far enough for PackageManager to recognize
the stub as a system package.

The remaining implementation needed a correct privileged permission
policy and careful package reconciliation.

------------------------------------------------------------------------

# 16. The v1.1 Permission Policy

The successful policy allows:

``` text
ACTIVITY_EMBEDDING
BLUETOOTH_PRIVILEGED
CALL_PRIVILEGED
CHANGE_COMPONENT_ENABLED_STATE
COMPANION_APPROVE_WIFI_CONNECTIONS
CONTROL_INCALL_EXPERIENCE
DUMP
ENTER_CAR_MODE_PRIORITIZED
LOCAL_MAC_ADDRESS
LOCATION_HARDWARE
MANAGE_USB
MANAGE_USERS
MODIFY_AUDIO_ROUTING
MODIFY_DAY_NIGHT_MODE
MODIFY_PHONE_STATE
POWER_SAVER
READ_PRIVILEGED_PHONE_STATE
START_ACTIVITIES_FROM_BACKGROUND
TETHER_PRIVILEGED
TOGGLE_AUTOMOTIVE_PROJECTION
UPDATE_APP_OPS_STATS
```

and explicitly denies:

``` text
BIND_APPWIDGET
SEND_SMS
```

The resulting project policy is:

``` xml
<?xml version="1.0" encoding="utf-8"?>
<permissions>
    <privapp-permissions package="com.google.android.projection.gearhead">
        <permission name="android.permission.ACTIVITY_EMBEDDING"/>
        <permission name="android.permission.BLUETOOTH_PRIVILEGED"/>
        <permission name="android.permission.CALL_PRIVILEGED"/>
        <permission name="android.permission.CHANGE_COMPONENT_ENABLED_STATE"/>
        <permission name="android.permission.COMPANION_APPROVE_WIFI_CONNECTIONS"/>
        <permission name="android.permission.CONTROL_INCALL_EXPERIENCE"/>
        <permission name="android.permission.DUMP"/>
        <permission name="android.permission.ENTER_CAR_MODE_PRIORITIZED"/>
        <permission name="android.permission.LOCAL_MAC_ADDRESS"/>
        <permission name="android.permission.LOCATION_HARDWARE"/>
        <permission name="android.permission.MANAGE_USB"/>
        <permission name="android.permission.MANAGE_USERS"/>
        <permission name="android.permission.MODIFY_AUDIO_ROUTING"/>
        <permission name="android.permission.MODIFY_DAY_NIGHT_MODE"/>
        <permission name="android.permission.MODIFY_PHONE_STATE"/>
        <permission name="android.permission.POWER_SAVER"/>
        <permission name="android.permission.READ_PRIVILEGED_PHONE_STATE"/>
        <permission name="android.permission.START_ACTIVITIES_FROM_BACKGROUND"/>
        <permission name="android.permission.TETHER_PRIVILEGED"/>
        <permission name="android.permission.TOGGLE_AUTOMOTIVE_PROJECTION"/>
        <permission name="android.permission.UPDATE_APP_OPS_STATS"/>
        <deny-permission name="android.permission.BIND_APPWIDGET"/>
        <deny-permission name="android.permission.SEND_SMS"/>
    </privapp-permissions>
</permissions>
```

This is the known-good v1.1 project policy.

------------------------------------------------------------------------

# 17. Why BIND_APPWIDGET and SEND_SMS Are Denied

The project did not need to grant every privileged permission requested
by Gearhead merely because it was requested.

For the tested implementation:

``` text
BIND_APPWIDGET
SEND_SMS
```

were explicitly denied.

The successful Android Auto projection result demonstrates that neither
permission was required for the tested core projection/media use case.

This should not be interpreted as a universal claim about every future
Android Auto feature.

It is a statement about the known-good tested implementation.

------------------------------------------------------------------------

# 18. Why TOGGLE_AUTOMOTIVE_PROJECTION Was Included

The R4 package requested:

``` text
android.permission.TOGGLE_AUTOMOTIVE_PROJECTION
```

and the successful R4-specific policy includes it.

This was not part of the observed Samsung reference allowlist
comparison, reinforcing the decision to build the policy around the R4's
actual package behavior rather than blindly copying Samsung's list.

------------------------------------------------------------------------

# 19. Why Magisk Was Used

The project needed to present files under:

``` text
/product/priv-app/
```

and:

``` text
/product/etc/permissions/
```

without physically modifying Android's product/system partitions.

Magisk provides a systemless overlay mechanism suitable for that
purpose.

The final implementation therefore changes the effective Android
filesystem view at boot while leaving the underlying physical product
partition untouched.

Conceptually:

``` text
physical /product
        +
Magisk module overlay
        =
effective /product seen by Android
```

This significantly limits the scope of persistent modification compared
with directly rewriting dynamic partitions.

------------------------------------------------------------------------

# 20. The Final Module Layout

``` text
r4_androidauto_enabler/
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

The repository does not distribute the proprietary APK.

Users supply their own extracted compatible stub.

------------------------------------------------------------------------

# 21. The Windows ZIP Path Bug

An early v1.1 archive built with a Windows-oriented compression method
stored entries with literal backslashes.

Instead of:

``` text
system/product/priv-app/...
```

it contained:

``` text
system\product\priv-app\...
```

Magisk extracted these incorrectly.

The problem was caught during preflight before reboot.

The module was cleaned up and rebuilt using Python's ZIP tooling with
POSIX path names.

This is why the public builder explicitly rejects archive entries
containing:

``` text
\
```

Correct archive paths must use:

``` text
/
```

This sounds trivial until the boot-critical module tree is one character
away from being nonsense.

------------------------------------------------------------------------

# 22. Successful Pre-Play State

After activating the corrected v1.1 module, before installing the Play
update:

``` text
pm path:
package:/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk

codePath:
/product/priv-app/AndroidAutoStub

version:
1.2.558700-stub

flags:
SYSTEM

privateFlags:
PRIVILEGED
PRODUCT

MANAGE_USB:
granted
```

This proved that the R4 recognized the systemless donor stub as the
intended privileged product package.

------------------------------------------------------------------------

# 23. Successful Post-Play State

After Google Play updated Android Auto, the active application moved to
split APKs under:

``` text
/data/app/...
```

The tested active package became:

``` text
versionCode:
175663214

versionName:
17.5.663214-release
```

while its state included:

``` text
SYSTEM
UPDATED_SYSTEM_APP
PRIVILEGED
PRODUCT
```

and:

``` text
android.permission.MANAGE_USB = granted
```

The underlying system stub remained associated with:

``` text
/product/priv-app/AndroidAutoStub
```

This was the target architecture.

------------------------------------------------------------------------

# 24. Package Reconciliation

The crucial behavior can be summarized as:

``` text
BOOT
 │
 ▼
Magisk exposes AndroidAutoStub under /product/priv-app
 │
 ▼
PackageManager scans product applications
 │
 ▼
Gearhead becomes SYSTEM + PRIVILEGED + PRODUCT
 │
 ▼
R4 privapp policy grants allowed privileged permissions
 │
 ▼
MANAGE_USB becomes available
 │
 ▼
Google Play Gearhead package is recognized as update
 │
 ▼
Active /data/app package becomes UPDATED_SYSTEM_APP
 │
 ▼
privileged/product identity is retained
```

The Play update does not need to physically live inside `/product`.

It inherits the system relationship from the underlying compatible
package.

------------------------------------------------------------------------

# 25. Runtime Permissions Are a Separate Layer

After package reconciliation, normal Android runtime permissions still
needed to be handled.

During successful testing, permissions including:

``` text
BLUETOOTH_CONNECT
BLUETOOTH_SCAN
READ_PHONE_STATE
ACCESS_COARSE_LOCATION
ACCESS_FINE_LOCATION
RECORD_AUDIO
```

were granted.

These are conceptually separate from:

``` text
MANAGE_USB
```

A normal runtime permission can be presented to the user through
Android's permission model.

A privileged permission depends on privileged package integration and
policy.

Confusing those two categories was one of the traps in the original
problem.

------------------------------------------------------------------------

# 26. The Vehicle Test

The live test vehicle was:

``` text
2023 Nissan Rogue SV
```

The Rogue detected the R4.

Initial onboarding requested additional setup/permissions and Google
Maps.

The first attempt became stuck during onboarding.

After permissions were handled and the R4 was disconnected/reconnected:

**Android Auto loaded successfully on the Nissan head unit.**

Media playback worked.

Poweramp worked.

This converted the project from:

``` text
package state looks correct
```

to:

``` text
actual Android Auto projection works in a vehicle
```

------------------------------------------------------------------------

# 27. Wireless Android Auto

The working R4 was subsequently tested through a third-party wireless
Android Auto adapter.

That also worked.

The external adapter provides the wireless bridge; the R4 is still
supplying the Android Auto projection session.

This demonstrates that the implementation is not limited to a direct USB
cable when a compatible wireless bridge is used.

It does not establish compatibility with every wireless adapter.

------------------------------------------------------------------------

# 28. Audio Routing Quirk

A reproducible-ish behavior was observed where:

``` text
Android Auto connected
media playback active
vehicle silent
```

until the R4's volume control was operated once.

Then audio became audible immediately.

The exact mechanism has not been proven.

A reasonable investigation area is audio route/output activation, but
that remains a hypothesis.

The important architectural observation is that projection and playback
were already functioning.

Therefore this symptom is being treated separately from the
privilege/USB problem.

------------------------------------------------------------------------

# 29. GPS / Location Limitation

Location remains unresolved.

Google Maps launches, but the development R4 produced wildly incorrect
location information.

Testing included:

``` text
location permission
precise location
Wi-Fi enabled
Android location assistance
```

without producing usable positioning.

Potential investigation areas include:

``` text
GNSS hardware
GNSS HAL/provider exposure
HiBy firmware configuration
Android location framework integration
```

None of those has yet been proven as the root cause.

The project intentionally does not modify the known-good Android Auto
privilege module to chase this unrelated subsystem.

------------------------------------------------------------------------

# 30. Reboot Persistence

After successful vehicle testing, the R4 was rebooted normally.

Verification showed that the working architecture persisted:

``` text
active Gearhead:
/data/app/...

SYSTEM:
yes

UPDATED_SYSTEM_APP:
yes

PRIVILEGED:
yes

PRODUCT:
yes

MANAGE_USB:
true

underlying stub:
/product/priv-app/AndroidAutoStub

stub privileged/product state:
preserved
```

Normal runtime permissions used during testing also persisted.

This established that the result was not merely a one-session
package-manager accident.

------------------------------------------------------------------------

# 31. What Was Physically Modified

The rooting process wrote the Magisk-patched image to the development
R4's active boot partition.

That was an actual persistent partition write.

The Android Auto implementation itself did **not** physically rewrite:

``` text
system
product
system_ext
super
vbmeta
```

The Android Auto files are supplied systemlessly through Magisk.

This distinction matters both technically and for recovery.

------------------------------------------------------------------------

# 32. What Was Not Required

The successful implementation did not require:

``` text
physical /system modification
physical /product modification
physical /super modification
vbmeta modification
verity disabling
slot switching
custom recovery installation
KernelSU
a custom Android ROM
vehicle/head-unit modification
```

Fastboot boot/flash commands were also not the path used for rooting
because the development R4's Fastboot implementation rejected the
relevant commands.

Rooting details are documented separately in:

`ROOTING.md`

------------------------------------------------------------------------

# 33. Why the Project Does Not Ship a Patched Boot Image

Boot images are firmware- and device-state-sensitive.

The development image came from the development R4's own active
partition.

Users should:

``` text
inspect their own device
→ identify their own active slot
→ dump their own matching boot image
→ preserve a GOLDEN copy
→ patch their own image with Magisk
```

Shipping a generic patched boot image would encourage exactly the kind
of blind partition write this project is trying to prevent.

------------------------------------------------------------------------

# 34. Why the Project Does Not Ship AndroidAutoStub.apk

The stub is proprietary Google software.

The project does not need to redistribute it in order to document or
automate the implementation.

Instead:

``` text
user extracts own compatible stub
        ↓
builder verifies/reference-checks it
        ↓
module is constructed locally
```

Project principle:

> **We provide the implementation, not somebody else's proprietary
> binaries.**

See:

`ANDROID-AUTO-STUB.md`

------------------------------------------------------------------------

# 35. Why the Builder Warns Instead of Rejecting New Stub Hashes

The known-good stub hash is:

``` text
57EA6D176178E52FEDB8B351441141AEFAF8B6E98CFBED10A9FA1B006A608072
```

Future compatible donor firmware may ship a different legitimate stub.

Therefore the builder should distinguish:

``` text
KNOWN-GOOD REFERENCE MATCH
```

from:

``` text
UNTESTED STUB VERSION
```

rather than pretending the reference hash is the only possible valid
Android Auto stub forever.

A mismatch is information.

It is not proof of corruption.

------------------------------------------------------------------------

# 36. Security / Permission Scope

The project deliberately avoids granting two requested privileged
permissions:

``` text
BIND_APPWIDGET
SEND_SMS
```

The tested projection/media functionality works without them.

This does not make the module a security boundary or security product.

Rooting the R4 and introducing a privileged Google package materially
changes the device's security model.

Users should understand that before installing it.

------------------------------------------------------------------------

# 37. Firmware OTA Considerations

A HiBy OTA can replace the patched boot image.

If that happens:

``` text
Magisk disappears
        ↓
systemless module does not mount
        ↓
AndroidAutoStub disappears from effective /product
        ↓
Gearhead may lose system/privileged relationship
        ↓
MANAGE_USB may disappear
        ↓
Android Auto projection can fail again
```

This is why firmware updates should be treated as a new compatibility
event.

Do not blindly reflash a patched boot image from an older firmware.

------------------------------------------------------------------------

# 38. Google Play Update Considerations

Google Play updates are a different case.

The entire architecture is based on the normal Android concept of:

``` text
factory system package
+
updated /data/app package
```

Therefore Play updates are expected to be compatible with the design.

But future Android Auto releases can still change behavior.

After a significant update, verify:

``` text
SYSTEM
UPDATED_SYSTEM_APP
PRIVILEGED
PRODUCT
MANAGE_USB
```

before assuming the module itself failed.

------------------------------------------------------------------------

# 39. Final Architecture

``` text
                     HiBy R4 firmware
                            │
                            ▼
                     Magisk-patched boot
                            │
                            ▼
                    Magisk systemless overlay
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
 /product/priv-app/             /product/etc/permissions/
 AndroidAutoStub/               privapp-permissions-
 AndroidAutoStub.apk            r4-androidauto.xml
              │                           │
              └─────────────┬─────────────┘
                            ▼
                    Android PackageManager
                            │
                            ▼
            Gearhead = SYSTEM / PRIVILEGED / PRODUCT
                            │
                            ▼
                    MANAGE_USB granted
                            │
                            ▼
                Google Play Android Auto update
                            │
                            ▼
                     /data/app/... Gearhead
                            │
                            ▼
                      UPDATED_SYSTEM_APP
                            │
                            ▼
              privileged/product identity retained
                            │
                            ▼
                 Android Open Accessory connection
                            │
                            ▼
                    Android Auto projection
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
       wired USB                    wireless AA bridge
             │                             │
             └──────────────┬──────────────┘
                            ▼
                  2023 Nissan Rogue SV
                            │
                            ▼
                         WORKING
```

------------------------------------------------------------------------

# 40. What Actually Solved It

The breakthrough was not:

``` text
a magic USB setting
a hidden developer toggle
a runtime permission grant
a different cable
a custom Android Auto APK
a modified Nissan head unit
```

It was recognizing that the R4 already had enough USB/accessory
capability to begin Android Auto negotiation.

The blocker was Android's trust/privilege model.

The successful solution was:

``` text
compatible factory Android Auto stub
+
systemless PRODUCT privileged placement
+
R4-specific privileged permission policy
+
Google Play update inheritance
=
MANAGE_USB
=
working Android Auto projection
```

That is the core technical result of this project.

------------------------------------------------------------------------

# Credits

This project exists because of work from many communities and upstream
projects, including:

-   HiBy R4 users and modding researchers;
-   the 4PDA community and R4 research shared there;
-   Benjamin Erker / bkerler EDL tooling;
-   John Wu / Magisk;
-   Android platform and Android Auto reverse-engineering/debugging work
    throughout the community;
-   Oscar Lara, for the device work, testing, persistence, vehicle
    testing, and the occasional willingness to stare directly into
    Qualcomm 9008;
-   Lyra / ChatGPT, for research synthesis, diagnostics, module design,
    documentation, and repeatedly asking whether we really wanted to
    cross the partition-write line.

------------------------------------------------------------------------

# Closing

The HiBy R4 did not need to become a phone.

It needed Android to believe Android Auto belonged there.

Once PackageManager agreed, the Nissan did too.
