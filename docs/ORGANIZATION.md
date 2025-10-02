# Documentation Organization

All documentation has been organized into the `docs/` folder for better structure and maintainability.

---

## 📁 Current Structure

```
draft-killer/
│
├── README.md                     ⬅ Main project overview (ROOT LEVEL)
│
├── docs/                         ⬅ All other documentation
│   ├── README.md                    Index of all documentation
│   │
│   ├── Getting Started/
│   │   ├── QUICKSTART.md           ⭐ Quick start guide
│   │   ├── AUTOMATION_README.md     Setup automation overview
│   │   └── SETUP_VISUAL_GUIDE.md   Visual diagrams & flowcharts
│   │
│   ├── Setup & Configuration/
│   │   ├── SETUP_GUIDE.md          Detailed setup instructions
│   │   └── SETUP_AUTOMATION.md     Technical automation docs
│   │
│   ├── Architecture & Design/
│   │   ├── DEVELOPMENT_NOTES.md     Architecture decisions
│   │   ├── IMPLEMENTATION_OUTLINE.md Complete roadmap
│   │   └── IMPLEMENTATION_STATUS.md  Current status
│   │
│   └── APIs & Research/
│       ├── SPORTSBOOK_RESEARCH_COMPLETE.md  Complete research
│       ├── SPORTSBOOK_API_RESEARCH.md       Detailed analysis
│       ├── SPORTSBOOK_API_SUMMARY.md        Summary
│       └── API_TESTING_README.md            Testing guide
│
├── setup.sh                      Setup automation script
├── start-dev.sh                  Development server launcher
├── docker-compose.yml            PostgreSQL configuration
├── Makefile                      Convenient commands
│
├── backend/                      FastAPI backend
└── frontend/                     Next.js frontend
```

---

## 📚 Documentation Files

### Root Level (1 file)

- **README.md** - Main project overview and quick start

### docs/ Directory (12 files)

**Getting Started:**
- QUICKSTART.md - Quick reference guide
- AUTOMATION_README.md - Setup automation overview
- SETUP_VISUAL_GUIDE.md - Visual diagrams and flowcharts

**Setup & Configuration:**
- SETUP_GUIDE.md - Detailed manual setup
- SETUP_AUTOMATION.md - Technical automation documentation

**Architecture & Design:**
- DEVELOPMENT_NOTES.md - Architecture decisions and rationale
- IMPLEMENTATION_OUTLINE.md - Complete project roadmap
- IMPLEMENTATION_STATUS.md - Current implementation status

**APIs & Research:**
- SPORTSBOOK_RESEARCH_COMPLETE.md - Complete sportsbook API research
- SPORTSBOOK_API_RESEARCH.md - Detailed API comparison
- SPORTSBOOK_API_SUMMARY.md - Executive summary
- API_TESTING_README.md - API testing guide

**Index:**
- README.md - Documentation index and navigation

---

## 🔗 Link Updates

All documentation links have been updated to reflect the new structure:

### In Root README.md

```markdown
[docs/QUICKSTART.md](docs/QUICKSTART.md)
[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)
[docs/IMPLEMENTATION_OUTLINE.md](docs/IMPLEMENTATION_OUTLINE.md)
```

### In docs/ Files

```markdown
[QUICKSTART.md](./QUICKSTART.md)           # Within docs/
[../README.md](../README.md)               # Back to root
```

### In Scripts (setup.sh)

```bash
echo "docs/QUICKSTART.md - Quick reference guide"
echo "docs/SETUP_VISUAL_GUIDE.md - Visual diagrams"
```

---

## ✅ Benefits of This Organization

1. **Cleaner Root Directory**
   - Only essential files at top level
   - README.md as main entry point
   - Scripts and configs easily visible

2. **Better Documentation Discovery**
   - docs/README.md as comprehensive index
   - Logical categorization
   - Easy to find specific docs

3. **Easier Maintenance**
   - All docs in one place
   - Consistent relative paths
   - Simpler to update links

4. **Professional Structure**
   - Standard open-source layout
   - Clear separation of concerns
   - Better for new contributors

---

## 🎯 Quick Navigation

**From Root:**
```bash
# View all documentation
ls docs/

# Read quick start
cat docs/QUICKSTART.md

# Open in editor
code docs/
```

**From docs/:**
```bash
# View index
cat README.md

# List all docs
ls -lh

# Search for content
grep -r "search term" .
```

---

## 📝 Adding New Documentation

When creating new documentation:

1. **Place it in docs/**
   ```bash
   touch docs/NEW_FEATURE_GUIDE.md
   ```

2. **Update docs/README.md**
   - Add to appropriate section
   - Include brief description
   - Add to navigation table

3. **Update root README.md if major**
   - Add to Documentation section
   - Link with `docs/` prefix

4. **Use relative links correctly**
   ```markdown
   # From docs/ to docs/
   [Other Doc](./OTHER_DOC.md)
   
   # From docs/ to root
   [Main README](../README.md)
   
   # From root to docs/
   [Documentation](docs/README.md)
   ```

---

## 🔍 Finding Documentation

### By Topic

| Need | Document |
|------|----------|
| Quick start | docs/QUICKSTART.md |
| Visual guide | docs/SETUP_VISUAL_GUIDE.md |
| Manual setup | docs/SETUP_GUIDE.md |
| Architecture | docs/DEVELOPMENT_NOTES.md |
| Roadmap | docs/IMPLEMENTATION_OUTLINE.md |
| API research | docs/SPORTSBOOK_RESEARCH_COMPLETE.md |

### By Experience Level

| Level | Start Here |
|-------|------------|
| Beginner | docs/QUICKSTART.md |
| Visual learner | docs/SETUP_VISUAL_GUIDE.md |
| Experienced dev | docs/AUTOMATION_README.md |
| Architect | docs/DEVELOPMENT_NOTES.md |

---

## 🎓 Documentation Best Practices

### For Readers

1. Start with docs/README.md to understand what's available
2. Use docs/QUICKSTART.md for immediate needs
3. Dive deeper into specific docs as needed
4. Keep documentation open while working

### For Contributors

1. Keep docs/ up to date when making changes
2. Use clear, descriptive filenames
3. Include table of contents for long docs
4. Cross-reference related documentation
5. Update docs/README.md when adding new docs

---

## 📊 Documentation Statistics

- **Total documentation files:** 13 (including this file)
- **Lines of documentation:** ~3,500+ lines
- **Categories:** 4 (Getting Started, Setup, Architecture, APIs)
- **Root level docs:** 1 (README.md only)
- **Organization level:** Professional ✨

---

**All documentation is now organized and easy to find! 📚**

