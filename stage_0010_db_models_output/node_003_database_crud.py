"""
node_003_database_crud — wipe + fake-seed all stage_0010_db_models tables

id_project FKs wired on project-scoped tables. Deeper FKs (task/person/product) next.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

from sqlmodel import Session, select

HERE = Path(__file__).resolve().parent
SCHEMA_DIR = HERE.parent / "stage_0010_db_models"
DB_PATH = HERE / "stage_0010_production.db"

sys.path.insert(0, str(SCHEMA_DIR))

from node_002_db_engine import (  # noqa: E402
    ALL_MODELS,
    db_render,
    snippet_engine,
)
from node_002_db_model_plate import Plate  # noqa: E402
from node_003_db_model_people import (  # noqa: E402
    Assignment,
    Department,
    Level,
    Person,
    PersonKind,
    Role,
)
from node_004_db_model_project import Project, ProjectStatus, Server  # noqa: E402
from node_005_db_model_kitsu import (  # noqa: E402
    Asset,
    AssetType,
    Comment,
    EntityStatus,
    Episode,
    Sequence,
    Shot,
    Task,
    TaskStatus,
    TaskType,
)
from node_006_db_model_ayon import (  # noqa: E402
    Product,
    ProductType,
    Representation,
    Version,
    Workfile,
)

STUDIO_SIZE = 200
PROJECT_COUNT = STUDIO_SIZE - 10

ROLE_DEPARTMENT: dict[Role, Department] = {
    Role.MODELER: Department.CG,
    Role.LIGHTER: Department.CG,
    Role.CG_COMPOSITOR: Department.CG,
    Role.RIGGER: Department.CG,
    Role.AI_ARTIST: Department.AI,
    Role.ANIMATOR: Department.ANIMATION,
    Role.VFX_COMPOSITOR: Department.COMPOSITING,
    Role.RETOUCHER: Department.COMPOSITING,
    Role.PAINTER: Department.COMPOSITING,
    Role.MOTION_GRAPHICS_COMPOSITOR: Department.MOTION_GRAPHICS,
    Role.EDITOR: Department.EDITORIAL,
    Role.PRODUCER: Department.PRODUCTION,
    Role.COORDINATOR: Department.PRODUCTION,
    Role.SUPERVISOR: Department.PRODUCTION,
    Role.TD: Department.PIPELINE,
    Role.IT: Department.IT,
}

TASK_ROLES: dict[TaskType, list[Role]] = {
    TaskType.CONCEPT: [Role.PAINTER, Role.AI_ARTIST],
    TaskType.MODELING: [Role.MODELER],
    TaskType.RIGGING: [Role.RIGGER],
    TaskType.SHADER: [Role.LIGHTER, Role.MODELER],
    TaskType.ANIMATION: [Role.ANIMATOR],
    TaskType.LAYOUT: [Role.ANIMATOR, Role.TD],
    TaskType.LIGHTING: [Role.LIGHTER],
    TaskType.FX: [Role.TD, Role.AI_ARTIST],
    TaskType.COMP: [
        Role.VFX_COMPOSITOR,
        Role.MOTION_GRAPHICS_COMPOSITOR,
        Role.CG_COMPOSITOR,
    ],
    TaskType.PAINT: [Role.PAINTER, Role.RETOUCHER],
    TaskType.EDIT: [Role.EDITOR],
    TaskType.RENDERING: [Role.LIGHTER, Role.TD],
    TaskType.OTHER: [Role.TD, Role.COORDINATOR],
}

ASSET_TASKS = [
    TaskType.CONCEPT,
    TaskType.MODELING,
    TaskType.RIGGING,
    TaskType.SHADER,
    TaskType.PAINT,
]
SHOT_TASKS = [
    TaskType.LAYOUT,
    TaskType.ANIMATION,
    TaskType.LIGHTING,
    TaskType.FX,
    TaskType.COMP,
    TaskType.EDIT,
    TaskType.RENDERING,
]

FIRST_NAMES = [
    "Ana", "Bruno", "Carla", "Diego", "Elena", "Felipe", "Giulia", "Hugo",
    "Iris", "Joao", "Kai", "Luna", "Marco", "Nina", "Omar", "Paula",
    "Quinn", "Rosa", "Sam", "Tina", "Ulisses", "Vera", "Wade", "Xena",
    "Yuri", "Zara", "Alex", "Bia", "Chris", "Dani",
]
LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Costa", "Pereira",
    "Almeida", "Nascimento", "Araujo", "Fernandes", "Carvalho", "Gomes",
    "Martins", "Rocha", "Ribeiro", "Alves", "Monteiro", "Mendes", "Barbosa",
]
CLIENTS = [
    "Netflix", "Disney", "HBO", "Amazon", "Apple TV", "Paramount",
    "StudioCanal", "Globo", "BBC", "Nike", "Adidas", "Local Indie",
]
ASSET_STEMS = [
    "hero", "villain", "sidekick", "prop_car", "prop_gun", "env_city",
    "env_forest", "fx_smoke", "fx_water", "crowd", "vehicle", "creature",
]
LEVELS = list(Level)
CAMERAS = ["Alexa35", "Venice2", "RED_VRaptor", "FX9"]
LENSES = ["Cooke_S4_32", "MasterPrime_50", "Sigma_24_70", "Zeiss_85"]
COLORSPACES = ["ACES_AP0", "ARRI_LogC4", "SLog3", "RedLog3G10"]


def log(msg: str) -> None:
    print(f"[seed] {msg}", flush=True)


def snippet_reset_db(db_path: Path = DB_PATH) -> None:
    """Wipe file so unique project names never collide on re-seed."""
    if db_path.exists():
        log(f"wipe existing db: {db_path}")
        db_path.unlink()
    else:
        log(f"no existing db at {db_path}")
    log("create_all tables from SQLModel.metadata")
    db_render(db_path)
    log("schema ready")


def snippet_seed_people(session: Session, count: int = STUDIO_SIZE) -> list[Person]:
    log(f"people: creating {count}")
    roles = list(Role)
    people: list[Person] = []
    for i in range(count):
        role = roles[i % len(roles)]
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        person = Person(
            name=f"{first} {last} {i:03d}",
            email=f"{first.lower()}.{last.lower()}.{i:03d}@studio.local",
            kind=random.choice(list(PersonKind)),
            role=role,
            department=ROLE_DEPARTMENT[role],
            level=random.choice(LEVELS),
        )
        session.add(person)
        people.append(person)
    session.commit()
    for person in people:
        session.refresh(person)
    log(
        f"people: committed {len(people)} "
        f"ids={people[0].id_person}..{people[-1].id_person}"
    )
    return people


def _pick_by_role(people: list[Person], roles: list[Role]) -> Person:
    pool = [p for p in people if p.role in roles]
    return random.choice(pool or people)


def snippet_seed_studio_graph(
    session: Session,
    people: list[Person],
    project_count: int = PROJECT_COUNT,
) -> dict[str, int]:
    """Seed projects + Kitsu/AYON/Plate rows. All project children set id_project."""
    log(f"graph: seeding {project_count} shows + related tables (id_project FKs)")
    statuses = list(ProjectStatus)
    servers = list(Server)
    entity_statuses = list(EntityStatus)
    asset_types = list(AssetType)
    task_statuses = list(TaskStatus)

    counts = {
        "people": len(people),
        "projects": 0,
        "episodes": 0,
        "sequences": 0,
        "shots": 0,
        "assets": 0,
        "tasks": 0,
        "assignments": 0,
        "comments": 0,
        "plates": 0,
        "products": 0,
        "versions": 0,
        "representations": 0,
        "workfiles": 0,
    }
    progress_every = max(1, project_count // 10)

    for p_idx in range(1, project_count + 1):
        code = f"PRJ{p_idx:03d}"
        server = servers[(p_idx - 1) % len(servers)]
        project = Project(
            name=f"Show_{code}",
            code=code,
            client=random.choice(CLIENTS),
            status=statuses[(p_idx - 1) % len(statuses)],
            server=server,
            fps=random.choice(["24", "25", "30"]),
            resolution=random.choice(["1920x1080", "3840x2160", "2048x858"]),
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        pid = project.id_project
        assert pid is not None
        counts["projects"] += 1

        # --- Kitsu ---
        if random.random() < 0.4:
            session.add(Episode(name=f"{code}_EP01", id_project=pid))
            counts["episodes"] += 1

        n_seq = random.randint(1, 2)
        for s_idx in range(1, n_seq + 1):
            session.add(
                Sequence(
                    name=f"{code}_SEQ{s_idx * 10:03d}",
                    description=f"fake sequence {s_idx} for {code}",
                    id_project=pid,
                )
            )
            counts["sequences"] += 1

        assets: list[Asset] = []
        for a_idx in range(1, random.randint(3, 5) + 1):
            stem = random.choice(ASSET_STEMS)
            asset = Asset(
                name=f"{code}_{stem}_{a_idx:02d}",
                asset_type=random.choice(asset_types),
                entity_status=random.choice(entity_statuses),
                id_project=pid,
            )
            session.add(asset)
            assets.append(asset)
            counts["assets"] += 1

        shots: list[Shot] = []
        for s_idx in range(1, random.randint(6, 10) + 1):
            frame_in = 1001 + (s_idx - 1) * 100
            shot = Shot(
                name=f"{code}_SH{s_idx * 10:03d}",
                entity_status=random.choice(entity_statuses),
                frame_in=frame_in,
                frame_out=frame_in + random.randint(40, 120),
                id_project=pid,
            )
            session.add(shot)
            shots.append(shot)
            counts["shots"] += 1
        session.commit()
        for asset in assets:
            session.refresh(asset)
        for shot in shots:
            session.refresh(shot)

        tasks: list[Task] = []
        for asset in assets:
            for task_type in ASSET_TASKS:
                task = Task(
                    name=f"{asset.name}_{task_type.value}",
                    task_type=task_type,
                    task_status=random.choice(task_statuses),
                    id_project=pid,
                )
                session.add(task)
                tasks.append(task)
                counts["tasks"] += 1

        for shot in shots:
            for task_type in random.sample(SHOT_TASKS, k=random.randint(2, 3)):
                task = Task(
                    name=f"{shot.name}_{task_type.value}",
                    task_type=task_type,
                    task_status=random.choice(task_statuses),
                    id_project=pid,
                )
                session.add(task)
                tasks.append(task)
                counts["tasks"] += 1
        session.commit()
        for task in tasks:
            session.refresh(task)

        # Assignment: person/task FKs later
        for task in tasks:
            preferred = TASK_ROLES[task.task_type]
            _ = _pick_by_role(people, preferred)
            session.add(Assignment(is_lead=True))
            counts["assignments"] += 1
            if random.random() < 0.3:
                session.add(Assignment(is_lead=False))
                counts["assignments"] += 1

        for _ in range(random.randint(1, 3)):
            session.add(
                Comment(
                    text=f"fake note on {code}",
                    is_client=random.random() < 0.25,
                    id_project=pid,
                )
            )
            counts["comments"] += 1

        # --- Plates ---
        for c_idx in range(1, random.randint(2, 4) + 1):
            clip = f"{code}_A{c_idx:03d}C001"
            session.add(
                Plate(
                    server=server,
                    id_project=pid,
                    clip_name=clip,
                    folder_path=f"/shows/{code}/intake/{clip}",
                    media_path=f"/shows/{code}/intake/{clip}/{clip}.%04d.exr",
                    frame_width=random.choice([1920, 3840]),
                    frame_height=random.choice([1080, 2160]),
                    file_size=random.randint(120, 8000),
                    frame_rate=random.choice([23.976, 24.0, 25.0]),
                    camera=random.choice(CAMERAS),
                    lens=random.choice(LENSES),
                    shutter=random.choice(["180", "172.8", "90"]),
                    colorspace=random.choice(COLORSPACES),
                    encoding=random.choice(["LogC4", "SLog3", "Log3G10"]),
                    set_supervisor=random.choice(people).name,
                )
            )
            counts["plates"] += 1

        # --- AYON ---
        product_specs = [
            ("model", ProductType.MODEL, "usd"),
            ("plateMain", ProductType.PLATE, "exr"),
            ("renderBeauty", ProductType.RENDER, "exr"),
        ]
        if random.random() < 0.3:
            product_specs.append(("aiConcept", ProductType.AI_IMAGE, "png"))

        for prod_name, prod_type, rep_name in product_specs:
            product = Product(
                name=prod_name,
                product_type=prod_type,
                id_project=pid,
            )
            session.add(product)
            session.commit()
            session.refresh(product)
            counts["products"] += 1

            ver_n = random.randint(1, 3)
            for number in range(1, ver_n + 1):
                version = Version(
                    number=number,
                    comment=f"{code} {prod_name} v{number:03d}",
                    tool="midjourney" if prod_type == ProductType.AI_IMAGE else None,
                    model_name="v6" if prod_type == ProductType.AI_IMAGE else None,
                    seed=str(random.randint(1000, 9999))
                    if prod_type == ProductType.AI_IMAGE
                    else None,
                )
                session.add(version)
                session.commit()
                session.refresh(version)
                counts["versions"] += 1

                session.add(
                    Representation(
                        name=rep_name,
                        path=(
                            f"/shows/{code}/publish/{prod_name}/"
                            f"v{number:03d}/{prod_name}.{rep_name}"
                        ),
                    )
                )
                counts["representations"] += 1

        for w_idx in range(1, random.randint(1, 2) + 1):
            session.add(
                Workfile(
                    name=f"{code}_work_{w_idx:02d}",
                    path=f"/shows/{code}/work/scenes/{code}_v{w_idx:03d}.blend",
                    id_project=pid,
                )
            )
            counts["workfiles"] += 1

        session.commit()

        if p_idx == 1 or p_idx % progress_every == 0 or p_idx == project_count:
            log(
                f"project {p_idx}/{project_count} id_project={project.id_project} "
                f"{code} server={project.server.value} status={project.status.value} | "
                f"assets={len(assets)} shots={len(shots)} tasks={len(tasks)}"
            )

    log("graph done — " + " ".join(f"{k}={v}" for k, v in counts.items()))
    return counts


def snippet_print_counts(session: Session) -> None:
    log("verify SELECT counts from db")
    for model in ALL_MODELS:
        n = len(session.exec(select(model)).all())
        log(f"  {model.__tablename__:16} {n}")


def snippet_seed_studio(
    people_count: int = STUDIO_SIZE,
    project_count: int = PROJECT_COUNT,
    seed: int = 42,
) -> None:
    log(
        f"start seed_studio people={people_count} "
        f"projects={project_count} rng_seed={seed}"
    )
    log(f"db path: {DB_PATH}")
    random.seed(seed)
    # ensure metadata registered even if reset path skipped create
    _ = ALL_MODELS
    snippet_reset_db(DB_PATH)
    engine = snippet_engine(DB_PATH)
    log("session open")

    with Session(engine) as session:
        people = snippet_seed_people(session, count=people_count)
        counts = snippet_seed_studio_graph(
            session, people=people, project_count=project_count
        )
        log(f"ok seeded {DB_PATH}")
        for key, value in counts.items():
            log(f"  summary {key:16} {value}")
        snippet_print_counts(session)
    engine.dispose()
    log("session closed - done")


if __name__ == "__main__":
    try:
        snippet_seed_studio(
            people_count=STUDIO_SIZE,
            project_count=PROJECT_COUNT,
        )
    except Exception as exc:  # noqa: BLE001 — learning cheat
        log(f"FAIL: {exc}")
        raise
