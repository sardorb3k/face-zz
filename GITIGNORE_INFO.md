# .gitignore Ma'lumotlari

## Ignore Qilingan Narsalar

### Python
- `__pycache__/` - Python bytecode cache
- `*.pyc`, `*.pyo` - Compiled Python files
- `venv/`, `env/` - Virtual environments
- `*.egg-info/` - Package metadata

### Database
- `*.db`, `*.sqlite`, `*.sqlite3` - Database fayllar
- `backend/data/*.db` - Attendance database

### Rasmlar va Data
- `backend/data/student_images/*` - Talabalar yuz rasmlari
- `backend/data/detected_faces/*` - Aniqlangan yuzlar
- `backend/image.png` - Test rasmlar

### Model Fayllar
- `models/` - InsightFace va boshqa modellar
- `*.onnx`, `*.pth`, `*.pt` - Model fayllar
- `**/insightface_models/` - InsightFace modellar

### Node.js / Next.js
- `frontend/node_modules/` - NPM paketlar
- `frontend/.next/` - Next.js build
- `frontend/out/` - Next.js export

### Environment
- `.env`, `.env.local` - Environment variables
- `backend/.env`
- `frontend/.env.local`

### Log va Temporary
- `*.log` - Log fayllar
- `tmp/`, `temp_images/` - Temporary fayllar
- `*.tmp`, `*.temp` - Temporary files

### IDE va OS
- `.vscode/`, `.idea/` - IDE settings
- `.DS_Store` - macOS
- `Thumbs.db` - Windows

## Saqlanadigan Narsalar

- `backend/data/.gitkeep` - Papka strukturasini saqlash
- `backend/data/student_images/.gitkeep`
- `backend/data/detected_faces/.gitkeep`

## Tekshirish

```bash
# Qaysi fayllar ignore qilinganini ko'rish
git status --ignored

# Yoki
git check-ignore -v <file_path>
```

