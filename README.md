# ICS Combiner

ICS Combiner is a Python script that merges multiple `.ics` calendar files into a single combined calendar, while providing detailed schedule analysis and conflict detection.

## Features
- **Text-based ICS parsing**: No external dependencies, directly reads ICS file content
- **Formatted schedule display**: Shows weekly course schedule with times, locations, and dates
- **Recurring event expansion**: Automatically expands weekly recurring events for semester planning
- **Smart conflict detection**: Distinguishes between real conflicts and same-course classroom options
- **Combined ICS generation**: Creates a merged calendar file for import into calendar applications
- **Robust error handling**: Handles various encoding issues and malformed ICS files
- **Outlook compatibility**: Successfully processes Outlook-generated ICS files with timezone issues

## Requirements
- Python 3.x (no additional dependencies required)

## Usage
1. Place all your `.ics` files in a single directory
2. Run the script:
   ```bash
   python icsCombiner.py
   ```
3. Enter the path to your ICS files directory
4. View your formatted weekly schedule and any conflicts
5. If no conflicts exist, a `combined.ics` file will be created

## Example Output

```
🔍 Looking for ICS files in: C:\Users\YourName\Calendars
📂 Found 11 ICS files
📄 CSC3150_L01_TU.ICS: 1 events
📄 CSC3150_L01_TH.ICS: 1 events
...

📊 Total base events: 11
📊 Total events (including recurring): 165

================================================================================
📅 COURSE SCHEDULE - 2025 Fall Semester
================================================================================

📚 WEEK 1
--------------------------------------------------

🗓️  Monday - 2025-09-01
   ----------------------------------------
   10:30-11:50 - ENG2001 - English for Academic Purposes II
     📍 Teaching D Bldg 310
   15:30-17:20 - GEA2000 - Modern Chinese History and Culture
     📍 Zhi Xin Bldg 110

🗓️  Tuesday - 2025-09-02
   ----------------------------------------
   10:30-11:50 - CSC3150 - Operating System
     📍 Administration Bldg E205

✅ No scheduling conflicts detected!
💾 Combined calendar saved to: combined.ics
📦 Combined file contains 11 base events (recurring events will be expanded by your calendar app)
```

## Technical Features
- **Manual ICS parsing**: Uses regex patterns to extract event information directly from ICS text
- **Timezone handling**: Automatically handles problematic timezone definitions from Outlook
- **Encoding support**: Handles UTF-8, UTF-8-BOM, and Latin-1 encodings with error recovery
- **Recurring events**: Parses RRULE patterns and expands weekly recurring events
- **Course code extraction**: Identifies course codes (e.g., CSC3150, ECE3810) for intelligent conflict detection
- **ICS generation**: Creates standards-compliant ICS files for calendar import

## Troubleshooting
- **No events found**: Check that your files have the `.ics` extension and contain valid VEVENT blocks
- **Encoding issues**: The script automatically tries multiple encodings and ignores unreadable characters
- **Malformed files**: The script is designed to be tolerant of formatting issues common in Outlook-generated files
- **Import issues**: Generated combined.ics files are compatible with most calendar applications including Google Calendar, Outlook, and Apple Calendar

## License
MIT License
