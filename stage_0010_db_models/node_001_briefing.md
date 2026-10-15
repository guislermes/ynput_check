# LET'S WORK ON ENTITIES

Think entities first. Tables / FKs / interconnect come after.

**Hard rule:** core production tables **MUST** follow Kitsu + AYON structure.
Python class names can be casual; **table/entity shapes mirror the APIs** so sync is mapping, not redesign.

| System | Owns | Hierarchy |
|---|---|---|
| **Kitsu** | tracking SoT | Project → (Episode?) → Sequence → Shot → Task · AssetType → Asset → Task · Person · Comment |
| **AYON** | publish SoT | Project → Folder → Task · Folder → Product → Version → Representation · Workfile |
| **Local SQL** | studio cache + extras | same shapes + `kitsu_id` / `ayon_id` · Client/Vendor · IntakePackage · Plate metadata · Delivery · ProjectSetting |

Refs already in repo: `stage_0000_code_refs/node_004_kitsu.py`, `node_003_ayon.py`.

---

## CANONICAL ENTITY MAP (name like the tools)

### Kitsu-shaped (tracking)

```
Project
├── Episode?                    # optional (series)
├── Sequence
│     └── Shot
├── AssetType → Asset
├── Task                        # on Shot XOR Asset (entity)
│     ├── assignees  → Person   # (= our Assignment rows)
│     └── Comment               # notes / feedback on task
└── Person                      # not "Artist" as the entity name
```

Status / task type stay as enums or lookup tables matching Kitsu language
(`Todo`, `WIP`, `Retake`, `Done` — exact labels can alias later).

### AYON-shaped (publish)

```
Project
└── Folder                      # folderType: episode|sequence|shot|asset|...
      ├── Task                  # same work unit; sync id with Kitsu task
      ├── Workfile
      └── Product               # name + productType/family
            └── Version         # v001, v002…  (never overwrite)
                  └── Representation   # path + name (exr, usd, abc, mp4…)
```

**Folder ↔ Kitsu entity:** Shot/Asset/Sequence folders mirror Kitsu entities.
Locally you can keep Shot/Asset/Sequence tables (Kitsu-shaped) and treat AYON Folder as the sync twin (`ayon_id` on each).

### Studio-only (not in Kitsu/AYON — keep thin)

| Entity | Why local |
|---|---|
| Client / Vendor | commercial orgs |
| ProjectSetting | show env/specs (fps, ocio, roots…) |
| IntakePackage | set/DIT/vendor drop (folder dump) |
| Plate | set clip + logger metadata **before / beside** publish |
| Delivery (+ items) | client handoff packing list |

---

## LAYER A — STUDIO / ORG (you blocked these)

| You wrote | Maps to | TD note |
|---|---|---|
| PEOPLE / STAFF | **Person** (Kitsu) | staff \| freelancer via type; vendors are orgs |
| PROJECTS | **Project** (both) | root; hang everything on `project_id` |
| ENVIRONMENTS / SPECS | **ProjectSetting** | key/value — not AssetType environment |
| CLIENTS | Client (local) | promote off string when needed |
| VENDORS / FREELANCERS | Vendor + Person.kind | Vendor = company; freelancer = Person |

`Person` = roster · assignees on Task = Assignment · ProjectCrew later if needed.

---

## LAYER B — PRODUCTION CONTENT (Kitsu + AYON spine)

```
PROJECT
├── EPISODE? / SEQUENCE / SHOT / ASSET / ASSET_TYPE     ← Kitsu
├── BREAKDOWN                                            ← shot ↔ asset (cast)
├── TASK + ASSIGNMENT (Person) + COMMENT                 ← Kitsu
├── FOLDER (sync twin)                                   ← AYON
├── PRODUCT → VERSION → REPRESENTATION                   ← AYON (3D + AI + published plate)
├── WORKFILE                                             ← AYON
├── INTAKE PACKAGE → PLATE                               ← local set intake
└── DELIVERY (+ items)                                   ← local client handoff
```

