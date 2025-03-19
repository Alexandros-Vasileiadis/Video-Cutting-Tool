# Video-Cutting-Tool

A GUI-based video editing tool for creating sub-clips from videos using marked cut points. Built with PyQt5 and MoviePy.

## Features
- Load videos from current directory
- Play/pause control with seek slider
- Frame-accurate navigation
- Mark multiple cut points
- Export segments with original filename + numbering

## Requirements
- **Windows OS** (Tested on Windows 10/11)
- Python 3.7+ (Anaconda recommended)

## Installation

### 1. Install K-Lite Codec Pack
Download and install the basic version from:
[https://codecguide.com/download_kl.htm](https://codecguide.com/download_kl.htm)

### 2. Create Conda Environment
```bash
conda create -n videoedit python=3.9
```
```bash
conda activate videoedit
```

### 3. Install Dependencies
```bash
pip install opencv-python==4.5.5.64 PyQt5==5.15.7 moviepy==1.0.3
```

## Usage
1. Place video files in the same directory as the script
2. Run the application:
```bash
python code.py
```
3. **Interface Guide**:
   - Left panel: List of video files
   - Right panel: Video player with controls
   - Playback controls: Play/Pause buttons + seek slider
   - Frame navigation: Input frame number and click "Go to Frame"
   - Cut points: Use "Mark Cut" to set cut locations
   - Export: Click "Perform Cuts" to generate segments

4. Workflow:
   1. Select video from left panel
   2. Play video and mark cut points
   3. Click "Perform Cuts" to export segments
   4. Find results in `/output` folder

## File Naming Convention
Exported clips follow this pattern:
```
<original_filename>_<segment_number>.mp4
```
Example: `DJI_0001_1.mp4`, `DJI_0001_2.mp4`

## Technical Specifications
- Input formats: MP4, AVI, MOV, MKV
- Output format: MP4 (H.264 codec)
- Output resolution: Same as source
- Frame rate: Auto-detected from source

## Troubleshooting
**Common Issues**:
- **"Could not open codec" errors**:
  - Reinstall K-Lite Codec Pack
  - Restart computer after installation
  
- **MoviePy version issues**:
  ```bash
  pip uninstall moviepy
  ```
  ```bash
  pip install moviepy==1.0.3
  ```


