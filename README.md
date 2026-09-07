# HiBy-R4-Android-Auto
Native Android Auto projection for the HiBy R4 using a systemless Magisk privileged-app implementation.

## Current Status

**WORKING — September 7, 2026**

Native Android Auto projection has been successfully enabled on the HiBy R4.

### Tested configuration

* HiBy R4
* Firmware 1.80
* Android 12
* Magisk 30.7
* Android Auto 17.5.663214-release
* 2023 Nissan Rogue SV

### Confirmed working

* Native wired Android Auto projection
* Wireless Android Auto using a third-party wireless AA adapter
* Android Auto onboarding
* Vehicle touchscreen/interface
* Google Play Android Auto updates
* Poweramp playback
* Normal reboot persistence
* Privileged `MANAGE_USB` permission survives reboot

Poweramp was used for testing, but nothing in this implementation is Poweramp-specific. Other Android Auto-compatible media applications are expected to work but have not yet been individually verified.

### Known Issues

#### Audio may initially be silent

Android Auto can begin playback with no audible output.

**Current workaround:** operate the volume control on the R4 once after connecting. Audio immediately becomes active and subsequently operates normally.

The cause is currently unknown but appears to involve initial audio-route activation rather than Android Auto projection itself.

#### Location currently does not work correctly

Android Auto and Google Maps launch, but the R4 currently does not provide a usable location.

Location permissions, precise location and Wi-Fi-assisted location have been enabled during testing without resolving the problem.

We have **not yet determined the cause**. Possible causes include the R4's hardware configuration, Android location/GNSS implementation, HiBy firmware, or additional system integration normally present on Android Auto-certified phones.

Location is being investigated separately.

The known-good Android Auto module will **not** be modified simply to experiment with location support.

---

## What This Is

This project enables the HiBy R4 to operate as the **Android Auto projection device**.

It is not:

* Bluetooth audio
* USB DAC mode
* screen mirroring
* Headunit Reloaded
* an Android Auto receiver

The R4 itself runs Android Auto and projects Android Auto to the vehicle.

Both of the following have now been tested successfully:

`R4 → USB → vehicle → Android Auto`

and:

`R4 → wireless AA adapter → vehicle → Android Auto`

---

> **We provide the implementation, not somebody else's proprietary binaries.**

Users obtain required proprietary components from their own devices or their respective official sources.

---

*A small step for an audiophile and an AI; a giant leap for DAPkind.*

**Oscar Lara + Lyra / ChatGPT — September 2026**
