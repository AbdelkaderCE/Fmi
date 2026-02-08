# FMI Announcement Bot

A Telegram bot that monitors university announcement pages and sends notifications to Telegram groups.

## Features

- **Multi-source monitoring**: Monitor multiple announcement pages simultaneously
- **Age-based filtering**: Only sends announcements from the last 3 days (configurable)
- **Source differentiation**: Visual icons distinguish CS department (🖥️) from university (🏛️) announcements
- **Persistent tracking**: Remembers sent announcements across restarts
- **Smart hashtags**: Automatically tags announcements based on keywords
- **HTML formatting**: Clean, formatted messages with preview content

## Configuration

### Adding Announcement Sources

Edit `config.json` to add or modify announcement sources:

```json
{
  "announcement_sources": [
    {
      "name": "main",
      "url": "https://fmi.univ-tiaret.dz/index.php"
    },
    {
      "name": "other_page",
      "url": "https://example.com/announcements"
    }
  ],
  "loop_time_seconds": 900,
  "bot_owner_id": "YOUR_TELEGRAM_ID"
}
```

Each source requires:
- `name`: Unique identifier for the source (used in tracking)
- `url`: Full URL of the announcement page

### Environment Variables

Set these as Replit Secrets or environment variables:

- `BOT_TOKEN`: Your Telegram bot token
- `GROUPS_IDS`: Comma-separated list of Telegram group IDs
- `PROXY_IP`: (Optional) Proxy server IP
- `PROXY_PORT`: (Optional) Proxy server port

## How It Works

### Age-Based Filtering

The bot automatically filters announcements based on their age:
- Only announcements from the last **3 days** are sent to Telegram groups
- Older announcements are ignored to prevent spam from outdated content
- The age limit is configurable via `MAX_ANNOUNCEMENT_AGE_DAYS` in `main.py`
- If a date cannot be parsed, the announcement is included (fail-safe behavior)

### Source Differentiation

Each announcement source has a unique icon for easy identification:
- **🖥️ CS Department**: Computer Science department announcements
- **🏛️ University**: Main university announcements
- Icons appear in the message header to quickly distinguish the source

### Announcement Tracking

Each announcement is assigned a unique ID in the format:
```
{source_name}:{title}_{date}
```

This prevents:
- Duplicate notifications when the bot restarts
- ID conflicts between different sources
- Re-sending old announcements

### Persistence

The bot maintains a `seen_announcements.json` file that stores all previously sent announcement IDs. This file persists across restarts, ensuring announcements are only sent once.

### Scraping Logic

The bot looks for table rows with this specific structure:
```html
<tr>
  <td style="border: 1px solid #ababab; text-align: center;">
    <strong>Title</strong>
    <p>Content...</p>
  </td>
  <td>Date</td>
</tr>
```

## Adding a New Source

1. Ensure the new page uses the same HTML structure
2. Add the source to `config.json`:
   ```json
   {
     "name": "department_news",
     "url": "https://your-university.edu/dept/news"
   }
   ```
3. Restart the bot

The bot will automatically:
- Start monitoring the new source
- Track announcements separately by source
- Display the source name in notifications

## First Run Behavior

On first startup, the bot:
1. Loads all current announcements from all sources
2. Sends only the latest announcement
3. Marks all others as "seen" to avoid spam
4. From then on, only sends new announcements

## Example Output

### CS Department Announcement
```
📢 🖥️ New CS Department Announcement! 🖥️ 📢

#Exams #Important

📌 Title: Planning examens Semestre 2
🗓️ Date: 06/02/2026
📡 Source: CS department

📝 Details:
Le planning des examens du semestre 2 est disponible
Consultez le tableau pour les dates et horaires
…

Visit the Announcements Page
```

### University Announcement
```
📢 🏛️ New University Announcement! 🏛️ 📢

#Results

📌 Title: Résultats Master1
🗓️ Date: 07/02/2026
📡 Source: main

📝 Details:
Les résultats sont affichés
…

Visit the Announcements Page
```

## Maintenance

### Cleaning Old Announcements

Run the cleanup script to remove old announcements from the tracking file:
```bash
python3 cleanup_old_announcements.py
```

This script:
- Removes announcements older than 3 days from `seen_announcements.json`
- Keeps the tracking file clean and manageable
- Safe to run periodically (will not affect current functionality)
