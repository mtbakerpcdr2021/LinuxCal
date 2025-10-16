# Personal Calendar & Task Manager

A simple, user-friendly desktop application for managing appointments and daily tasks.

## Features

- **Visual Monthly Calendar** - Navigate through months with ease
- **Appointment Scheduling** - Click any date to add, view, or remove appointments
- **To Do Today List** - Manage your daily tasks
- **Things to Get Around To** - Keep track of future tasks
- **Persistent Storage** - All your data is automatically saved

## Installation

### Prerequisites

This application requires Python 3 and tkinter. On Ubuntu, install tkinter with:

```bash
sudo apt-get update
sudo apt-get install python3-tk
```

### Running the Application

1. Make the script executable (optional):
```bash
chmod +x calendar_app.py
```

2. Run the application:
```bash
python3 calendar_app.py
```

Or if you made it executable:
```bash
./calendar_app.py
```

## How to Use

### Keyboard Shortcuts

- **F11** - Toggle fullscreen mode
- **Escape** - Exit fullscreen mode

### Calendar & Appointments

1. **Navigate Months**: Use the ◀ and ▶ buttons to move between months
2. **Go to Today**: Click the "Today" button to return to the current month
3. **Select a Date**: Click on any day in the calendar
4. **Add Appointment**: Select a date, then click "Add Appointment" and enter details
5. **Remove Appointment**: Select an appointment from the list and click "Remove"
6. **View Appointments**: Dates with appointments show a dot (•) and are highlighted in yellow

### Task Lists

#### To Do Today
- **Add Task**: Click "Add" button and enter task description
- **Mark Complete**: Select a task and click "✓ Done"
- **Remove Task**: Select a task and click "Remove"

#### Things to Get Around To
- **Add Task**: Click "Add" button for future tasks
- **Move to Today**: Select a task and click "Move to Today" when you're ready to work on it
- **Remove Task**: Select a task and click "Remove"

## Data Storage

All your data is automatically saved to `~/calendar_data.json` in your home directory. Your appointments and tasks will persist between sessions.

## Color Coding

- **Light Blue** - Today's date
- **Light Yellow** - Dates with appointments
- **Light Green** - Currently selected date

## Tips

- The calendar shows appointments with a bullet point (•) next to the date
- All changes are saved automatically
- You can have multiple appointments on the same day
- Tasks can be moved from "Things to Get Around To" to "To Do Today" as priorities change

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'tkinter'`  
**Solution**: Install python3-tk using the command above

**Issue**: App freezes on startup or crashes with json.scanner error  
**Solution**: Corrupted data file. Run the quick fix:
```bash
bash fix_calendar.sh
```
Or manually delete the data file:
```bash
rm ~/calendar_data.json
```
Then restart the app. Your old data will be backed up automatically if found.

**Issue**: Segmentation fault on Linux  
**Solution**: Try these steps:
1. Update tkinter: `sudo apt-get install --reinstall python3-tk`
2. Check display: `echo $DISPLAY` (should show `:0` or similar)
3. Try X11 mode: `GDK_BACKEND=x11 python3 calendar_app.py`

**Issue**: Can't save data  
**Solution**: Make sure you have write permissions in your home directory

## Requirements

- Python 3.6 or higher
- python3-tk (tkinter)
- Ubuntu/Linux with display server (X11 or Wayland)
