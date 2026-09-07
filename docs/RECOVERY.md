# Recovery Guide

This guide covers recovery from problems encountered while rooting the
HiBy R4 or activating the Android Auto Magisk module.

> \[!CAUTION\] \# DO NOT FACTORY RESET JUST BECAUSE ANDROID RECOVERY
> APPEARS
>
> During development, an early Android Auto module caused the R4 to boot
> into Android Recovery with:
>
> ``` text
> Can't load Android system
> ```
>
> The device was recovered **without a factory reset and without
> rewriting Android system/product partitions**.
>
> A recovery screen is evidence that something went wrong. It is not
> automatically evidence that userdata is destroyed.
>
> **Preserve data and make the smallest possible change first.**

------------------------------------------------------------------------

# Recovery Philosophy

When something breaks:

1.  **STOP.**
2.  Record what happened.
3.  Identify the last change made.
4.  Prefer reversing that single change.
5.  Escalate only when the less-invasive recovery path is unavailable.
6.  Do not introduce several new variables at once.

A module problem is not automatically a boot-image problem.

A boot-image problem is not automatically a `super`/`system` problem.

An Android Recovery screen is not an invitation to flash every partition
you can find.

------------------------------------------------------------------------

# Risk Legend

### 🟢 READ-ONLY

Inspection only.

### 🟡 REBOOT / DEVICE STATE

Reboots or temporary device-state changes.

### 🟠 SYSTEMLESS RECOVERY

Removing or disabling Magisk modules without intentionally rewriting
Android partitions.

### 🔴 ACTUAL PARTITION WRITE

Direct persistent flash write.

### ☢️ LAST-RESORT RESTORE

Direct restoration of your own verified stock image.

------------------------------------------------------------------------

# 1. First Question: What Changed Immediately Before the Failure?

Recovery depends heavily on what happened immediately before the
problem.

## Case A --- Failure began after installing/rebooting a Magisk module

Start with:

**Systemless module recovery.**

Do **not** begin by reflashing boot.

## Case B --- Failure began immediately after writing a Magisk-patched boot image

The boot image itself becomes a stronger suspect.

Your own verified stock/GOLDEN boot backup may eventually be needed.

## Case C --- Failure began after a firmware OTA

The firmware may have replaced the patched boot image or changed
assumptions used by the module.

Do not blindly reinstall an old patched image.

## Case D --- Failure began after some unrelated modification

Do not assume this project's recovery steps apply.

Identify what actually changed.

------------------------------------------------------------------------

# 2. Known Development Failure

The first Android Auto module prototype used:

