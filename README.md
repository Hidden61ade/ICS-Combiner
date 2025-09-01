# ICS Combiner

ICS Combiner is a Python script that merges multiple `.ics` calendar files into a single combined calendar, while checking for scheduling conflicts between events.

## Features
- Loads all `.ics` files from a specified directory
- Detects and reports overlapping (conflicting) events
- Combines all events into a single `combined.ics` file if no conflicts are found

## Requirements
- Python 3.x
- [ics](https://pypi.org/project/ics/) library
- [pytz](https://pypi.org/project/pytz/) library

Install dependencies with:
```bash
pip install ics pytz
```

## Usage
1. Place all your `.ics` files in a single directory.
2. Run the script:
   ```bash
   python icsCombiner.py
   ```
3. Enter the path to the directory containing your `.ics` files when prompted.
4. If there are conflicting events, they will be listed and the script will stop. If there are no conflicts, a `combined.ics` file will be created in the same directory.

## Example
```
Enter the path to your ICS files: C:\Users\YourName\Calendars
No conflicts found. Combined calendar saved to C:\Users\YourName\Calendars\combined.ics
```

## License
MIT License
