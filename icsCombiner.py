import os
import re
from datetime import datetime, timedelta
from collections import defaultdict

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

def print_weekly_schedule(events):
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
    
    # Show first few weeks
    for week in sorted(schedule.keys())[:4]:  # Show first 4 weeks
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
        ics_content += f"UID:{event.get('uid', f'event-{hash(str(event))}')}@ics-combiner\n"
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

def main():
    path = input("Enter the path to your ICS files: ").strip()
    
    if not os.path.exists(path):
        print(f"❌ Path not found: {path}")
        return
    
    print(f"� Looking for ICS files in: {path}")
    
    # Find all ICS files
    ics_files = [f for f in os.listdir(path) if f.lower().endswith('.ics') and f != 'combined.ics']
    print(f"📂 Found {len(ics_files)} ICS files")
    
    if not ics_files:
        print("❌ No ICS files found in the specified directory")
        return
    
    all_events = []
    
    # Parse each file
    for filename in ics_files:
        file_path = os.path.join(path, filename)
        events = parse_ics_file(file_path)
        print(f"� {filename}: {len(events)} events")
        all_events.extend(events)
    
    print(f"\n📊 Total base events: {len(all_events)}")
    
    if not all_events:
        print("❌ No events found in any files")
        return
    
    # Expand recurring events
    expanded_events = expand_recurring_events(all_events)
    print(f"📊 Total events (including recurring): {len(expanded_events)}")
    
    # Print schedule
    print_weekly_schedule(expanded_events)
    
    # Check for conflicts
    conflicts = check_conflicts(expanded_events)
    if conflicts:
        print(f"\n⚠️  WARNING: {len(conflicts)} scheduling conflicts found!")
        print("="*50)
        for i, (e1, e2) in enumerate(conflicts[:5], 1):  # Show first 5 conflicts
            print(f"{i}. {e1['summary']} vs {e2['summary']}")
            print(f"   📅 {e1['start'].strftime('%Y-%m-%d %H:%M')} - {e1['end'].strftime('%H:%M')}")
            print(f"   📅 {e2['start'].strftime('%Y-%m-%d %H:%M')} - {e2['end'].strftime('%H:%M')}")
            print()
        if len(conflicts) > 5:
            print(f"   ... and {len(conflicts) - 5} more conflicts")
        print("\n⚠️  Please resolve conflicts before combining calendars.")
    else:
        print(f"\n✅ No scheduling conflicts detected!")
        
        # Create combined ICS file
        output_path = os.path.join(path, "combined.ics")
        create_combined_ics(all_events, output_path)  # Use base events, not expanded
        print(f"💾 Combined calendar saved to: {output_path}")
        print(f"📦 Combined file contains {len(all_events)} base events (recurring events will be expanded by your calendar app)")

if __name__ == "__main__":
    main()