``` text
module.prop
system/product/etc/permissions/privapp-permissions-r4-androidauto.xml
system/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

but its privileged-permission policy was incomplete.

After activation reboot, the development R4 entered splash/reboot cycles
and eventually displayed Android Recovery:

``` text
Can't load Android system
```

Recovery ADB was not usable because the computer was not authorized in
that recovery environment.

The device was **not factory reset**.

Using Recovery's:

``` text
Try again
```

eventually allowed Android to enter a RescueParty-style boot.

Evidence from that boot showed that Android had attempted to reconcile
the systemified Android Auto package.

The exact original boot failure was not proven beyond doubt, but the
incomplete privileged-app policy was a leading cause and the module was
treated as the offending change.

The module was then removed using Magisk's module-removal function.

Normal Android boot and root were restored.

------------------------------------------------------------------------

# 3. If Android Recovery Appears

**Risk: 🟢 READ-ONLY / 🟡 REBOOT**

Do not select:

``` text
Factory data reset
```

as your first response.

If Recovery offers:

``` text
Try again
```

that is the least-destructive first option used successfully during
development.

Try a normal reboot/Retry before escalating.

If Android boots, even in an unusual rescue state, immediately focus on
removing the last Magisk module change.

Do not use the temporary successful boot as an opportunity to experiment
with something else.

------------------------------------------------------------------------

# 4. If Android Boots After "Try Again"

**Risk: 🟠 SYSTEMLESS RECOVERY**

If the failure began immediately after activating a Magisk module,
remove modules before another normal reboot.

During development, the official Magisk command used was:

``` bat
adb shell magisk --remove-modules
```

When root timing during boot was unreliable, the following Windows CMD
recovery loop was used successfully:

``` bat
@echo off
echo Rebooting R4 and waiting for Magisk...
adb reboot
:retry
timeout /t 1 /nobreak >nul
adb shell magisk --remove-modules 2>nul
if errorlevel 1 goto retry
echo Magisk accepted module removal command.
pause
```

This repeatedly waits for Android/Magisk to become available and asks
Magisk to remove installed modules.

Magisk may reboot the device as part of the operation.

> \[!IMPORTANT\] `magisk --remove-modules` removes Magisk modules
> broadly. It is a recovery operation, not a surgical everyday uninstall
> command.
>
> If Android is healthy enough to remove only the known offending module
> safely, that narrower approach is preferable.

After recovery, allow Android to boot fully before doing anything else.

------------------------------------------------------------------------

# 5. Verify Recovery Before Reinstalling Anything

**Risk: 🟢 READ-ONLY**

After Android boots normally:

``` bat
adb devices
```

Then:

``` bat
adb shell su -c id
```

If root is expected, confirm UID 0.

Check whether the offending module remains:

``` bat
adb shell "su -c 'ls -la /data/adb/modules 2>/dev/null'"
```

For this project, also check:

``` bat
adb shell pm path com.google.android.projection.gearhead
```

Do not immediately reinstall the same module.

First determine why it failed.

------------------------------------------------------------------------

# 6. The Malformed ZIP Failure We Caught Before Reboot

Another development problem did **not** become a boot failure because it
was detected during preflight.

A ZIP created with a Windows-oriented archive process contained literal
backslashes in archive entries, for example:

``` text
system\product\priv-app\AndroidAutoStub\AndroidAutoStub.apk
```

Magisk extracted those as malformed filenames rather than the intended
Unix directory hierarchy.

Because the staged module was inspected **before reboot**, activation
was stopped.

This is why `INSTALL.md` requires checking:

``` bat
adb shell "su -c 'find /data/adb/modules_update/r4_androidauto_enabler -maxdepth 8 -type f'"
```

before activation.

Correct paths look like:

``` text
system/product/priv-app/AndroidAutoStub/AndroidAutoStub.apk
```

If you catch malformed paths before reboot:

**DO NOT REBOOT.**

Remove the staged module, rebuild the ZIP with POSIX `/` paths, and
verify again.

Preflight is recovery performed before there is anything to recover
from.

------------------------------------------------------------------------

# 7. If ADB Works but Android Does Not Fully Start

**Risk: 🟢 READ-ONLY → 🟠 SYSTEMLESS RECOVERY**

If ADB becomes available during boot, use that window to inspect or
remove the most recent Magisk module change.

Do not start modifying Android partitions.

Useful read-only checks include:

``` bat
adb devices
adb shell getprop sys.boot_completed
adb shell getprop ro.boot.slot_suffix
```

If Magisk becomes available:

``` bat
adb shell magisk -v
```

If the failure clearly began after a module activation, module removal
remains the first recovery target.

------------------------------------------------------------------------

# 8. If Recovery ADB Says Unauthorized

During the development failure, ADB inside Android Recovery was not
authorized.

That meant Recovery ADB could not be relied upon as the recovery path.

Do not repeatedly alter drivers or issue random ADB commands expecting
authorization to magically appear.

Use the recovery UI's least-destructive reboot option first.

If Android can reach a rescue/partial boot where the previously
authorized ADB environment returns, use that opportunity to remove the
module.

If Android cannot reach any usable boot, escalation may be necessary.

------------------------------------------------------------------------

# 9. If the Problem Began Immediately After Rooting

If the R4 stopped booting immediately after the **Magisk-patched boot
image** was written, and no Android Auto module had yet been activated,
the boot image is a more plausible cause.

At this point:

-   do not factory reset;
-   do not write `system`;
-   do not write `product`;
-   do not write `super`;
-   do not flash both boot slots;
-   do not use somebody else's boot image.

Your own verified stock/GOLDEN boot image is the relevant rollback
artifact.

See the restoration section below.

------------------------------------------------------------------------

# 10. Entering EDL for Recovery

**Risk: 🟡 DEVICE STATE CHANGE**

From a working or partially working Android environment:

``` bat
adb reboot edl
```

If Android cannot execute ADB commands, you may need a hardware route
into the R4's recovery/EDL environment.

The R4's known forced reset/recovery key combination is:

``` text
Power + Next Track
```

held for approximately 15 seconds.

Do not substitute generic Qualcomm key combinations from unrelated
phones merely because they use the same SoC family.

Hardware behavior can differ by device.

------------------------------------------------------------------------

# 11. Before Any EDL Restore

**Risk: 🟢 READ-ONLY**

A direct boot restore is an actual partition write.

Before crossing that line, re-establish what you know.

Verify:

-   device is the expected HiBy R4;
-   firmware version associated with your backup;
-   GPT is readable;
-   active/target slot is understood;
-   target boot partition is identified;
-   Firehose programmer is the independently verified R4-compatible
    programmer;
-   storage identifies as expected eMMC;
-   GOLDEN image came from this device;
-   GOLDEN image size is correct;
-   GOLDEN image SHA-256 matches the value you recorded when it was
    dumped.

If you cannot verify those items, do not write yet.

------------------------------------------------------------------------

# 12. ☢️ Restoring Your Own GOLDEN Boot Image

**Risk: ☢️ ACTUAL PARTITION WRITE**

> \[!CAUTION\] This section involves direct persistent flash
> modification.
>
> It is appropriate only when evidence points to the patched boot image
> itself and less-invasive recovery has failed or is unavailable.

During development, the stock active-slot boot image was dumped
**before** rooting and preserved as a GOLDEN backup.

That is the image intended for this recovery path.

Use bkerler/edl with the same explicitly verified R4-compatible Firehose
programmer used to dump the partition.

Inspect GPT again before writing.

Write:

``` text
YOUR OWN GOLDEN BOOT IMAGE
```

to:

``` text
THE MATCHING BOOT PARTITION FOR THAT IMAGE
```

This guide deliberately does not provide a hard-coded:

``` text
boot_b
```

restore command.

The development device used slot B.

Yours may not.

Do not write both boot slots "just to be safe."

Do not restore an image from another R4.

Do not restore an image from another firmware release.

Do not use a boot image downloaded from this project; the project does
not distribute one.

After a successful restore, reboot and reassess from a known stock-boot
state.

------------------------------------------------------------------------

# 13. What NOT to Do

When the R4 stops booting, avoid turning one failure into five.

Do not:

-   immediately factory reset;
-   blindly reflash `boot_b`;
-   flash both boot slots;
-   write `vbmeta` because a random rooting guide did;
-   disable verity without evidence that it is necessary;
-   modify `super`, `system`, or `product`;
-   use an automatic Firehose loader;
-   use a random "SM6125" programmer;
-   use another user's stock boot image;
-   use another user's patched boot image;
-   change slots merely because the current one failed;
-   keep stacking new Magisk modules on a broken boot;
-   interpret every recovery screen as permanent damage.

The successful Android Auto implementation requires **no physical
system/product partition modification**.

Keep recovery proportional to the thing that actually changed.

------------------------------------------------------------------------

# 14. Android Auto Module Recovery Specifically

If the R4 boots normally after removing modules, confirm the Android
Auto module is gone or disabled before reinstalling anything.

Check:

``` bat
adb shell "su -c 'ls -la /data/adb/modules'"
```

and:

``` bat
adb shell "su -c 'ls -la /data/adb/modules_update 2>/dev/null'"
```

If stale staging data for:

``` text
r4_androidauto_enabler
```

remains, inspect it before removing anything.

The known-good public module is based on the corrected v1.1 privileged
permission policy and proper POSIX ZIP paths.

Do not reinstall an older experimental module.

------------------------------------------------------------------------

# 15. Known-Good v1.1 Permission Policy

The successful module grants the R4 Android Auto package the privileged
permissions required by the tested architecture while explicitly denying
two permissions that were not needed for this implementation.

The important result for Android Auto projection is:

``` text
android.permission.MANAGE_USB = granted
```

Do not "simplify" the policy to a MANAGE_USB-only allowlist.

An early incomplete policy was associated with the development boot
failure.

Likewise, do not add every permission Android Auto requests merely
because it appears in `dumpsys`.

The working policy is documented in the repository.

Change it only when you have evidence and a recovery plan.

------------------------------------------------------------------------

# 16. Recovery After a Firmware OTA

A HiBy firmware update may replace the Magisk-patched boot image.

Possible symptoms include:

-   Magisk root disappears;
-   modules no longer load;
-   Android Auto loses privileged state;
-   Android Auto returns to ordinary application behavior.

That does **not** automatically mean the Android Auto module corrupted
the device.

Check root first:

``` bat
adb shell su -c id
```

If `su` is gone after an OTA, investigate the new firmware's matching
boot image.

Do not flash your old firmware 1.80 patched boot image onto a newer
firmware without first establishing that it is appropriate.

The safe model is:

``` text
new firmware
→ new matching boot image
→ new backup
→ new Magisk patch
→ verify
→ then restore module functionality
```

------------------------------------------------------------------------

# 17. Recovery Data Worth Saving

Before experimenting, keep copies of:

``` text
stock active-slot boot image
GOLDEN untouched boot image
SHA-256 of stock/GOLDEN image
Magisk-patched boot image
SHA-256 of patched image
R4 firmware version
build fingerprint
GPT output
active slot
Firehose programmer hash
known-good Android Auto module ZIP
```

Store at least the GOLDEN boot image and its hash somewhere other than
the R4 itself.

A backup stored only on the device that will not boot is an unusually
decorative backup.

------------------------------------------------------------------------

# 18. Asking for Help

If opening a GitHub issue or community support post, provide facts
rather than only:

``` text
it bricked
```

Useful information includes:

``` text
R4 firmware:
What changed immediately before failure:
Does the HiBy logo appear:
Does Android Recovery appear:
Exact recovery message:
Does "Try again" boot:
Does ADB appear at any point:
Does Magisk become available:
Active slot before the change:
Was a partition written:
If yes, which partition:
Was the image dumped from this same R4:
Firehose programmer SHA-256:
```

Also include relevant logs or command output.

Before publishing diagnostic files, inspect them and remove identifiers
or other information you do not want to share.

------------------------------------------------------------------------

# 19. Recovery Decision Tree

``` text
R4 does not boot normally
        │
        ▼
