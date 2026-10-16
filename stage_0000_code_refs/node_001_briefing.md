# stage_0000 — learn what each framework does

Entrance to the lab. **No studio architecture here** — mind maps + `snippet_*` only.

| Node | Tool | Goal |
|---|---|---|
| `node_002_blender.py` | `bpy` | data vs context vs ops |
| `node_003_ayon.py` | `ayon_api` | folders / products / versions / reps |
| `node_004_kitsu.py` | `gazu` | projects / shots / tasks / status |
| `node_005_sqlmodel.py` | `sqlmodel` | engine vs session vs tables |
| `node_006_rez.py` | ASWF **Rez** | packages / requests / ResolvedContext |

## Rez one-liner

Rez resolves a **list of package requests** into a configured environment (PATH, PYTHONPATH, custom vars). It does **not** install a new copy of Blender into a venv — packages live once on disk; contexts are computed.

When you want a **show → software matrix** product (repos, show YAML, bootstrap), go to `stage_0060_rez_env/`.
