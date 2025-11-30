# NVIDIA Course Web Scraper

Automatically extracts NVIDIA Deep Learning Institute course data from learn.nvidia.com and generates JSON template files.

## Features

- **Fully Automated**: No manual JSON editing required
- **Anti-Detection**: User agent rotation, stealth mode, human-like delays
- **Robust**: Retry logic, error recovery, progress backups
- **Comprehensive**: Extracts all course metadata including descriptions, prerequisites, objectives
- **Production-Ready**: Logging, validation, configurable settings

## Quick Start

### 1. Install Dependencies

```bash
cd pdf_ingestion_system
pip install -r requirements_scraper.txt
playwright install chromium
```

### 2. Run Scraper

```bash
python run_scraper.py
```

That's it! The scraper will:
1. Visit learn.nvidia.com catalog
2. Extract all course URLs
3. Scrape each course page
4. Save to `nvidia_courses_scraped.json`

### 3. Import to Database

```bash
python json_importer.py nvidia_courses_scraped.json
```

## Usage

### Basic Commands

```bash
# Full scrape (headless browser)
python run_scraper.py

# Test run (no saving)
python run_scraper.py --dry-run

# Show browser window (for debugging)
python run_scraper.py --visible

# Limit to 10 courses (for testing)
python run_scraper.py --max-courses 10

# Scrape and auto-import to database
python run_scraper.py --import

# Validate existing output
python run_scraper.py --validate
```

### Custom Configuration

```bash
python run_scraper.py --config my_custom_config.yaml
```

## Configuration

Edit `nvidia_scraper_config.yaml` to customize:

### URLs
```yaml
urls:
  catalog: "https://learn.nvidia.com/catalog"
  course_detail: "https://learn.nvidia.com/courses/course-detail?course_id={course_id}"
```

### Scraping Behavior
```yaml
scraping:
  delay_between_requests:
    min: 2.0    # Minimum delay (seconds)
    max: 5.0    # Maximum delay
  max_retries: 3
  max_courses: 100  # Safety limit
```

### Browser Settings
```yaml
browser:
  headless: true   # Set to false to see browser
  timeout: 30000   # Page load timeout (ms)
```

### CSS Selectors

**IMPORTANT**: You'll need to update these after inspecting the actual NVIDIA Learn website HTML structure.

```yaml
parsing:
  catalog:
    course_card: ".course-card, .catalog-item"
    course_title: "h3, .course-title"
    course_url: "a[href*='course-detail']"

  course_detail:
    title: "h1, .course-title"
    description: ".description, .course-description"
    learning_objectives: ".objectives ul li"
    duration: ".duration, .course-duration"
    price: ".price, .cost"
    # ... etc
```

## Output Format

The scraper generates JSON matching your template structure:

```json
{
  "metadata": {
    "source": "nvidia_learn_website_scraper",
    "extraction_date": "2025-11-13",
    "total_courses": 38,
    "scraper_version": "1.0.0"
  },
  "courses": [
    {
      "id": "course-v1:DLI+S-FX-01+V1",
      "title": "Generative AI Explained",
      "url": "https://learn.nvidia.com/courses/...",
      "description": "Learn the fundamentals of generative AI...",
      "learning_objectives": [
        "Understand transformer architecture",
        "Explore generative AI applications"
      ],
      "duration": "2 Hours",
      "duration_hours": 2.0,
      "price": "Free",
      "cost_usd": 0.0,
      "level": "Beginner",
      "prerequisites": [],
      "skills_taught": ["generative AI", "transformers"],
      "certificate": true,
      "tags": ["beginner", "free", "certificate"]
    }
  ]
}
```

## Troubleshooting

### No Courses Found

**Problem**: Scraper returns 0 courses

**Solutions**:
1. **Inspect HTML**: Visit learn.nvidia.com and inspect page structure
2. **Update Selectors**: Modify CSS selectors in `nvidia_scraper_config.yaml`
3. **Test Visible Mode**: Run with `--visible` to see what's happening
4. **Check Logs**: Review `scraper_logs/scraper_YYYYMMDD.log`

### Selector Not Working

**Problem**: Specific field not extracted (e.g., description empty)

**Debug Process**:
```bash
# 1. Run in visible mode with limited courses
python run_scraper.py --visible --max-courses 1

# 2. Check debug screenshots
# → scraper_logs/debug/*.png

# 3. Inspect page HTML
# → scraper_logs/debug/*.html

# 4. Update selector in nvidia_scraper_config.yaml
```

### Rate Limiting / Blocked

**Problem**: NVIDIA website blocks scraper

**Solutions**:
1. **Increase Delays**: Set `delay_between_requests.min` to 5-10 seconds
2. **Reduce Concurrency**: Scraper is already sequential, so this shouldn't happen
3. **Check robots.txt**: Ensure scraping is allowed
4. **Contact NVIDIA**: Request official API access

### Browser Launch Fails

**Problem**: `playwright` errors

**Solution**:
```bash
# Reinstall playwright browsers
playwright install --force chromium

# Or try different browser
# (modify browser_manager.py to use 'firefox' instead of 'chromium')
```