What changed immediately before failure?
        │
        ├── Magisk module activation
        │       │
        │       ▼
        │   Android Recovery?
        │       │
        │       ├── Yes → DO NOT FACTORY RESET
        │       │          │
        │       │          ▼
        │       │       Try again
        │       │          │
        │       │          ▼
        │       │     Android/ADB returns?
        │       │          │
        │       │          ├── Yes → remove offending module
        │       │          │          → reboot
        │       │          │          → verify
        │       │          │
        │       │          └── No → investigate before escalation
        │       │
        │       └── ADB available during boot?
        │                  │
        │                  └── Yes → remove offending module
        │
        ├── Patched boot image write
        │       │
        │       ▼
        │   Verify own GOLDEN backup + GPT + slot + programmer
        │       │
        │       ▼
        │   Restore matching boot only if evidence supports it
        │
        └── Firmware OTA / other change
                │
                ▼
            Diagnose that change first
```

------------------------------------------------------------------------

# 20. Development Recovery Result

For historical clarity, the development R4 successfully recovered from
the early module failure with:

``` text
No factory reset
No system partition rewrite
No product partition rewrite
No super partition rewrite
No slot change
No vbmeta modification
No stock boot restoration
```

The offending Magisk module was removed, Android returned to normal, and
Magisk root remained functional.

A corrected v1.1 module was later staged, preflight-verified, activated
successfully, and survived subsequent normal reboots.

That is why this guide strongly prefers:

**reverse the last systemless change before escalating to physical flash
writes.**

------------------------------------------------------------------------

# Final Recovery Rule

When something fails:

**change the smallest thing that can plausibly undo the failure.**

Do not reward uncertainty with a more dangerous command.

And if Android Recovery gives you a giant button labeled factory reset
immediately after you spent hours building a perfectly good backup
strategy:

maybe don't press the giant button.
