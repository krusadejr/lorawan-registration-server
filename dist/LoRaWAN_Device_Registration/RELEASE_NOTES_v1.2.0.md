# Release Notes v1.2.0

**Release Date:** February 20, 2026  
**Version:** 1.2.0  
**Stage:** Beta

## 🎉 Overview

v1.2.0 introduces a **simpler, more reliable approach** to handling LoRaWAN version differences. Instead of complex auto-detection, users now explicitly select their device's LoRaWAN version via a dropdown before registration.

## ✨ Major Features

### 1. LoRaWAN Version Selector (NEW)
- **Dropdown menu** on registration preview page showing all supported LoRaWAN versions
- Users select: 1.0.0, 1.0.1, 1.0.2, 1.0.3, 1.0.4, or 1.1.0
- Selection passed to all devices in current batch
- **Why?** ChirpStack's protobuf API has different field semantics for different versions - user knows their version

### 2. version-aware Key Mapping
- **LoRaWAN 1.0.x:** AppKey → `nwk_key` field (ChirpStack protocol requirement)
- **LoRaWAN 1.1.x:** AppKey → `app_key` field (standard mapping)
- Automatic routing based on user's version selection
- No more guessing or silent failures

### 3. Simplified Architecture
- Removed complex REST API version detection
- Removed auto-detection attempts
- Removed unnecessary diagnostic pages (still accessible for advanced users)
- Focus on user control and transparency

## 🐛 Fixes

- Fixed HTML tag rendering in Device Profile ID messages (clean text instead of HTML code)
- Fixed f-string syntax errors in registration stream
- Removed undefined variable references

## 📊 What's New

| Component | Before | After |
|-----------|--------|-------|
| Version Detection | Auto (unreliable) | User dropdown (explicit) |
| Field Mapping | Guessed from CSV | Based on version + CSV |
| API Calls | 1+ per registration | 0 (gRPC only) |
| User Friction | "Why is it failing?" | "I chose 1.0.3" |

## 🧹 Cleanup

Removed development/testing files:
- BUG_ANALYSIS.md
- TECHNICAL_ANALYSIS.md
- FIX_OTAA_KEY_MAPPING.md (superseded)
- FEATURE_LORAWAN_VERSION_DETECTION.md
- SOLUTION_FLOW_DIAGRAM.txt
- test_otaa_fix.py
- UI_IMPROVEMENT_PROPOSAL.md
- TESTING_SAFETY_FEATURES.md

Kept user-facing docs:
- README.md
- USER_GUIDE_KEY_MAPPING.md
- SOLUTION_SUMMARY.md

## 🔄 Upgrade from v1.1.0

**No breaking changes.** Simply:
1. Update to v1.2.0
2. Restart the application
3. Users will see the LoRaWAN version dropdown before registration

Existing code continues to work with the `is_otaa` fallback.

## 📋 Known Limitations

- Version selection applies to **all devices in a batch**
- Mixed-version batches (1.0.x + 1.1.x in same CSV) not yet supported
- User must know their device profile's LoRaWAN version

## 🚀 To Merge to Main

```bash
git checkout main
git merge feature/lorawan-version-detection
git tag -a v1.2.0 -m "Release v1.2.0: LoRaWAN version dropdown selector"
git push origin main --tags
```

## 🙏 Acknowledgments

Thanks to the team for pushing back on over-engineering and keeping the solution simple!

---

**Next Steps for v1.3.0:**
- Multi-version batch handling
- Version detection caching
- UI warnings for missing version info
