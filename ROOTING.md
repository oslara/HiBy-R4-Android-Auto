# Rooting the HiBy R4 (Firmware 1.80)

> \[!CAUTION\] \# READ THIS BEFORE DOING ANYTHING
>
> This procedure modifies the HiBy R4 in ways not supported by HiBy and
> includes an **actual write to a boot partition**. A mistake can make
> the device unbootable, destroy data, complicate recovery, or require
> low-level Qualcomm recovery.
>
> These instructions document **one successful procedure on one HiBy R4
> running firmware 1.80**. They are not a guarantee that the same
> procedure is safe for your device, firmware revision, partition
> layout, active slot, computer, drivers, or future HiBy releases.
>
> **Do your own research before proceeding.**
>
> Verify every filename, hash, partition, slot, image, size, programmer,
> and command yourself. If your output differs from the documented
> output, **STOP and investigate instead of continuing.**
>
> In particular:
>
> -   Never flash another user's boot image.
> -   Never assume your active slot matches the author's.
> -   Never use a Qualcomm Firehose programmer merely because the
>     chipset name looks right.
> -   Never write a partition until you have dumped and verified your
>     own backup.
> -   A successful EDL connection does **not** prove that a Firehose
>     programmer is correct.
> -   Firmware updates may invalidate these instructions.
> -   Do not factory-reset merely because a later Magisk module causes
>     Android Recovery to appear.
>
> This project is provided **AS IS, WITHOUT WARRANTY**. You are
> responsible for what you do with your hardware, software, data,
> warranty, sanity, household harmony, and relationship with whichever
> ancient gods currently administer Qualcomm Emergency Download Mode.
>
> **You chose to root the weird little music brick.**
>
> May the old gods and the new gods have mercy on your eMMC.

------------------------------------------------------------------------

## Scope

This document explains the rooting path used during development of the
HiBy R4 Android Auto project.

The known-good development device was:

-   HiBy R4
-   Firmware 1.80
-   Android 12 / API 31
-   Qualcomm Snapdragon 665 / SM6125 family
-   A/B partition layout
-   eMMC storage
-   Bootloader already unlocked
-   Active slot during development: **B**
-   Magisk 30.7

HiBy lists R4 firmware 1.80 as a September 2, 2026 update.

**The values above describe the development device. They are not
instructions to assume the same values on yours.**

------------------------------------------------------------------------

# Risk Legend

Throughout this guide:

### 🟢 READ-ONLY

Interrogates the device or reads data without intentionally modifying
persistent device storage.

Examples: `getprop`, slot checks, GPT inspection, partition dumps,
hashes.

### 🔵 LOCAL / PC ONLY

Changes files on your computer, not the R4.

Examples: copying the boot image, hashing it, patching it with Magisk.

### 🟡 DEVICE STATE CHANGE

Changes temporary device state but does not intentionally write a
partition.

Examples: rebooting into EDL, changing a Windows USB driver.

### 🟠 ROOT / SYSTEMLESS STATE

Operations involving Magisk after the boot image is successfully
patched.

### 🔴 ACTUAL PARTITION WRITE

Writes directly to persistent flash storage.

**This is the point where a wrong image, partition, slot, programmer, or
interrupted operation can ruin your afternoon.**

### ☢️ RECOVERY / RESTORE WRITE

Emergency restoration of a previously verified backup.

If you are here, you are already having an afternoon.

------------------------------------------------------------------------

# 1. Prerequisites

You should be comfortable with:

-   Windows Command Prompt
-   ADB
-   Fastboot concepts
-   Android A/B slots
-   Qualcomm EDL / Sahara / Firehose
-   partition images
-   SHA-256 hashes
-   Magisk boot-image patching

You will need:

-   Android SDK Platform-Tools
-   Python
-   bkerler/edl
-   a working Qualcomm 9008 USB driver arrangement
-   a compatible SM6125 Firehose programmer
-   Magisk
-   enough disk space for backups
-   a reliable USB cable
-   enough time to stop and investigate if anything looks wrong

Official Android Platform-Tools:

https://developer.android.com/tools/releases/platform-tools

Official Magisk:

https://github.com/topjohnwu/Magisk

bkerler/edl:

