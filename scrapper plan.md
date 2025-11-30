Web Scraping Module for NVIDIA Course Automation

 Overview

 Build a production-ready web scraper to automatically extract NVIDIA 
  course data from learn.nvidia.com and populate the JSON template,   
 eliminating all manual "EDIT_ME" fields.

 What Will Be Created

 New Files (8 files)

 pdf_ingestion_system/
 ├── web_scraper/                          # NEW MODULE
 │   ├── __init__.py                      
 │   ├── scraper.py                       # Main orchestrator
 │   ├── browser_manager.py               # Playwright automation     
 with anti-detection
 │   ├── config.py                        # Configuration loader      
 │   ├── utils.py                         # Retry logic, delays,      
 helpers
 │   ├── validators.py                    # JSON schema validation    
 │   └── parsers/
 │       ├── __init__.py
 │       ├── catalog_parser.py            # Extract course list from  
 catalog
 │       ├── course_parser.py             # Parse individual course   
 pages
 │       └── prerequisite_parser.py       # Extract course 
 relationships
 ├── nvidia_scraper_config.yaml           # Scraper settings (URLs,   
 selectors, delays)
 ├── requirements_scraper.txt             # Dependencies (playwright, 
  beautifulsoup4, etc.)
 └── run_scraper.py                       # CLI: python 
 run_scraper.py

 Key Technologies

 - Playwright: Browser automation (better than Selenium - faster,     
 more reliable)
 - BeautifulSoup4 + lxml: HTML parsing
 - fake-useragent: Rotate user agents for anti-detection
 - tenacity: Retry logic with exponential backoff
 - loguru: Enhanced logging with rotation
 - pydantic: Data validation

 Implementation Phases

 Phase 1: Setup (15 min)

 - Create module structure
 - Install dependencies: playwright, beautifulsoup4, fake-useragent,  
 etc.
 - Run playwright install chromium to download browser

 Phase 2: Configuration (10 min)

 - Create nvidia_scraper_config.yaml with:
   - URLs (catalog, course detail patterns)
   - CSS selectors (need to inspect actual HTML)
   - Politeness settings (2-5 second delays between requests)
   - Anti-detection settings (user agent rotation, stealth mode)      

 Phase 3: Browser Manager (30 min)

 - Playwright wrapper with anti-detection features:
   - Disable automation flags
   - Random user agents
   - Human-like scrolling and delays
   - Screenshot/HTML capture on errors for debugging

 Phase 4: Parsers (45 min)

 - CatalogParser: Extract all course URLs from catalog page
 - CourseParser: Extract from individual course pages:
   - Title, description, learning objectives
   - Duration, price, level, format
   - Prerequisites (course links)
   - Target audience, technical requirements
   - Certificate availability, skills taught
 - PrerequisiteParser: Build relationship graph

 Phase 5: Main Orchestrator (30 min)

 - NVIDIACourseScraper class that:
   a. Scrapes catalog → get course URLs
   b. For each course URL → scrape details
   c. Validates data against JSON schema
   d. Saves progress backups every 10 courses
   e. Outputs nvidia_courses_scraped.json matching your template      
 format

 Phase 6: CLI Entry Point (15 min)

 - run_scraper.py with options:
   - python run_scraper.py - Full scrape
   - python run_scraper.py --dry-run - Test without saving
   - python run_scraper.py --validate-only - Check existing JSON      

 Phase 7: Testing & Tuning (2-3 hours)

 - Run on 2-3 sample courses first
 - Inspect actual HTML structure from NVIDIA Learn
 - Tune CSS selectors to match real page structure
 - Handle edge cases (missing data, different formats)
 - Test full scrape on all courses

 Key Features

 Automation Benefits

 - No more manual JSON editing - Fully automated extraction
 - Regular updates - Run weekly/monthly to refresh course data        
 - Accuracy - Directly from source (no copy-paste errors)
 - Scalability - Handles 38 courses now, 500+ courses in future       

 Anti-Detection Measures

 - Random delays (2-5 seconds between requests)
 - User agent rotation
 - Human-like scrolling behavior
 - Stealth mode (hides automation flags)
 - Respects robots.txt (politeness)

 Error Handling

 - Retry failed requests (3 attempts with exponential backoff)        
 - Save progress backups (recover from crashes)
 - Screenshot + HTML dump on errors (debugging)
 - Detailed logging (track what went wrong)

 Data Quality

 - JSON schema validation (ensure all required fields)
 - Data normalization (durations → hours, prices → USD)
 - Duplicate detection
 - Derived field generation (tags from level/price/format)

 Expected Output

 Before (manual template):
 {
   "id": "gen-ai-explained",
   "url":
 "https://learn.nvidia.com/courses/course-detail?course_id=EDIT_ME",  
   "description": "EDIT_ME - Course description here",
   "learning_objectives": ["EDIT_ME - Objective 1", "EDIT_ME -        
 Objective 2"]
 }

 After (automated scraping):
 {
   "id": "course-v1:DLI+S-FX-01+V1",
   "url": "https://learn.nvidia.com/courses/course-detail?course_id=c 
 ourse-v1:DLI+S-FX-01+V1",
   "description": "Learn the fundamentals of generative AI, including 
  how large language models work, their applications, and ethical     
 considerations.",
   "learning_objectives": [
     "Understand the architecture of transformer models",
     "Explore various generative AI applications",
     "Learn about prompt engineering techniques"
   ],
   "duration": "2 Hours",
   "duration_hours": 2.0,
   "price": "Free",
   "cost_usd": 0.0
 }

 Usage After Implementation

 One-Time Setup

 cd pdf_ingestion_system
 pip install -r requirements_scraper.txt
 playwright install chromium

 Run Scraper

 # Full scrape (takes ~10-20 minutes for 38 courses)
 python run_scraper.py

 # Test mode (no saving)
 python run_scraper.py --dry-run

 # Output: nvidia_courses_scraped.json

 Integrate with Existing System

 # After scraping, import to database
 python json_importer.py nvidia_courses_scraped.json

 Schedule Regular Updates

 # Cron job (Linux/Mac) - run weekly on Sundays at 2am
 0 2 * * 0 cd /path/to/project && python run_scraper.py

 Risks & Mitigations

 | Risk                        | Mitigation
                         |
 |-----------------------------|------------------------------------- 
 ------------------------|
 | Website structure changes   | Modular parsers - update selectors   
 in config.yaml           |
 | Rate limiting / IP blocking | Polite delays (2-5s), user agent     
 rotation                   |
 | Missing data fields         | Fallback extraction strategies,      
 sensible defaults           |
 | Scraping fails mid-run      | Progress backups every 10 courses    
                         |
 | Legal concerns              | Respect robots.txt, reasonable rate  
 limits, educational use |

 Timeline

 - Implementation: 2-3 hours (phases 1-6)
 - Testing & Tuning: 2-3 hours (phase 7)
 - Total: ~5-6 hours

 Next Steps After Approval

 1. Create all module files with scraper code
 2. Install dependencies
 3. Run test scrape on 2-3 courses
 4. Inspect actual HTML and tune selectors
 5. Run full scrape
 6. Validate output matches your template
 7. Integrate with existing import pipeline