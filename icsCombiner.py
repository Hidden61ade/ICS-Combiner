import os
import re
from datetime import datetime, timedelta
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox

def parse_ics_file(file_path):
    """Parse ICS file and extract event information"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        events = []
        
        # Find all VEVENT blocks
        vevent_pattern = r'BEGIN:VEVENT(.*?)END:VEVENT'
        vevent_matches = re.findall(vevent_pattern, content, re.DOTALL)
        
        for vevent_content in vevent_matches:
            event_data = {}
            
            # Extract SUMMARY
            summary_match = re.search(r'SUMMARY(?:;[^:]*)?:(.+)', vevent_content)
            if summary_match:
                event_data['summary'] = summary_match.group(1).strip()
            
            # Extract LOCATION
            location_match = re.search(r'LOCATION:(.+)', vevent_content)
            if location_match:
                event_data['location'] = location_match.group(1).strip()
            
            # Extract DTSTART
            dtstart_match = re.search(r'DTSTART(?:;[^:]*)?:(\d{8}T\d{6})', vevent_content)
            if dtstart_match:
                dt_str = dtstart_match.group(1)
                event_data['start'] = parse_datetime(dt_str)
            
            # Extract DTEND
            dtend_match = re.search(r'DTEND(?:;[^:]*)?:(\d{8}T\d{6})', vevent_content)
            if dtend_match:
                dt_str = dtend_match.group(1)
                event_data['end'] = parse_datetime(dt_str)
            
            # Extract RRULE (for recurring events)
            rrule_match = re.search(r'RRULE:(.+)', vevent_content)
            if rrule_match:
                event_data['rrule'] = rrule_match.group(1).strip()
            
            # Extract UID for uniqueness
            uid_match = re.search(r'UID:(.+)', vevent_content)
            if uid_match:
                event_data['uid'] = uid_match.group(1).strip()
            
            if 'start' in event_data and 'end' in event_data:
                events.append(event_data)
        
        return events
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def parse_datetime(dt_str):
    """Parse YYYYMMDDTHHMMSS format to datetime object"""
    year = int(dt_str[0:4])
    month = int(dt_str[4:6])
    day = int(dt_str[6:8])
    hour = int(dt_str[9:11])
    minute = int(dt_str[11:13])
    second = int(dt_str[13:15])
    return datetime(year, month, day, hour, minute, second)

def expand_recurring_events(events, weeks=16):
    """Expand recurring events for the specified number of weeks"""
    expanded_events = []
    
    for event in events:
        expanded_events.append(event)  # Add the original event
        
        # Check if it's a recurring event
        if 'rrule' in event:
            rrule = event['rrule']
            
            # Parse RRULE for weekly events
            if 'FREQ=WEEKLY' in rrule:
                count_match = re.search(r'COUNT=(\d+)', rrule)
                count = int(count_match.group(1)) if count_match else weeks
                
                # Generate recurring events
                for i in range(1, min(count, weeks)):
                    new_event = event.copy()
                    new_event['start'] = event['start'] + timedelta(weeks=i)
                    new_event['end'] = event['end'] + timedelta(weeks=i)
                    expanded_events.append(new_event)
    
    return expanded_events

def print_weekly_schedule(events, max_weeks=None):
    """Print a formatted weekly schedule"""
    if not events:
        print("No events found")
        return
    
    # Group events by week and day
    schedule = defaultdict(lambda: defaultdict(list))
    
    for event in events:
        start_date = event['start']
        # Calculate week number from Sept 1, 2025
        week_start = datetime(2025, 9, 1)  # Monday Sept 1, 2025
        week_num = (start_date - week_start).days // 7 + 1
        day_name = start_date.strftime('%A')
        
        schedule[week_num][day_name].append(event)
    
    print("\n" + "="*80)
    print("📅 COURSE SCHEDULE - 2025 Fall Semester")
    print("="*80)
    
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Show all weeks by default
    weeks = sorted(schedule.keys())
    if max_weeks is not None:
        weeks = weeks[:max_weeks]

    for week in weeks:
        print(f"\n📚 WEEK {week}")
        print("-" * 50)
        
        for day in days_order:
            if day in schedule[week]:
                events_today = schedule[week][day]
                # Sort by start time
                events_today.sort(key=lambda x: x['start'])
                
                week_start = datetime(2025, 9, 1) + timedelta(weeks=week-1)
                day_offset = days_order.index(day)
                current_date = week_start + timedelta(days=day_offset)
                
                print(f"\n🗓️  {day} - {current_date.strftime('%Y-%m-%d')}")
                print("   " + "-" * 40)
                
                for event in events_today:
                    time_str = f"{event['start'].strftime('%H:%M')}-{event['end'].strftime('%H:%M')}"
                    summary = event.get('summary', 'Unknown Course')
                    location = event.get('location', '')
                    
                    print(f"   {time_str} - {summary}")
                    if location:
                        print(f"     📍 {location}")

def check_conflicts(events):
    """Check for scheduling conflicts"""
    conflicts = []
    
    for i in range(len(events)):
        for j in range(i+1, len(events)):
            e1, e2 = events[i], events[j]
            
            # Check if events overlap in time
            if (e1['start'] < e2['end'] and e2['start'] < e1['end']):
                # Extract course code from summary to check if it's the same course
                course1 = extract_course_code(e1.get('summary', ''))
                course2 = extract_course_code(e2.get('summary', ''))
                
                # If it's the same course, it's not a conflict (just different classroom options)
                if course1 != course2:
                    conflicts.append((e1, e2))
    
    return conflicts

def extract_course_code(summary):
    """Extract course code from summary (e.g., CSC3150, ECE3810)"""
    # Look for pattern like CSC3150, ECE3810, etc.
    match = re.search(r'([A-Z]{3}\d{4})', summary)
    return match.group(1) if match else summary

def create_combined_ics(events, output_path):
    """Create a combined ICS file from all events"""
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//ICS Combiner//ICS Combiner 1.0//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
"""
    
    for event in events:
        ics_content += "BEGIN:VEVENT\n"
        uid = event.get('uid')
        if uid:
            uid = f"{uid}-{event['start'].strftime('%Y%m%dT%H%M%S')}"
        else:
            uid = f"event-{hash(str(event))}"
        ics_content += f"UID:{uid}@ics-combiner\n"
        ics_content += f"DTSTART:{event['start'].strftime('%Y%m%dT%H%M%S')}\n"
        ics_content += f"DTEND:{event['end'].strftime('%Y%m%dT%H%M%S')}\n"
        ics_content += f"SUMMARY:{event.get('summary', 'Event')}\n"
        if event.get('location'):
            ics_content += f"LOCATION:{event['location']}\n"
        ics_content += f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}\n"
        ics_content += "END:VEVENT\n"
    
    ics_content += "END:VCALENDAR"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ics_content)

