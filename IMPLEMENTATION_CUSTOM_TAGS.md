# Custom Tags Feature - Implementation Summary

## Overview
Added support for **custom user-defined tags** that can be applied to all registered devices simultaneously. Users can now define up to 4 custom tags with names and values during the registration preview step.

## Features

### 1. **Tag Input Interface** (registration_preview.html)
- Located on the registration preview page, before the "Duplikat-Behandlung" section
- **Max 4 tags** per registration session
- Each tag consists of:
  - **Tag Name** (up to 50 characters)
  - **Tag Value** (up to 100 characters)
  - Examples: `Abteilung: IT-Team`, `Standort: Büro Berlin`, `Projekt: IoT-Gateway`

### 2. **Dynamic Tag Management**
- **Add Tag Button**: Allows users to add additional tag rows (max 4)
- **Remove Button**: Appears on each tag row when more than one exists
- **Client-side Validation**: Enforces maximum of 4 tags with visual feedback

### 3. **Tag Application Process**

#### Step 1: Preview Page (registration_preview.html)
```
User enters custom tags in the form:
┌─────────────────┐  ┌──────────────────────┐
│ Tag Name        │  │ Tag Value            │
├─────────────────┼──────────────────────────┤
│ Abteilung       │  │ IT-Team              │
├─────────────────┼──────────────────────────┤
│ Standort        │  │ Büro Berlin          │
├─────────────────┼──────────────────────────┤
│ Projekt         │  │ IoT-Gateway          │
└─────────────────┴──────────────────────────┘
```

#### Step 2: Form Submission (app.py - start_registration)
- Custom tags are collected as JSON object
- Stored in `customTagsInput` hidden input field
- Parsed and stored in session: `session['custom_tags']`

```python
# Example of stored custom tags:
{
    "Abteilung": "IT-Team",
    "Standort": "Büro Berlin",
    "Projekt": "IoT-Gateway"
}
```

#### Step 3: Device Registration (app.py - register_devices_stream)
- Custom tags from session are retrieved
- **Merged with device-specific tags** from CSV columns
- Applied to every device during registration

```python
# Device tags after merge:
device['tags'] = {
    **column_tags,          # Tags from CSV columns
    **custom_tags           # Custom tags (override if duplicate names)
}
```

#### Step 4: gRPC API Call (grpc_client.py)
- Tags passed to ChirpStack's `create_device()` method
- Tags stored in device metadata in ChirpStack

## Implementation Details

### Frontend Changes
**File: templates/registration_preview.html**

1. **Custom Tags Section (HTML)**
   - Added before registration warning section
   - Styled with green border (#16a34a) to indicate it's optional
   - Includes helpful description and icon

2. **Form Collection (JavaScript)**
   - ID: `customTagsInput` (hidden input)
   - Collects all tag rows and validates before form submission
   - Maximum 4 tags enforced with user alert
   - Serialized as JSON string

3. **Tag Management (JavaScript)**
   - `addTagBtn`: Add new tag row up to max 4
   - `remove-tag`: Dynamically remove tag rows
   - `updateRemoveButtons()`: Shows/hides remove buttons based on tag count

### Backend Changes
**File: app.py**

1. **start_registration() route**
   ```python
   # Parse custom tags JSON from form
   custom_tags_json = request.form.get('custom_tags', '{}')
   custom_tags = json.loads(custom_tags_json)
   session['custom_tags'] = custom_tags
   ```

2. **register_devices_stream() route**
   ```python
   # Retrieve custom tags and merge with device tags
   custom_tags = session.get('custom_tags', {})
   
   # For each device:
   if custom_tags:
       tags.update(custom_tags)
   device['tags'] = tags
   ```

### Styling Changes
**File: static/style.css**

Added styling for custom tag inputs:
- `.tag-row`: Container for tag name/value inputs
- `.tag-name`, `.tag-value`: Dark mode input styling
- `.remove-tag`: Delete button styling with red hover effect
- Focus states with green border (#16a34a)

## User Experience Flow

```
1. User uploads CSV file
   ↓
2. Selects sheet & maps columns
   ↓
3. Arrives at registration preview
   ↓
4. [NEW] Sees "Custom Tags" section
   ↓
5. Enters up to 4 custom tags (optional)
   ├─ Can click "Add Tag" to add more (max 4)
   └─ Can remove tags with delete button
   ↓
6. Optionally selects duplicate handling
   ↓
7. Clicks "Register Devices"
   ↓
8. All devices created with custom tags applied
```

## API Integration

### ChirpStack Tags Structure
Tags are sent to ChirpStack as key-value pairs:
```python
tags = {
    "Abteilung": "IT-Team",          # Custom tag
    "Standort": "Büro Berlin",       # Custom tag
    "location": "Berlin, DE",        # Device-specific tag (from CSV)
}
```

## Advantages

✅ **Batch Tagging**: Apply the same tags to all devices in one registration batch
✅ **Flexible**: Up to 4 custom tags, combined with device-specific tags from CSV
✅ **Non-intrusive**: Completely optional - existing workflows unaffected
✅ **User-friendly**: Simple input interface with client-side validation
✅ **Scalable**: Custom tags merged on per-device basis, not affecting registration performance

## Limitations

⚠️ **Max 4 Tags**: Limited to 4 custom tags per registration
⚠️ **Same for All**: All custom tags apply uniformly to every device in the batch
⚠️ **Override Behavior**: If custom tag name matches device-specific tag, custom value takes precedence

## Example Use Cases

1. **Department Tracking**
   - `Abteilung: IT-Team`, `Manager: John Smith`

2. **Geographic Organization**
   - `Standort: Büro Berlin`, `Region: Deutschland`

3. **Project Management**
   - `Projekt: IoT-Gateway`, `Phase: Pilot`

4. **Device Classification**
   - `Typ: LoRaWAN`, `Version: 1.0.4`

## Testing
Created test script: `test_custom_tags.py`
- Verifies custom tags section appears on preview page
- Tests form submission with custom tags
- Validates tags are passed to backend

## Configuration
No additional configuration required. Feature is enabled by default.

## Future Enhancements
- Per-device custom tags specification
- Tag templates/presets for common scenarios
- Tag editing capability after device creation
- Tag validation rules