https://github.com/bkerler/edl

HiBy support / firmware information:

https://store.hiby.com/apps/help-center

------------------------------------------------------------------------

# 2. Confirm ADB Access

**Risk: 🟢 READ-ONLY**

With USB debugging enabled:

``` bat
adb devices
```

Your R4 should appear as an authorized device.

Do not proceed until ADB communication is reliable.

------------------------------------------------------------------------

# 3. Record the Device State

**Risk: 🟢 READ-ONLY**

Before entering EDL, record information about your own device.

Useful checks include:

``` bat
adb shell getprop ro.build.fingerprint
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.security_patch
adb shell getprop ro.boot.slot_suffix
adb shell getprop ro.boot.slot
adb shell getprop ro.boot.verifiedbootstate
adb shell getprop ro.boot.vbmeta.device_state
adb shell getprop ro.boot.flash.locked
```

Save the output.

On the development R4, important observations included:

``` text
Firmware: 1.80
Active slot: B
ro.boot.flash.locked=0
ro.boot.vbmeta.device_state=unlocked
ro.boot.verifiedbootstate=orange
```

Again:

> **Do not assume your active slot is B merely because the development
> R4 used slot B.**

Determine your own device state.

------------------------------------------------------------------------

# 4. Understand the A/B Layout Before Writing Anything

**Risk: 🟢 READ-ONLY**

The development R4 used an A/B layout.

Observed boot partitions were:

``` text
boot_a
boot_b
```

Each was 64 MiB on the development unit.

The active slot at the time was B, so the matching `boot_b` image was
dumped and patched.

Your job is not to copy that choice.

Your job is to determine:

1.  which slot your device is currently using;
2.  which boot partition corresponds to that slot;
3.  whether your GPT/layout agrees with the documented development
    device.

If any of those are uncertain, stop.

------------------------------------------------------------------------

# 5. Fastboot Is Not the Rooting Method Used Here

During development, Fastboot communication worked well enough to inspect
the device, but:

``` text
fastboot boot
```

and:

``` text
fastboot flash boot_b
```

were rejected by the device with an unknown-command response.

No successful boot-partition write was performed through Fastboot.

**Do not interpret an unlocked bootloader as proof that this R4 accepts
ordinary Fastboot boot/flash commands.**

The successful development path used Qualcomm EDL.

------------------------------------------------------------------------

# 6. Enter Qualcomm EDL Mode

**Risk: 🟡 DEVICE STATE CHANGE**

From a working Android system:

``` bat
adb reboot edl
```

The R4 should leave Android and enumerate as a Qualcomm Emergency
Download device, commonly USB VID/PID:

``` text
05C6:9008
```

On the development Windows system, a WinUSB-compatible driver was used
for the 9008 interface.

Driver configuration varies between Windows installations.

Do not blindly replace drivers for unrelated Qualcomm devices.

------------------------------------------------------------------------

# 7. Firehose Programmer Warning

> \[!CAUTION\] \## DO NOT USE RANDOM OR AUTOMATIC LOADERS
>
> During development, allowing an automatic loader selection chose an
> **incorrect mdm9x05 NAND programmer**.
>
> It failed with an error and, fortunately, no partition write occurred.
>
> The lesson is important:
>
> **"Qualcomm loader accepted" is not the same thing as "correct
> programmer for this R4."**

The successful R4-specific programmer used during development came from
community research for the R4 / SM6125 platform.

Development programmer archive:

``` text
prog_emmc_firehose_Sm6125_ddr_work.zip
```

Archive size:

``` text
244,897 bytes
```

Archive SHA-256:

``` text
71284D7BEDD3502941BAD56CEB8D12AFD0BE255D1AB5D11BFCB301DD97297EAF
```

Extracted programmer SHA-256:

``` text
17741425698012D34F9ADE8F9C31EA4D83660BFBAF7554BD8A49DC8E7C53E42D
```

The programmer identified as:

-   AArch64
-   SM_NICOBAR
-   eMMC

These hashes document the file used successfully during development.

**They do not constitute a promise that a file downloaded from somewhere
else with a similar name is safe.**

Obtain the programmer from a source you trust, independently verify it,
and compare hashes.

