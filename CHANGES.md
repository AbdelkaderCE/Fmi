# Announcement Bot Changes - Before and After

## Changes Made

### 1. Age-Based Filtering (3 days)
- **Before**: All announcements were sent, regardless of age
- **After**: Only announcements from the last 3 days are sent

### 2. Source Differentiation
- **Before**: All announcements had the same header
- **After**: Different icons for different sources:
  - 🖥️ CS Department
  - 🏛️ University (main)

### 3. Seen Announcements Cleanup
- Cleaned up 120 old announcements from `seen_announcements.json`
- All announcements were over 100 days old

## Message Format Comparison

### BEFORE (v5.1):
```
📢 New University Announcement! 📢

#Exams

📌 Title: Planning examens Semestre 2
🗓️ Date: 29/04/2025
📡 Source: main

📝 Details:
Le planning des examens...
```

### AFTER (v5.2) - University Announcement:
```
📢 🏛️ New University Announcement! 🏛️ 📢

#Exams

📌 Title: Planning examens Semestre 2
🗓️ Date: 07/02/2026
📡 Source: main

📝 Details:
Le planning des examens...
```

### AFTER (v5.2) - CS Department Announcement:
```
📢 🖥️ New CS Department Announcement! 🖥️ 📢

#Exams

📌 Title: Planning examens Informatique
🗓️ Date: 07/02/2026
📡 Source: CS department

📝 Details:
Le planning des examens...
```

## Key Features

### ✅ Automatic Age Filtering
- Announcements older than 3 days are automatically skipped
- Prevents spam from old content
- Keeps the bot focused on recent news

### ✅ Visual Source Identification
- Quick visual identification at a glance
- 🖥️ icon for Computer Science department
- 🏛️ icon for general university announcements

### ✅ Configurable
- Age limit can be adjusted via `MAX_ANNOUNCEMENT_AGE_DAYS` constant
- Source icons can be customized in `SOURCE_ICONS` dictionary
- Easy to add new sources with custom icons

## Technical Details

### New Functions Added:
1. `parse_announcement_date(date_str)` - Parses dd/mm/yyyy format
2. `is_announcement_recent(date_str, max_days)` - Checks if announcement is recent
3. `get_source_icon(source_name)` - Returns appropriate icon for source

### Configuration Changes:
- `MAX_ANNOUNCEMENT_AGE_DAYS = 3` - Announcement age limit
- `SOURCE_ICONS` - Dictionary mapping source names to icons

### Startup Message:
- New: "Bot v5.2 is starting up... (Filtering announcements older than 3 days)"
- Informs users about the age filtering feature

## Benefits

1. **Reduced Spam**: No more year-old announcements
2. **Better UX**: Visual distinction between sources at a glance
3. **Cleaner Data**: Smaller `seen_announcements.json` file
4. **Relevant Content**: Only recent, actionable information
