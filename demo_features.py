#!/usr/bin/env python3
"""
Demonstration script showing the new announcement filtering and source differentiation features
"""
from datetime import datetime, timedelta

def parse_announcement_date(date_str):
    """Parse date string in format dd/mm/yyyy and return datetime object."""
    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except (ValueError, TypeError):
        return None

def is_announcement_recent(date_str, max_days=3):
    """Check if announcement is within the max age limit."""
    announcement_date = parse_announcement_date(date_str)
    if not announcement_date:
        return True
    days_old = (datetime.now() - announcement_date).days
    return days_old <= max_days

def get_source_icon(source_name):
    """Get the icon for a specific source."""
    SOURCE_ICONS = {
        "CS department": "🖥️",
        "main": "🏛️"
    }
    return SOURCE_ICONS.get(source_name, "📡")

# Demo announcements
demo_announcements = [
    {
        "source_name": "CS department",
        "title": "Planning examens Semestre 2",
        "date": (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y"),
        "age_days": 1
    },
    {
        "source_name": "main",
        "title": "Résultats Master1",
        "date": (datetime.now() - timedelta(days=2)).strftime("%d/%m/%Y"),
        "age_days": 2
    },
    {
        "source_name": "CS department",
        "title": "Old announcement",
        "date": (datetime.now() - timedelta(days=100)).strftime("%d/%m/%Y"),
        "age_days": 100
    },
    {
        "source_name": "main",
        "title": "Another old announcement",
        "date": "25/12/2024",
        "age_days": 410  # Approximately 1 year old
    }
]

print("=" * 70)
print("ANNOUNCEMENT FILTERING AND SOURCE DIFFERENTIATION DEMO")
print("=" * 70)
print()

print("📋 Processing announcements with 3-day age filter...\n")

for i, ann in enumerate(demo_announcements, 1):
    is_recent = is_announcement_recent(ann['date'], 3)
    source_icon = get_source_icon(ann['source_name'])
    status = "✅ WILL BE SENT" if is_recent else "❌ FILTERED OUT"
    
    print(f"Announcement #{i}:")
    print(f"  Source: {source_icon} {ann['source_name']}")
    print(f"  Title: {ann['title']}")
    print(f"  Date: {ann['date']} (Age: {ann['age_days']} days)")
    print(f"  Status: {status}")
    print()

print("=" * 70)
print("SUMMARY")
print("=" * 70)
recent_count = sum(1 for ann in demo_announcements if is_announcement_recent(ann['date'], 3))
filtered_count = len(demo_announcements) - recent_count
print(f"Total announcements: {len(demo_announcements)}")
print(f"Recent (will be sent): {recent_count}")
print(f"Old (filtered out): {filtered_count}")
print()
print("✨ Source icons help distinguish:")
print("   🖥️ CS Department announcements")
print("   🏛️ University (main) announcements")
print()