def combine_ics(path, max_weeks=None):
    if not os.path.exists(path):
        return False, f"❌ Path not found: {path}"

    log_lines = []
    log_lines.append(f"🔍 Looking for ICS files in: {path}")

    # Find all ICS files
    ics_files = [f for f in os.listdir(path) if f.lower().endswith('.ics') and f != 'combined.ics']
    log_lines.append(f"📂 Found {len(ics_files)} ICS files")

    if not ics_files:
        return False, "❌ No ICS files found in the specified directory"

    all_events = []

    # Parse each file
    for filename in ics_files:
        file_path = os.path.join(path, filename)
        events = parse_ics_file(file_path)
        log_lines.append(f"📄 {filename}: {len(events)} events")
        all_events.extend(events)

    log_lines.append(f"\n📊 Total base events: {len(all_events)}")

    if not all_events:
        return False, "❌ No events found in any files"

    # Expand recurring events
    expanded_events = expand_recurring_events(all_events)
    log_lines.append(f"📊 Total events (including recurring): {len(expanded_events)}")

    # Check for conflicts
    conflicts = check_conflicts(expanded_events)
    if conflicts:
        log_lines.append(f"\n⚠️  WARNING: {len(conflicts)} scheduling conflicts found!")
        log_lines.append("="*50)
        for i, (e1, e2) in enumerate(conflicts[:5], 1):  # Show first 5 conflicts
            log_lines.append(f"{i}. {e1['summary']} vs {e2['summary']}")
            log_lines.append(f"   📅 {e1['start'].strftime('%Y-%m-%d %H:%M')} - {e1['end'].strftime('%H:%M')}")
            log_lines.append(f"   📅 {e2['start'].strftime('%Y-%m-%d %H:%M')} - {e2['end'].strftime('%H:%M')}")
            log_lines.append("")
        if len(conflicts) > 5:
            log_lines.append(f"   ... and {len(conflicts) - 5} more conflicts")
        log_lines.append("\n⚠️  Please resolve conflicts before combining calendars.")
        return False, "\n".join(log_lines)

    # Create combined ICS file (expanded events for full semester)
    output_path = os.path.join(path, "combined.ics")
    create_combined_ics(expanded_events, output_path)
    log_lines.append(f"\n✅ No scheduling conflicts detected!")
    log_lines.append(f"💾 Combined calendar saved to: {output_path}")
    log_lines.append(f"📦 Combined file contains {len(expanded_events)} events (expanded for full semester)")

    if max_weeks is None:
        log_lines.append("\n(Full schedule printed in console mode only.)")
    return True, "\n".join(log_lines)


def run_gui():
    root = tk.Tk()
    root.title("ICS Combiner")
    root.geometry("720x520")

    path_var = tk.StringVar()

    def browse_folder():
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)

    def run_combine():
        path = path_var.get().strip()
        if not path:
            messagebox.showwarning("Missing Path", "Please select a folder containing .ics files.")
            return
        ok, output = combine_ics(path)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, output)
        if ok:
            messagebox.showinfo("Done", "Combined calendar created successfully.")
        else:
            messagebox.showwarning("Issue", "Conflicts detected or no events found. See details below.")

    header = tk.Label(root, text="ICS Combiner", font=("Segoe UI", 16, "bold"))
    header.pack(pady=10)

    frame = tk.Frame(root)
    frame.pack(fill=tk.X, padx=12)

    path_entry = tk.Entry(frame, textvariable=path_var)
    path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    browse_btn = tk.Button(frame, text="Browse", command=browse_folder)
    browse_btn.pack(side=tk.LEFT, padx=8)

    run_btn = tk.Button(root, text="Combine", command=run_combine)
    run_btn.pack(pady=10)

    output_text = tk.Text(root, wrap=tk.WORD)
    output_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

    root.mainloop()


def main():
    path = input("Enter the path to your ICS files (or press Enter for GUI): ").strip()

    if not path:
        run_gui()
        return

    ok, output = combine_ics(path)
    print(output)

if __name__ == "__main__":
    main()