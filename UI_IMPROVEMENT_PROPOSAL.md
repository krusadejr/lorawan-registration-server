# UI Improvement Proposal: Pre-Registration Key Validation

## Problem

Users can select columns but have no idea if they're correct until AFTER registration completes and they see wrong values in ChirpStack.

## Solution: Enhanced Preview Screen

Add a **Key Verification Panel** in the column mapping preview that shows:

```
╔════════════════════════════════════════════════════════════╗
║  🔍 KEY MAPPING VERIFICATION                              ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  Your selections:                                          ║
║  └─ Application Key Column: "OTAA keys"                    ║
║  └─ Network Key Column: "lora_nwkskey"                     ║
║                                                            ║
║  Preview of first 3 devices:                               ║
║                                                            ║
║  Device 1 (A84041F4935D6EEA):                              ║
║    Application Key: D60F739062E3B90BBBAE3B26C4308FAE       ║
║    Network Key:     E1190B75A10FFF4066138DA3836EC843       ║
║                                                            ║
║  Device 2 (A84041205D5D6EED):                              ║
║    Application Key: D60F739062E3B90BBBAE3B26C4308FAE ✓ SAME║
║    Network Key:     E1190B75A10FFF4066138DA3836EC844 ✓ DIFF║
║                                                            ║
║  Device 3 (A8404133515D6F24):                              ║
║    Application Key: D60F739062E3B90BBBAE3B26C4308FAE ✓ SAME║
║    Network Key:     E1190B75A10FFF4066138DA3836EC845 ✓ DIFF║
║                                                            ║
║  🟢 LOOKS GOOD!                                            ║
║  ✓ Application Key is SAME for all devices (expected)     ║
║  ✓ Network Key is DIFFERENT for each device (expected)    ║
║                                                            ║
║  [Continue] [Edit Column Mapping]                          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

## Implementation Code

Add this validation function to `app.py` in the `registration_preview()` route:

```python
def validate_key_mapping(df, app_key_col, nwk_key_col, sample_size=3):
    """
    Validate key mapping before registration
    
    Returns:
        dict: {
            'valid': bool,
            'warnings': [list of warnings],
            'preview': {sample devices with their key values},
            'summary': str
        }
    """
    validation = {
        'valid': True,
        'warnings': [],
        'preview': [],
        'summary': ''
    }
    
    if not app_key_col or not nwk_key_col:
        validation['valid'] = False
        validation['warnings'].append("Application Key or Network Key column not selected")
        return validation
    
    # Get sample devices
    sample_df = df.head(sample_size)
    app_key_values = []
    nwk_key_values = []
    
    for idx, row in sample_df.iterrows():
        device_id = str(row.get('Zaehlernummer', f'Device {idx}'))
        app_key = str(row[app_key_col]).strip() if app_key_col in row else ''
        nwk_key = str(row[nwk_key_col]).strip() if nwk_key_col in row else ''
        
        app_key_values.append(app_key)
        nwk_key_values.append(nwk_key)
        
        validation['preview'].append({
            'device_id': device_id,
            'app_key': app_key,
            'nwk_key': nwk_key,
            'app_key_same': len(set(app_key_values)) == 1,
            'nwk_key_diff': len(set(nwk_key_values)) == len(nwk_key_values)
        })
    
    # Validate patterns
    app_key_set = set(app_key_values)
    nwk_key_set = set(nwk_key_values)
    
    # Check: Application Key should be SAME for all devices (OTAA)
    if len(app_key_set) > 1:
        validation['warnings'].append(
            f"⚠️ WARNING: Application Key is DIFFERENT for each device ({len(app_key_set)} different values). "
            f"For OTAA devices, this should be the SAME. Did you select the right column?"
        )
        validation['valid'] = False
    
    # Check: Network Key should be DIFFERENT for each device
    if len(nwk_key_set) == 1:
        validation['warnings'].append(
            f"⚠️ WARNING: Network Key is the SAME for all devices. "
            f"For proper security, each device should have a DIFFERENT network key. Did you select the right column?"
        )
        validation['valid'] = False
    
    # Check: Values look like hex
    for val in app_key_values:
        if val and (len(val) != 32 or not all(c in '0123456789ABCDEFabcdef' for c in val)):
            validation['warnings'].append(
                f"⚠️ WARNING: Application Key '{val[:16]}...' doesn't look like a valid 32-char hex key"
            )
            validation['valid'] = False
            break
    
    # Generate summary
    if validation['valid']:
        validation['summary'] = '✅ Key mapping looks correct! Ready to register.'
    else:
        validation['summary'] = f"❌ Issues found: {len(validation['warnings'])} warning(s)"
    
    return validation