| Entity | In code today? |
|---|---|
| Project, Asset, Shot, Task, Delivery | yes (`node_002`) — rename Artist→Person later |
| Person (as Artist), Assignment | yes (`node_003`) |
| Sequence, Episode, AssetType table | no (AssetType is enum only) |
| Comment | no |
| Product / Version / Representation / Workfile | no (scalar `version` int today) |
| IntakePackage / Plate | no |
| Client / Vendor / ProjectSetting | no / partial |

---

## LAYER B2 — PLATE (set + logger → then AYON productType `plate`)

**Name:** `Plate` (not Footage).

Goal: track **what came from set**, **folder on disk**, **camera/lens/colorspace metadata**.
One **Plate** row = merge of set report + logger report (no dual SetReport/LoggerReport tables).

### Entities

- **IntakePackage** — one drop (shoot day / drive / folder).
  - `project_id`, `name`, `shoot_day`, `received_on`
  - `root_folder` — package path
  - `source` — set | vendor | archive
  - optional: `vendor_id`, notes, raw report file paths

- **Plate** — one clip / take.
  - `package_id` → IntakePackage
  - `shot_id` — **nullable until conform**
  - `clip_name`, `folder_path`, `media_path` (uri/path, not blob)
  - set+logger metadata (below)
  - optional later: `ayon_product_id` / `ayon_version_id` once published

### Metadata (queryable)

| Field | From | Why |
|---|---|---|
| scene / slate / take | set | editorial |
| camera_body / reel | logger | identity |
| lens / focal_length / t_stop | set + logger | matchmove |
| iso / shutter / white_balance | logger | grade / QC |
| capture_fps | logger | vs ProjectSetting fps |
| colorspace / encoding | DIT / logger | OCIO |
| codec / format | logger | decode |
| tc_in / tc_out | logger | conform |
| shoot_day / unit | set | context |
| is_circle_take / select | set | selects |
| lut_on_set | DIT | viewing only |
| notes | merged | one field |

**Publish path (don’t invent a second version system):**

```
Plate (local intake)
  → publish → Product (productType/family = plate) → Version → Representation
```

Plate holds rich set metadata; AYON Version holds the pipeline publish. Link by id when you interconnect.

---

## LAYER B3 — 3D + AI = AYON Product / Version / Representation

No parallel AiTable. Same spine as AYON.

```
Folder (Shot | Asset)
  └── Product   (name + productType)   e.g. model|rig|render|cache|plate|ai_image|ai_mesh|…
        └── Version
              └── Representation
```

| Kind | productType examples |
|---|---|
| 3D | `model`, `rig`, `cache`, `render`, `look` |
| AI | `ai_image`, `ai_video`, `ai_mesh` |
| Set publish | `plate` |

### Naming → AYON anatomy later

```text
{projectCode}_{entityCode}_{product}[_variant]_v{###}
```

| Token | Local field | AYON |
|---|---|---|
| projectCode | Project.code | project |
| entityCode | Shot.name / Asset.code | folder |
| product | Product.name | product |
| productType | Product.product_type | productType / family |
| v### | Version.number | version |
| file | Representation.path | representation |

Resolve by **id**; name is a label.

AI extras on Version (or thin side-row): `tool` / `model_name`, `seed`, `prompt_ref`, `source_version_ids`.

---

## LAYER C — OUT OF SCOPE (for now)

Salary, budget ledger, HR, licenses, farm jobs, raw CSV schemas as tables, prompt warehouses, weight registries.

---

## ENTITY CHECKLIST

### Org / local
- [ ] Person (replace Artist name; staff + freelancer)
- [ ] Client / Vendor
- [x] Project
- [ ] ProjectSetting
- [ ] IntakePackage
- [ ] Plate
- [ ] Delivery (+ items)

### Kitsu-shaped
- [x] Asset / Shot / Task / Assignment
- [ ] Sequence / Episode
- [ ] AssetType (as entity or synced enum)
- [ ] Comment

### AYON-shaped
- [ ] Product / Version / Representation
- [ ] Workfile
- [ ] Folder sync ids on Shot/Asset/Sequence

---

## NEXT (still thinking — no refactor yet)

1. Locked: entity **Plate**; core tables follow **Kitsu + AYON**.
2. Prefer entity name **Person** (Kitsu) over Artist when we rename.
3. Client/Vendor now vs later — still open.
4. Then redraw FKs / modules to match this map.
