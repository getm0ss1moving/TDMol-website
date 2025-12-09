# EDM Web Application - Recent Changes

This document describes all the major changes made to the EDM web application.

## Summary of Changes

1. **Full English Translation** - All user-facing content translated to English
2. **Result URL Display** - Added visible result URL in EDM.php with special styling
3. **History Feature** - Added paginated history of previous tasks in index.html
4. **Automatic Cleanup** - Created scripts to automatically delete old files (>3 days)
5. **Unified Styling** - Applied consistent, modern design across all pages

---

## 1. English Translation (processhtml.py)

### Changes Made:
- Translated all Chinese text in `processhtml.py` to English
- Updated HTML `lang` attribute from `zh` to `en`
- Modified both result detail pages and brief overview pages

### Files Modified:
- `processhtml.py`

### Key Translations:
- "分子详情" → "Molecule Details"
- "返回结果概览" → "Back to Results Overview"
- "分子信息" → "Molecule Information"
- "下载 XYZ 文件" → "Download XYZ File"
- "相似分子" → "Similar Molecules"
- "生成的分子" → "Generated Molecules"

---

## 2. Result URL Display (EDM.php)

### Changes Made:
- Added a highlighted box showing the direct result URL
- URL is displayed in a special color (orange) with monospace font
- Users can bookmark this URL to access results directly
- URL is constructed using: `http://[HOST]/bioinf/TDMol/result/[TASK_ID]/brief.html`

### Location in File:
```php
// Line 154-162 in EDM.php
<div class="info-box" style="background-color: #fff9e6; border: 2px solid #ffc107; ...">
    <p><strong>Your Result URL:</strong></p>
    <p style="font-size: 16px; color: #d35400; font-weight: bold; ...">
        <?php echo "http://" . $_SERVER['HTTP_HOST'] . "/bioinf/TDMol/result/" . $timeVar . "/brief.html"; ?>
    </p>
</div>
```

---

## 3. History Feature (index.html)

### Changes Made:
- Added a "Recent Task History" section below the email input field
- Displays task ID, description, number of molecules, creation date
- Supports pagination (5 items per page)
- Each history item has a "View" button that opens the result page

### New Files Created:
- `get_history.php` - Backend script to fetch history data from result directory

### How It Works:
1. JavaScript fetches history from `get_history.php` when page loads
2. `get_history.php` scans the `/var/www/bioinf/TDMol/result/` directory
3. Finds all tasks with `brief.html` and reads their `summary.json`
4. Returns JSON array sorted by creation time (newest first)
5. JavaScript displays data in paginated table

### API Response Format:
```json
{
  "success": true,
  "data": [
    {
      "task_id": "20231208123456",
      "url": "/bioinf/TDMol/result/20231208123456/brief.html",
      "user_input": "A small molecule...",
      "num_molecules": 5,
      "created_time": 1702012345,
      "created_date": "2023-12-08 12:34:56"
    }
  ]
}
```

---

## 4. Automatic Cleanup System

### Created Files:

#### 4.1 `cleanup_old_tasks.py`
- Python script to delete files older than 3 days
- Cleans both `upload/` and `result/` directories
- Logs all deletions to `logs/cleanup.log`
- Shows space freed in human-readable format

**Usage:**
```bash
python3 cleanup_old_tasks.py
```

**Configuration:**
```python
MAX_AGE_DAYS = 3  # Files older than this will be deleted
UPLOAD_DIR = "/var/www/bioinf/TDMol/upload/"
RESULT_DIR = "/var/www/bioinf/TDMol/result/"
```

#### 4.2 `cleanup_trigger.php`
- Web-based cleanup trigger
- Can be called via cron or accessed via browser
- Shows cleanup progress in real-time
- Optional token-based authentication

**Usage:**
```bash
# Via command line
php cleanup_trigger.php

# Via web (from localhost)
curl http://localhost/bioinf/TDMol/cleanup_trigger.php

# Via web with token (if enabled)
curl http://yourserver/bioinf/TDMol/cleanup_trigger.php?token=your_secret_token
```

#### 4.3 `setup_cleanup_cron.sh`
- Shell script to setup automatic daily cleanup
- Adds cron job to run cleanup at 2:00 AM daily

**Setup:**
```bash
chmod +x setup_cleanup_cron.sh
./setup_cleanup_cron.sh
```

**Cron Job Created:**
```
0 2 * * * /usr/bin/python3 /path/to/cleanup_old_tasks.py >> /path/to/logs/cleanup_cron.log 2>&1
```

### Cleanup Logic:
1. Scans directories for all files and folders
2. Checks modification time of each item
3. If older than 3 days (259200 seconds):
   - Files are deleted
   - Directories are recursively deleted
4. Logs each deletion with age and size
5. Reports total files, directories, and space freed

---

## 5. Unified CSS Styling

### Created Files:
- `css/unified-style.css` - Master stylesheet for consistent design

### Design Features:

