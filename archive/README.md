# 📦 Archive Directory

This directory contains legacy files and development artifacts from the Pomodoro Timer project.

## 📁 Directory Structure

### `legacy_versions/`
Historical versions of the main application files, organized by development phase:

- **`phase1/`** - MVP development files
  - `main_mvp.py`, `main_mvp_debug.py`, `main_mvp_fixed.py`

- **`phase2/`** - Feature enhancement files  
  - `main_phase2.py`, `main_phase2_windows.py`

- **`phase3_development/`** - Advanced features development
  - Multiple `main_phase3_*.py` and `pomodoro_phase3_*.py` variants
  - Contains experimental and intermediate versions

- **`deprecated_modules/`** - No longer maintained modules
  - `minimal_timer_*.py`, standalone utilities

### `development_tests/`
All test files and testing utilities from the development process:
- Unit tests (`test_*.py`)
- Integration tests (`integration_test.py`, `run_*_test.py`) 
- Test configuration (`conftest.py`)
- Mock modules (`music_player_mock.py`)

### `backup_configs/`
Reserved for configuration file backups

## 🎯 Current Active Files (Root Directory)
- `main.py` - Phase 1 MVP (stable)
- `main_phase2_final.py` - Phase 2 complete (stable)
- `pomodoro_phase3_final_integrated_simple_break.py` - **Latest version** (active development)

## 📝 Notes
- Archive files are kept for reference and potential future use
- Active development should use files in the root directory
- Test files remain accessible but are separated from main codebase
- This organization improves codebase clarity and maintainability

---
*Created during project refactoring - July 24, 2025*