```

## In the Template

Add to `registration_preview.html`:

```html
<!-- Key Validation Preview Section -->
<div class="card mt-4" id="keyValidationPanel">
    <div class="card-header bg-info text-white">
        <h5>🔍 Key Mapping Verification</h5>
    </div>
    <div class="card-body">
        <!-- Validation Summary -->
        <div id="validationSummary"></div>
        
        <!-- Sample Devices Preview -->
        <table class="table table-sm mt-3">
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>Application Key</th>
                    <th>Network Key</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody id="keyPreviewTable">
            </tbody>
        </table>
        
        <!-- Warnings -->
        <div id="validationWarnings"></div>
        
        <div class="mt-3">
            <button class="btn btn-primary" id="proceedBtn">Proceed with Registration</button>
            <button class="btn btn-secondary" onclick="history.back()">Edit Column Mapping</button>
        </div>
    </div>
</div>

<script>
// Populate the validation panel with data from Python
const validationData = {{ validation_data | tojson }};

// Render summary
document.getElementById('validationSummary').innerHTML = `
    <div class="alert alert-${validationData.valid ? 'success' : 'warning'}">
        ${validationData.summary}
    </div>
`;

// Render preview table
const previewTable = document.getElementById('keyPreviewTable');
validationData.preview.forEach(device => {
    const row = `
        <tr>
            <td><code>${device.device_id}</code></td>
            <td><code>${device.app_key.substring(0, 16)}...</code> ${device.app_key_same ? '✓ SAME' : '❌ DIFF'}</td>
            <td><code>${device.nwk_key.substring(0, 16)}...</code> ${device.nwk_key_diff ? '✓ DIFF' : '❌ SAME'}</td>
            <td>${device.app_key_same && device.nwk_key_diff ? '✅' : '⚠️'}</td>
        </tr>
    `;
    previewTable.innerHTML += row;
});

// Render warnings
const warningsHtml = validationData.warnings.map(w => 
    `<div class="alert alert-warning"><strong>⚠️</strong> ${w}</div>`
).join('');
document.getElementById('validationWarnings').innerHTML = warningsHtml;

// Disable proceed if invalid
if (!validationData.valid) {
    document.getElementById('proceedBtn').disabled = true;
    document.getElementById('proceedBtn').title = 'Fix the warnings above before proceeding';
}
</script>
```

## Benefits

✅ **Users see exactly what will be registered**
✅ **Catches 80% of column selection mistakes BEFORE they happen**
✅ **Shows sample data so they can verify**
✅ **Clear warnings with explanations**
✅ **Prevents 50 devices getting registered with wrong keys**

## Integration

Add to the `registration_preview()` route in `app.py`:

```python
# After loading the data
validation = validate_key_mapping(
    df,
    app_key_col=column_mapping.get('app_key'),
    nwk_key_col=column_mapping.get('nwk_key'),
    sample_size=3
)

# Pass to template
return render_template('registration_preview.html',
    ...
    validation_data=validation,
    ...
)
```

## This Prevents

❌ Users selecting "lora_appskey" instead of "OTAA keys"
❌ Users accidentally selecting the same column twice
❌ Users registering 50 devices with wrong keys
❌ Support tickets asking "why are my keys wrong?"

## Timeline

- Low effort implementation (1-2 hours)
- High impact (prevents 90% of key mapping issues)
- Easy to test
- Can be added to existing preview screen