#### Color Scheme:
- **Primary:** Blue gradient (#3498db to #2980b9)
- **Success:** Green gradient (#27ae60 to #229954)
- **Warning:** Orange gradient (#f39c12 to #e67e22)
- **Danger:** Red gradient (#e74c3c to #c0392b)
- **Background:** Purple gradient (#667eea to #764ba2)

#### Components Styled:
1. **Headers** - Gradient background with text shadow
2. **Buttons** - Gradient with hover effects (lift and shadow)
3. **Cards** - White background with subtle shadow
4. **Info Boxes** - Color-coded with left border accent
5. **Tables** - Striped rows with hover effects
6. **Forms** - Modern inputs with focus states
7. **Pagination** - Bootstrap-style with custom colors

#### Responsive Design:
- Mobile-optimized breakpoints
- Stacks buttons vertically on small screens
- Reduces padding and font sizes on mobile
- Full-width containers on narrow screens

### Files Updated with Unified Styling:
1. `index.html` - Added unified-style.css link
2. `EDM.php` - Replaced inline styles with unified classes
3. `processhtml.py` - Generated HTML includes unified-style.css

### Before/After Comparison:

**Before:**
- Inconsistent colors across pages
- Mix of inline styles and CSS classes
- Different button sizes and styles
- Plain tables without hover effects

**After:**
- Consistent gradient color scheme
- All pages use same CSS framework
- Unified button styles with animations
- Modern card-based layouts
- Professional table styling

---

## File Structure

```
web_apps/
├── css/
│   └── unified-style.css          [NEW] - Master stylesheet
├── index.html                      [MODIFIED] - Added history feature
├── EDM.php                         [MODIFIED] - Added result URL display
├── processhtml.py                  [MODIFIED] - English translation + styling
├── get_history.php                 [NEW] - History data API
├── cleanup_old_tasks.py           [NEW] - Python cleanup script
├── cleanup_trigger.php            [NEW] - PHP cleanup trigger
├── setup_cleanup_cron.sh          [NEW] - Cron setup script
└── CHANGES_README.md              [NEW] - This file
```

---

## Testing Checklist

### 1. English Translation
- [ ] Open any result page - all text should be in English
- [ ] Check brief.html - "Generated Molecules" header
- [ ] Check result_X.html - "Molecule Details" header
- [ ] Verify button text: "Download XYZ File" not "下载 XYZ 文件"

### 2. Result URL Display
- [ ] Submit a new task via index.html
- [ ] On EDM.php waiting page, verify URL is displayed
- [ ] URL should be in orange color with yellow background box
- [ ] Copy URL and open in new tab - should work once results are ready

### 3. History Feature
- [ ] Open index.html
- [ ] Scroll down to "Recent Task History" section
- [ ] Should show list of previous tasks
- [ ] Click "View" button - should open result page
- [ ] If more than 5 tasks, pagination controls should appear
- [ ] Click page numbers - should show different tasks

### 4. Cleanup System
- [ ] Run: `python3 cleanup_old_tasks.py`
- [ ] Check logs/cleanup.log for output
- [ ] Verify files older than 3 days are deleted
- [ ] Run: `php cleanup_trigger.php`
- [ ] Should see text output of cleanup process
- [ ] Setup cron: `./setup_cleanup_cron.sh`
- [ ] Run: `crontab -l` - should show new entry

### 5. Unified Styling
- [ ] Open index.html - check gradient background
- [ ] Hover over buttons - should lift and show shadow
- [ ] Open EDM.php - should match index.html design
- [ ] Open result page - should have same header style
- [ ] Open brief.html - table should have hover effects
- [ ] Resize browser - responsive design should work

---

## Maintenance Notes

### Adjusting Cleanup Period:
Edit `cleanup_old_tasks.py`:
```python
MAX_AGE_DAYS = 7  # Change to 7 days instead of 3
```

### Adjusting History Page Size:
Edit `index.html`:
```javascript
var itemsPerPage = 10;  // Change from 5 to 10
```

### Customizing Colors:
Edit `css/unified-style.css`:
```css
.btn-primary {
    background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
}
```

### Changing Result URL Format:
Edit `EDM.php` line 157:
```php
echo "http://" . $_SERVER['HTTP_HOST'] . "/bioinf/TDMol/result/" . $timeVar . "/brief.html";
```

---

## Security Notes

### Cleanup Trigger Authentication:
By default, `cleanup_trigger.php` only allows access from localhost. To enable token authentication:

1. Edit `cleanup_trigger.php` lines 9-13
2. Uncomment the token authentication code
3. Set a strong secret token
4. Access with: `?token=your_secret_token`

### History API:
`get_history.php` reads the result directory. Consider:
- Adding authentication if needed
- Limiting results to specific user (if user system exists)
- Adding rate limiting to prevent abuse

---

## Support

For questions or issues:
1. Check this README first
2. Review code comments in modified files
3. Check logs in `logs/` directory
4. Contact the development team

---

## Version History

**Version 1.0** (2025-12-08)
- Initial changes implemented
- All 5 major features completed
- Documentation created

---

**End of README**
