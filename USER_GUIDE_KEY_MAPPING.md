# End-User Guide: Understanding LoRaWAN Keys

*For non-technical staff working with device registration*

---

## TL;DR (The Simple Version)

When your software asks "which column has the Application Key?", **look for a column with 32-character hex values that are THE SAME for all devices**. That's your answer.

---

## The Problem (Why This Is Confusing)

Different devices use keys differently, and they have very confusing names:

- **OTAA keys** = "Application Key" (shared across all devices)
- **Network Key** = "lora_nwkskey" (different for each device) 
- **Application Session Key** = "lora_appskey" (sometimes used, sometimes ignored)

The software doesn't know which VALUE to put where **without asking you**. Hence the column selection screen.

---

## For Dragino WL03A Leak Sensors (50 devices)

Your sensors use **LoRaWAN 1.0.3 OTAA** mode. Here's what to do:

### In Your CSV File

Open your Excel/CSV file and find these columns:

| Column Name | Example Value | What It Is |
|---|---|---|
| **OTAA keys** | `D60F739062E3B90BBBAE3B26C4308FAE` | Shared security key (all 50 devices have same value) |
| **lora_nwkskey** | `E1190B75A10FFF4066138DA3836EC843` | Unique security key (EACH device has DIFFERENT value) |

⚠️ **These names might be different** - check your actual CSV column headers!

### When You Upload to the Software

The software shows you a column selection screen. Fill it like this:

```
Application Key Column:  ← Select "OTAA keys"
Network Key Column:      ← Select "lora_nwkskey"  
Device EUI:              ← Select the MAC address column
Device Name:             ← Select product/model name
```

### Why This Works

The Dragino uses this key for joining the network:
- **AppKey (shared)** = The password all 50 sensors already know
- **Network Key (per-device)** = Unique encryption per sensor for operations

---

## Red Flags / Warning Signs

❌ **If the Application Key value is DIFFERENT for each device** → You selected the WRONG column!
- Should be: All devices have the SAME application key value

❌ **If you see an error after registration** → Check ChirpStack:
1. Open ChirpStack web interface
2. Find the device
3. Click "Edit"
4. Look at the keys section
5. Compare with your CSV - do they match?

✅ **If ChirpStack shows:**
- Application Key = `D60F739062E3B90BBBAE3B26C4308FAE` (from your "OTAA keys" column)
- Network Session Key = `E1190B75A10FFF4066138DA3836EC843` (from your "lora_nwkskey" column)

→ Then you did it correctly!

---

## Different Devices = Different Rules

⚠️ **IMPORTANT:** If you're working with DIFFERENT device types later:

| Device | Mode | App Key Column | Network Key Column |
|---|---|---|---|
| **Dragino WL03A** | OTAA 1.0.x | "OTAA keys" | "lora_nwkskey" |
| **Generic 1.0.x** | OTAA 1.0.x | "OTAA keys" or "lora_appkey" | "lora_nwkskey" |
| **1.1.x devices** | OTAA 1.1.x | "lora_appkey" | "lora_nwkskey" |
| **ABP devices** | ABP | Not needed | "lora_nwkskey" |

→ **Always check your device documentation or ask IT!**

---

## What If You Get It Wrong?

**Don't panic.** It's recoverable:

1. Check what got registered in ChirpStack (wrong keys)
2. Tell your software to DELETE these devices
3. Upload again with CORRECT column selection
4. ChirpStack will recreate them with correct keys

It's just data - not permanent damage.

---

## Quick Checklist Before You Upload

- [ ] Do I have the file selected?
- [ ] Can I see 50 rows of device data?
- [ ] Do I see columns: OTAA keys, lora_nwkskey, Device ID?
- [ ] Did I select the right columns in the mapping screen?
- [ ] Are the "OTAA keys" values identical for all devices?
- [ ] Are the "lora_nwkskey" values DIFFERENT for each device?

If all checkboxes pass → You're good to go!

---

## Questions to Ask

**"Which column has the application keys?"**
- Answer: The one where all 50 rows have the SAME 32-character hex value

**"What if I don't know?"**
- Check the CSV column headers
- Look for names containing: "OTAA", "AppKey", "application"
- If still unsure: Screenshot the columns and ask IT support

**"How long does registration take?"**
- 50 devices: ~2-5 minutes (depends on network)
- Watch the progress bar

**"What if registration fails?"**
- Check the error message
- Most common: Wrong Application or Device Profile ID
- Check with ChirpStack admin

---

## Contact IT Support With

If something goes wrong, provide:

1. Screenshot of the column selection screen (before uploading)
2. First 5 rows of your CSV exported as image
3. The error message you saw (if any)
4. Device ID of ONE device that went wrong

→ This helps us fix it 10x faster!

---

*This guide is for LoRaWAN devices. If you have non-LoRaWAN devices (NBIoT, etc.), different rules apply.*
