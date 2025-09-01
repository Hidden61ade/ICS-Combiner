import os
from ics import Calendar, Event
from datetime import datetime
import pytz

def load_calendars(path):
    calendars = []
    for filename in os.listdir(path):
        if filename.endswith('.ics'):
            with open(os.path.join(path, filename), 'r', encoding='utf-8') as f:
                calendars.append(Calendar(f.read()))
    return calendars

def events_overlap(event1, event2):
    # Convert to aware datetimes for comparison
    start1 = event1.begin.astimezone(pytz.utc)
    end1 = event1.end.astimezone(pytz.utc)
    start2 = event2.begin.astimezone(pytz.utc)
    end2 = event2.end.astimezone(pytz.utc)
    return max(start1, start2) < min(end1, end2)

def find_conflicts(events):
    conflicts = []
    for i in range(len(events)):
        for j in range(i+1, len(events)):
            if events_overlap(events[i], events[j]):
                conflicts.append((events[i], events[j]))
    return conflicts

def main():
    path = input("Enter the path to your ICS files: ").strip()
    calendars = load_calendars(path)
    all_events = []
    for cal in calendars:
        all_events.extend(list(cal.events))

    conflicts = find_conflicts(all_events)
    if conflicts:
        print("Conflicting schedules found:")
        for e1, e2 in conflicts:
            print(f"\nConflict between:\n- {e1.name} ({e1.begin} - {e1.end})\n- {e2.name} ({e2.begin} - {e2.end})")
        print("\nResolve conflicts before combining.")
    else:
        combined = Calendar()
        for event in all_events:
            combined.events.add(event)
        output_path = os.path.join(path, "combined.ics")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(combined.serialize_iter())
        print(f"No conflicts found. Combined calendar saved to {output_path}")

if __name__ == "__main__":
    main()