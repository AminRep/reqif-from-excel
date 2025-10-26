ReqIF From Excel

Overview
- Select an Excel file with requirements and relations.
- Generates a ReqIF (.reqif) file compatible with tools expecting an IE PUID attribute.

Usage (End Users)
- Run the bundled EXE `ReqIF-From-Excel.exe`.
- Pick your Excel file when prompted.
- The tool writes `<excel_filename>.reqif` next to the Excel and shows a summary.

Excel Format
- Sheet `Requirements` (columns, case-insensitive; underscores/spaces accepted):
  - `ie_puid` (required)
  - `req_type` (required): functional | interface | performance
  - `foreign_id` (required)
  - `name` (required)
  - `chapter`, `description`, `text_content` (optional)
  - `status` (draft|wip|reviewed|approved), `priority` (high|medium|low)
  - `req_prefix`, `identifier`, `order` (optional)
- Sheet `Relations`:
  - `relation_type` (satisfy|derive|refine)
  - Either `source_id`/`target_id` (SPEC-OBJECT IDs) or `source_ie_puid`/`target_ie_puid`
  - `identifier` (optional)

Build (Developers)
- Python 3.9+; install dependencies:
  - `pip install -r requirements.txt`
  - optional: `pip install pandas`
- Build single EXE:
  - `scripts/build_exe.bat`
  - Output: `dist/ReqIF-From-Excel.exe`

Project Layout
- `src/reqif_app/` package with generator and Excel bridge
- `scripts/build_exe.bat` PyInstaller build script
- `examples/` sample Excel and optional sample ReqIFs
- `output/` (ignored) for generated files

