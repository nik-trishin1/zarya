# «Полночь» — festival newspaper

Standalone print piece (not part of the Mini App).

## Files

| Path | Role |
|------|------|
| `index.html` + `styles.css` | Screen layout, 8 × A4 |
| `export/polnoch-approval.pdf` | Screen-approval PDF (reading order 1–8) |
| `export/polnoch-press-a3.pdf` | **Press file** — 4 × A3 **Portrait** for TM-340 roll cut |
| `PRINT_GUIDE.md` | Step-by-step print on Canon TM-340 (roll → A3 → fold) |

## Rebuild

```bash
python3 polnoch-newspaper/export_pdf.py
python3 polnoch-newspaper/export_press_a3.py
```