## Architecture

### Module Structure
```
web_scraper/
├── browser_manager.py    # Playwright automation
├── scraper.py            # Main orchestrator
├── config.py             # Configuration loader
├── utils.py              # Helper functions
├── validators.py         # Data validation
└── parsers/
    ├── catalog_parser.py  # Extract course URLs
    └── course_parser.py   # Extract course details
```

### Data Flow
```
1. Load Configuration (nvidia_scraper_config.yaml)
   ↓
2. Start Browser (Playwright with anti-detection)
   ↓
3. Navigate to Catalog (learn.nvidia.com/catalog)
   ↓
4. Extract Course URLs (catalog_parser.py)
   ↓
5. For Each Course URL:
   a. Navigate to course page
   b. Extract course data (course_parser.py)
   c. Validate data (validators.py)
   d. Save to list
   ↓
6. Save All Courses to JSON
   ↓
7. Close Browser
```

## Advanced Usage

### Scheduling Regular Updates

**Linux/Mac (cron)**:
```bash
# Run every Sunday at 2 AM
0 2 * * 0 cd /path/to/project/pdf_ingestion_system && python run_scraper.py --import
```

**Windows (Task Scheduler)**:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Weekly, Sunday, 2:00 AM
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\project\pdf_ingestion_system\run_scraper.py --import`

### Custom Parser

To add custom extraction logic:

```python
# In course_parser.py, add method:
def _extract_custom_field(self, soup: BeautifulSoup) -> str:
    """Extract your custom field"""
    # Your extraction logic
    return custom_value

# In parse() method, add:
course_data["custom_field"] = self._extract_custom_field(soup)
```

### Testing Selectors

```python
# Test individual selector
from bs4 import BeautifulSoup

html = open('scraper_logs/debug/navigation_error_XXX.html').read()
soup = BeautifulSoup(html, 'lxml')

# Test selector
elements = soup.select('.course-title')
print(f"Found {len(elements)} elements")
for el in elements:
    print(el.get_text(strip=True))
```

## Best Practices

### 1. Be Polite
- **Respect delays**: Use 2-5 second delays between requests
- **Limit frequency**: Don't scrape more than once per day
- **Check robots.txt**: Respect NVIDIA's crawling guidelines

### 2. Validate Output
```bash
# Always validate after scraping
python run_scraper.py --validate
```

### 3. Keep Backups
Scraper automatically creates backups:
- Progress backups every 10 courses
- Final backup after completion
- Location: `scraper_backups/`

### 4. Monitor Logs
```bash
# Check logs for issues
tail -f scraper_logs/scraper_$(date +%Y%m%d).log
```

### 5. Update Selectors Regularly
NVIDIA may change their website structure. If scraping fails:
1. Inspect current HTML
2. Update `nvidia_scraper_config.yaml` selectors
3. Test with `--visible --max-courses 1`

## Performance

### Typical Run Time
- **38 courses**: 10-20 minutes (with 2-5s delays)
- **Per course**: ~15-30 seconds (including delays)

### Optimization Tips
1. **Block Images**: Set `block_images: true` in config (faster, may trigger detection)
2. **Reduce Delays**: Lower delay to 1-2s (faster, higher risk)
3. **Parallel Processing**: Not recommended (risks IP blocking)

## Legal & Ethical Considerations

### Educational Use
This scraper is designed for:
- ✅ Personal learning assistant
- ✅ Academic research
- ✅ Non-commercial course discovery

### Not Recommended For:
- ❌ Commercial course aggregation
- ❌ High-frequency scraping
- ❌ Redistribution of course content

### Respect NVIDIA
- Follow their Terms of Service
- Don't overload their servers
- Consider requesting official API access
- Give attribution when using data

## FAQ

**Q: How often should I run the scraper?**
A: Weekly or monthly is sufficient. Courses don't change that frequently.

**Q: Can I scrape other websites?**
A: Yes! Just modify the URLs and selectors in the config file.

**Q: Will this work with the vision model (Qwen Vision)?**
A: Not yet, but that's planned for v2.0! Vision model will auto-detect selectors.

**Q: How do I know if selectors are working?**
A: Run with `--visible --max-courses 1` and watch the browser.

**Q: Can I use Selenium instead of Playwright?**
A: Yes, but you'll need to rewrite `browser_manager.py`. Playwright is recommended (faster, more reliable).

## Support

**Issues**: https://github.com/your-repo/issues
**Logs**: `pdf_ingestion_system/scraper_logs/`
**Backups**: `pdf_ingestion_system/scraper_backups/`

## Version History

- **v1.0.0** (2025-11-13): Initial release
  - Catalog scraping
  - Course detail extraction
  - Anti-detection features
  - JSON output matching template

## Next Steps

After scraping:
1. **Validate**: `python run_scraper.py --validate`
2. **Import**: `python json_importer.py nvidia_courses_scraped.json`
3. **Test**: Query your courses through the chat interface!

---

**Built with**: Playwright, BeautifulSoup, Python 3.8+
**License**: MIT
