# Column Selection Safety Features - Testing Guide

## Branch Info
- **Feature Branch:** `feature/column-selection-safety`
- **Commit:** Last commit includes all safety features

## What's New

### 1. Column Validation in Selection Page (`/column-mapping`)
When you select a column from the dropdown, you'll now see:
- ✓ **Green check** with sample values if column looks good
- ⚠️ **Warning** if column is mostly empty or has invalid format
- **Sample data** showing 1-2 example values from that column

### 2. Real-Time Validation
As you select columns for each field, the form immediately validates:
- **DevEUI:** Must be 16 hex characters
- **Network Key:** Must be 32 hex characters (not a session key)
- **Application Key:** Must be 32 hex characters
- **Empty columns:** Warnings if >50% of values are empty

### 3. Data Audit Report
On the preview page (`/registration-preview`), you'll see:
- **Total devices count**
- **Devices with missing Network Key**
- **Devices with invalid DevEUI format** (not 16 hex chars)
- **Devices with invalid key formats** (not 32 hex chars)
- **Detailed warnings** with explanations

### 4. Form Protection
Before submitting to registration:
- If critical issues detected → Confirmation popup
- Can still proceed if you understand the issues

## How to Test

### With Your Problem CSV File
The provided CSV (`Feuchtesensoren LoRa 2025-SO-52960 keys.csv`) has:
- `OTAA keys` column with actual application keys
- `lora_appkey11` column that's empty
- `lora_nwkskey` network session key

**Expected behavior:**
1. Upload the CSV
2. Select the sheet
3. Go to column mapping
4. **AutoSelect:**
   - `OTAA keys` should be auto-selected for Application Key ✓ (This was the bug fix from before)
   - `lora_nwkskey` should NOT auto-select for Network Key (would warn if manually selected)
5. **You should see:**
   - Sample values appearing under each selection
   - Green checkmarks for valid columns
   - Warnings if you try to select wrong columns

### Test Steps

1. **Rebuild the app from the feature branch code**
   ```bash
   git pull origin feature/column-selection-safety
   # or already on the branch
   ```

2. **Start the application** (local dev or rebuild executable)

3. **Test with the CSV file:**
   - Upload `PRIVATE/2026-02-20 Test Devices/Feuchtesensoren LoRa 2025-SO-52960 keys.csv`
   - Go through the column mapping
   - Notice the sample values and validation messages
   - Proceed to registration preview
   - Check the data audit section for statistics

4. **Try selecting wrong columns:**
   - Select `lora_nwkskey` for the Network Key field
   - You should see: `⚠️ Values don't look like hex keys`
   - Form will warn you on submit

### What to Look For

✅ **Good signs:**
- Column samples are shown when you select a column
- Green validation messages appear
- Data audit shows reasonable statistics
- No crashes on form submission

⚠️ **Issues to report:**
- Sample values don't appear
- Validation messages show for correct columns
- Data audit calculations are wrong
- Any JavaScript errors in browser console

## Merging to Main
Once you confirm everything works correctly, you can:
```bash
git checkout main
git merge feature/column-selection-safety
git push origin main
```

Then rebuild the executable for distribution.
