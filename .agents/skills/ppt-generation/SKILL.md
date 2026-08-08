---
name: ppt-generation
description: Generates structured, professional slide decks, presentations, and PowerPoint (.pptx / Marp Markdown / PDF / HTML) artifacts from structured data, research briefs, travel itineraries, or user prompts. Inspired by ByteDance DeerFlow's PPT generation skill using Marp CLI, custom CSS themes, and semantic slide structures.
version: 1.0.0
---

# PPT Generation Skill (DeerFlow & Marp Engine)

This skill enables autonomous agents to design, structure, and generate publication-ready slide decks and presentations in PowerPoint (`.pptx`), PDF, HTML, and Marp Markdown formats.

---

## 1. 🎯 Overview & Architectural Workflow

```
[User Request / Itinerary / Research]
               │
               ▼
[1. Content Structuring & Outline Planning]
  - 1 Title Slide
  - 1 Executive Summary / Agenda Slide
  - N Content & Analysis Slides (2-column, grid, cards, timeline)
  - 1 Logistics / Budget / Comparison Slide
  - 1 Conclusion / Action Item Slide
               │
               ▼
[2. Marp Markdown Generation]
  - YAML Frontmatter (marp, theme, paginate, header, footer)
  - Scoped Layout Classes (lead, invert, columns, card grids)
  - High-Contrast Aesthetics & Visual Assets
               │
               ▼
[3. Rendering & Export]
  - Marp CLI: Markdown ➔ .pptx / .pdf / .html
  - Or Python `python-pptx` programmatic generation
```

---

## 2. 📝 Marp Markdown Syntax & Directives

All slide decks generated via Marp Markdown must follow standard Marp syntax:

### A. Frontmatter Configuration
```yaml
---
marp: true
theme: gaia
_class: lead
paginate: true
backgroundColor: #0F172A
color: #F8FAFC
header: "Travel Buddy — AI Agentic Presentation"
footer: "© 2026 AI Travel Buddy • Confidential & Curated"
style: |
  section {
    font-family: 'Inter', sans-serif;
    padding: 40px;
  }
  h1 {
    color: #FF6B6B;
  }
  h2 {
    color: #38BDF8;
  }
  .card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  .grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 16px;
  }
---
```

### B. Slide Separators & Directives
- **Slide Delimiter:** `---` separated by blank lines.
- **Title Slide Header / Lead:** `<!-- _class: lead invert -->` to center and invert primary titles.
- **Background Images:** `![bg right:40%](https://images.unsplash.com/...)` for split image slides.
- **Pagination Exclusions:** `<!-- _paginate: false -->` on title and agenda slides.

---

## 3. 🎨 Slide Layout Templates

### Template 1: Title Slide (Lead & Inverted)
```markdown
<!-- _class: lead invert -->
<!-- _paginate: false -->

# 🌍 5-Day Luxury Expedition
## Kyoto & Hokkaido, Japan

**Curated by AI Travel Buddy Multi-Agent Network**
*Travelers: 2 Adults, 1 Child • Budget: S$ 3,775 SGD*
```

---

### Template 2: Two-Column Comparison / Logistics Slide
```markdown
---
## 🗺️ Day 1–2 Highlights & Sights

<div class="grid-2">
<div class="card">

### 📍 Day 1: Kyoto Historic Temples
- **Morning:** Kinkaku-ji (Golden Pavilion)
- **Lunch:** Traditional Soba in Gion (S$ 25)
- **Evening:** Fushimi Inari Sunset Stroll
- **Lodging:** Kyoto Heritage Ryokan
</div>

<div class="card">

### 🌾 Day 2: Furano Lavender Fields
- **Morning:** Scenic Flight / Train to Sapporo
- **Afternoon:** Self-Drive Farm Tomita Route
- **Dinner:** Hokkaido Seafood Hotpot (S$ 45)
- **Lodging:** Riverside Boutique Resort
</div>
</div>
```

---

### Template 3: Budget & Breakdown Table Slide
```markdown
---
## 💰 Curated Cost & Logistics Breakdown

| Expense Category | Provider / Notes | Cost (SGD) |
| :--- | :--- | :--- |
| **✈️ Round-Trip Airfare** | Singapore Airlines (2 Adults, 1 Child) | S$ 1,860.00 |
| **🏨 Accommodations** | 4 Nights (Boutique & Family Stays) | S$ 840.00 |
| **🍽️ Dining & Food** | Multi-course tastings & Local Cafes | S$ 690.00 |
| **🗺️ Sights & Passes** | Temple Entries, Fjord Cruise, Gardens | S$ 385.00 |
| **TOTAL ESTIMATE** | **Target Range: Approved (Score: 9/10)** | **S$ 3,775.00 SGD** |
```

---

## 4. ⚙️ CLI Compilation & Export Commands

To compile Marp Markdown into PowerPoint (`.pptx`), PDF, or web presentation:

```bash
# 1. Install Marp CLI globally or run via npx
npm install -g @marp-team/marp-cli

# 2. Export to PowerPoint presentation
npx @marp-team/marp-cli presentation.md --pptx -o presentation.pptx

# 3. Export to PDF slide deck
npx @marp-team/marp-cli presentation.md --pdf -o presentation.pdf

# 4. Export to standalone interactive HTML presentation
npx @marp-team/marp-cli presentation.md --html -o presentation.html
```

---

## 5. 🐍 Programmatic Python Generation (`python-pptx`)

For direct binary `.pptx` creation without external CLI dependencies:

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

def create_presentation(title_text, subtitle_text, slides_data, output_path="presentation.pptx"):
    prs = Presentation()
    
    # 1. Title Slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = title_text
    subtitle.text = subtitle_text
    
    # 2. Content Slides
    bullet_slide_layout = prs.slide_layouts[1]
    for s_data in slides_data:
        slide = prs.slides.add_slide(bullet_slide_layout)
        shapes = slide.shapes
        title_shape = shapes.title
        body_shape = shapes.placeholders[1]
        
        title_shape.text = s_data["title"]
        tf = body_shape.text_frame
        for point in s_data["points"]:
            p = tf.add_paragraph()
            p.text = point
            p.level = 0
            
    prs.save(output_path)
    return output_path
```

---

## 6. ✅ Presentation Quality Checklist

- [ ] Clear slide hierarchy (H1 for title, H2 for slide header, H3 for card titles).
- [ ] Maximum 4–6 bullet points per slide to prevent cognitive overload.
- [ ] High contrast ratios between text and slide background ($\ge 4.5:1$).
- [ ] Consistent layout margins and spacing ($40\text{px}$ minimum padding).
- [ ] Clear financial or data summaries presented in clean tables or grid cards.