Do not proceed if you cannot establish confidence in the programmer.

------------------------------------------------------------------------

# 8. Connect With bkerler/edl

**Risk: 🟢 READ-ONLY, provided you use inspection/read commands only**

The development Windows installation invoked EDL approximately as:

``` bat
py -3.12 "C:\Program Files\edl\edl.py"
```

Your installation path and Python version may differ.

Use the explicit Firehose programmer rather than relying on automatic
loader selection.

Before any partition read or write, verify that EDL identifies the
expected target and storage type.

The development device reported approximately:

``` text
HWID: 0x001750e100000000
CPU: nicobar_IoT_modem
Serial: device-specific
Storage: eMMC
```

The serial number is unique to the device and should obviously differ.

If the platform/storage identification looks wrong:

**STOP.**

Do not try a write "just to see if it works."

------------------------------------------------------------------------

# 9. Inspect the GPT

**Risk: 🟢 READ-ONLY**

Use bkerler/edl's GPT inspection functionality with your explicitly
selected programmer.

The exact CLI syntax can vary with the EDL version you installed, so
check:

``` bat
py -3.12 "C:\Program Files\edl\edl.py" -h
```

and the upstream EDL documentation before proceeding.

On the development device, GPT inspection showed important entries
including:

``` text
boot_a     64 MiB
boot_b     64 MiB
recovery_a
recovery_b
vbmeta_a
vbmeta_b
super
userdata
```

The development layout placed `boot_a` and `boot_b` at different offsets
and identified slot B as active.

**Do not copy raw offsets from another R4 unless you independently
verify your own GPT.**

Partition names are safer than manually copied offsets when the tool can
resolve them correctly, but you still must verify the target.

------------------------------------------------------------------------

# 10. Dump Your Own Active Boot Partition

**Risk: 🟢 READ-ONLY**

This is one of the most important safety steps.

Dump the boot partition corresponding to **your own active slot** using
EDL's partition-read functionality.

For the development device, because slot B was active, the resulting
file was named:

``` text
R4_1.80_boot_b_stock.img
```

Its size was:

``` text
67,108,864 bytes
```

Do not download or use the author's stock boot image.

Do not download or use the author's patched boot image.

**Your backup should come from your R4.**

After dumping:

1.  confirm the expected size;
2.  calculate SHA-256;
3.  make at least one untouched backup copy;
4.  give the backup an unmistakable name;
5.  do not patch your only copy.

Example local Windows hash command:

``` bat
certutil -hashfile R4_1.80_boot_b_stock.img SHA256
```

A sensible local layout is:

``` text
R4_1.80_boot_b_stock.img
R4_1.80_boot_b_GOLDEN.img
R4_1.80_boot_b_for_magisk.img
```

The **GOLDEN** copy should remain untouched.

------------------------------------------------------------------------

# 11. Leave EDL / Return to Android

**Risk: 🟡 DEVICE STATE CHANGE**

Once you have safely dumped the boot image, return the device to Android
using the appropriate EDL reset/reboot operation for your installed EDL
version.

Verify that Android boots normally before continuing.

At this point you should possess a verified stock boot image and have
performed **no intentional boot-partition write**.

That is a very good place to stop, copy your backups somewhere safe, and
double-check everything.

------------------------------------------------------------------------

# 12. Patch Your Boot Image With Magisk

**Risk: 🔵 LOCAL IMAGE MODIFICATION + normal user-file transfer**

Install Magisk from its official project source.

Transfer the `for_magisk` copy of your boot image to the R4.

Use Magisk's **Select and Patch a File** workflow.

Select the boot image dumped from **your own R4 and matching your
current firmware**.

Magisk will produce a patched image.

Copy the patched image back to the PC.

The development device used Magisk 30.7.

The development patched image was 67,108,864 bytes.

Do not compare your patched-image SHA-256 to the author's and expect a
match. Magisk output and source images can differ.

Instead, verify:

-   the file exists;
-   its size is plausible;
-   it is based on your own stock image;
-   Magisk reported a successful patch;
-   you did not accidentally select another device's image.

Keep your original stock and GOLDEN copies untouched.

------------------------------------------------------------------------

# 13. Final Pre-Write Checklist

Everything up to this point was intended to avoid a blind partition
write.

Now stop.

Read this checklist literally.

Before writing the patched boot image, independently confirm:

-   [ ] This is a HiBy R4.
-   [ ] I know the exact firmware currently installed.
-   [ ] I confirmed the current active slot on my own device.
-   [ ] I inspected my own GPT.
-   [ ] I know which boot partition corresponds to my active slot.
-   [ ] I dumped that boot partition from my own device.
-   [ ] I verified the dump size.
-   [ ] I calculated and saved its SHA-256.
-   [ ] I have an untouched GOLDEN backup.
-   [ ] I patched a copy of my own boot image with Magisk.
-   [ ] I verified the patched file is plausible.
-   [ ] I am using the Firehose programmer I independently verified.
-   [ ] EDL identifies the expected Qualcomm target.
-   [ ] EDL identifies the expected eMMC storage.
-   [ ] I understand the next operation writes persistent flash.
-   [ ] I am not merely copying the author's `boot_b` choice.

If any box is unchecked:

**STOP.**

------------------------------------------------------------------------

# 14. ☢️ DANGER ZONE --- ACTUAL BOOT-PARTITION WRITE

**Risk: 🔴 ACTUAL PARTITION WRITE**

> \[!CAUTION\] \# THE NEXT OPERATION IS DIFFERENT
>
> Everything before this section can be completed without intentionally
> replacing the R4's boot partition.
>
> The next operation writes your Magisk-patched image directly to
> persistent flash.
>
> A wrong partition, wrong slot, wrong image, wrong programmer,
> corrupted image, or interrupted operation can leave the R4 unable to
> boot.
>
> **Do not continue because a guide told you to. Continue only because
> you independently verified your own device state.**

Re-enter EDL:

``` bat
adb reboot edl
```

Connect using the same **explicitly verified** Firehose programmer.

Re-run a read-only GPT/target check before writing.

Confirm your active slot and target partition again.

On the development R4:

``` text
active slot = B
target boot partition = boot_b
```

That is an observation, **not a universal command**.

Use bkerler/edl's partition-write command for **your verified target
boot partition** and **your Magisk-patched image**.

Because EDL CLI versions and local paths vary, this guide intentionally
does not provide a blind copy/paste write command with `boot_b`
hard-coded into it.

Consult the exact help for your installed EDL version:

``` bat
py -3.12 "C:\Program Files\edl\edl.py" -h
```

and the upstream bkerler/edl documentation.

Before pressing Enter, read your command from left to right and verify:

``` text
PROGRAMMER → DEVICE → PARTITION → IMAGE
```

Then read it again.

Then, if necessary, pray to the old gods and the new gods.

------------------------------------------------------------------------

# 15. Reboot and Verify Root

**Risk: 🟡 REBOOT / 🟠 ROOT STATE**

After a successful write, reboot the R4.

Allow Android time to start.

Do not panic merely because the first boot takes longer than usual.

Once ADB returns:

``` bat
adb devices
```

Verify Magisk/root:

``` bat
adb shell su -c id
```

A successful rooted shell should report UID 0.

During development, the working result included:

``` text
uid=0
context=u:r:magisk:s0
```

The R4 subsequently survived normal reboots with root intact.

At this point, rooting is complete.

Continue with:

`INSTALL.md`

for the Android Auto module.

------------------------------------------------------------------------

# 16. If It Does Not Boot

Do not immediately factory reset.

Do not start flashing random partitions.

Do not switch programmers because somebody on a forum said "this one
should probably work."

First determine what actually happened.

If Android Recovery appears after installing an Android Auto Magisk
module rather than immediately after the root boot-image write, see:

`RECOVERY.md`

The development project encountered a module-induced boot failure during
testing and recovered without factory-resetting the device.

If the patched boot image itself prevents Android from booting,
restoration of your own verified GOLDEN boot image may be necessary.

That operation is covered conceptually below because it is another
direct partition write.

------------------------------------------------------------------------

# 17. ☢️ Restoring Your Stock Boot Image

**Risk: ☢️ RECOVERY / ACTUAL PARTITION WRITE**

Your GOLDEN image exists for this reason.

Only consider restoration after determining that the boot image is
actually the problem.

You must again verify:

-   device identity;
-   firmware;
-   GPT;
-   target slot;
-   target boot partition;
-   GOLDEN image size;
-   GOLDEN image hash;
-   Firehose programmer.

Then use EDL to write **your own verified GOLDEN boot image** back to
the matching boot partition.

Do not restore the author's boot image.

Do not restore an image from another firmware version.

Do not casually write both A and B "for good measure."

Change the smallest thing necessary to restore the known-good state.

------------------------------------------------------------------------

# 18. Things We Tried That Did NOT Become Part of the Procedure

Development involved several dead ends.

They are documented here so future users do not need to rediscover them.

## Fastboot boot / flash

The development R4 rejected both temporary boot and direct
boot-partition flash commands through Fastboot.

## Automatic EDL loader selection

Automatic selection chose an incorrect mdm9x05 NAND loader.

It failed safely before a write, but demonstrated why automatic loader
selection should not be trusted here.

## KernelSU

KernelSU was not used in the successful implementation.

## Writing system/product partitions

The Android Auto implementation does **not** require physically
modifying `system`, `product`, or `super`.

The final Android Auto solution uses a Magisk systemless overlay.

Do not turn a systemless solution into unnecessary physical partition
writes.

------------------------------------------------------------------------

# 19. Firmware Updates

A HiBy firmware OTA may replace the boot image.

That can remove or disable Magisk root and therefore prevent the Android
Auto Magisk module from loading.

Do not assume a patched boot image from firmware 1.80 is appropriate for
a future firmware release.

For a new firmware:

1.  stop;
2.  obtain/dump the matching new boot image;
3.  verify the new device/partition state;
4.  patch that matching image;
5.  reassess the procedure before writing anything.

Never reuse a patched boot image merely because the hardware model is
still called "R4."

------------------------------------------------------------------------

# 20. Known Development Reference Values

These values exist for comparison and historical documentation.

They are **not defaults to blindly reproduce**.

``` text
Device: HiBy R4
Firmware: 1.80
Android: 12
API: 31
Platform family: Qualcomm SM6125 / trinket
Storage: eMMC
Partition scheme: A/B
Development active slot: B

boot_a size: 67,108,864 bytes
boot_b size: 67,108,864 bytes

Development Firehose archive:
prog_emmc_firehose_Sm6125_ddr_work.zip

Archive SHA-256:
71284D7BEDD3502941BAD56CEB8D12AFD0BE255D1AB5D11BFCB301DD97297EAF

Extracted programmer SHA-256:
17741425698012D34F9ADE8F9C31EA4D83660BFBAF7554BD8A49DC8E7C53E42D

Development Magisk version:
30.7
```

The project does not distribute the author's stock or patched boot
image.

------------------------------------------------------------------------

# 21. Credits

This rooting path was possible because of work by the wider Android and
Qualcomm reverse-engineering communities.

Special thanks to:

-   **www7575 --- 4PDA**, whose HiBy R4-specific research documented a
    workable EDL/root path and helped identify the compatible SM6125
    Firehose approach.
-   **B. Kerler / bkerler** and contributors for the open-source
    Qualcomm EDL / Sahara / Firehose tooling.
-   **John Wu / topjohnwu** and Magisk contributors for Magisk,
    MagiskBoot, and systemless Android modification.
-   The HiBy R4 community for documenting this unusually capable little
    DAP.
-   **Oscar Lara** for hardware testing, EDL execution, boot extraction,
    Magisk deployment, recovery testing, and the repeated willingness to
    press Enter when Lyra said, "Okay, but first let's make sure this
    won't brick the thing."
-   **Lyra / ChatGPT --- OpenAI** for research, comparative analysis,
    troubleshooting, partition/EDL assistance, safety checks, and
    documentation.

------------------------------------------------------------------------

# Final Rule

If your device behaves differently from the documented R4:

**STOP.**

Unexpected output is information.

It is not an invitation to escalate to a more dangerous command.

The goal is to root the R4.

The goal is not to become the proud owner of a very attractive Qualcomm
9008 device.

Good luck.

And may whichever gods handle bootloaders be feeling charitable today.
