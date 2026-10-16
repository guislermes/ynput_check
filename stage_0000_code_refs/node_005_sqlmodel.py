"""
node_005_sqlmodel — SQLModel mind map (learn what the ORM does)

Install:  pip install sqlmodel
Docs:     https://sqlmodel.tiangolo.com/
Combo of: Pydantic (validation/schemas) + SQLAlchemy (tables/engine/session)

Mental model:
  SQLModel class (table=True)  -> Python class AND DB table
  Engine                       -> one shared DB connection factory (app-wide)
  Session                      -> short-lived unit of work (add / exec / commit)
  Field / Relationship         -> columns and links between tables

For pipeline tracking later: local SQLite is enough to learn; Postgres URL swaps in.
"""

# ---------------------------------------------------------------------------
# MIND MAP (API surface)
# ---------------------------------------------------------------------------
#
# sqlmodel
# ├── SQLModel          # base class; table=True registers a real table
# ├── Field             # primary_key, index, foreign_key, default, ...
# ├── Relationship      # ORM links (back_populates); not a DB column itself
# ├── create_engine     # sqlite:///file.db  |  postgresql+psycopg://...
# ├── Session           # with Session(engine) as session: ...
# ├── select            # build SELECT; session.exec(statement)
# └── SQLModel.metadata.create_all(engine)  # create tables from models
#
# Session lifecycle (remember this):
#   add -> commit -> refresh (to read DB-generated id / defaults)
#
# table=True vs plain SQLModel:
#   table=True  -> persisted entity
#   no table    -> request/response / DTO schema only (Pydantic-style)
#

# ---------------------------------------------------------------------------
# EXAMPLE MODELS — tiny shapes to learn Field + Relationship
# (not a full pipeline schema — just “what the framework does”)
# ---------------------------------------------------------------------------

def snippet_define_models():
    from typing import Optional

    from sqlmodel import Field, Relationship, SQLModel

    class Project(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        name: str = Field(index=True, unique=True)
        code: str

        shots: list["Shot"] = Relationship(back_populates="project")

    class Shot(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        name: str = Field(index=True)
        frame_in: int = 1001
        frame_out: int = 1100

        project_id: Optional[int] = Field(default=None, foreign_key="project.id")
        project: Optional[Project] = Relationship(back_populates="shots")

        tasks: list["Task"] = Relationship(back_populates="shot")

    class Task(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        name: str  # e.g. "model", "anim", "light"
        status: str = "todo"  # todo | wip | done — plain string while learning
        ayon_folder_path: Optional[str] = None
        kitsu_task_id: Optional[str] = None

        shot_id: Optional[int] = Field(default=None, foreign_key="shot.id")
        shot: Optional[Shot] = Relationship(back_populates="tasks")

    return Project, Shot, Task


# ---------------------------------------------------------------------------
# SNIPPETS — engine + create tables
# ---------------------------------------------------------------------------

def snippet_connect(db_url: str = "sqlite:///pipeline_learn.db", echo: bool = True):
    from sqlmodel import create_engine

    # SQLite needs this check_same_thread flag for some app patterns
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    engine = create_engine(db_url, echo=echo, connect_args=connect_args)
    return engine


def snippet_create_tables(engine):
    from sqlmodel import SQLModel

    # Models must be defined/imported BEFORE create_all so metadata knows them
    snippet_define_models()
    SQLModel.metadata.create_all(engine)


# ---------------------------------------------------------------------------
# SNIPPETS — CRUD
# ---------------------------------------------------------------------------

def snippet_create_rows(engine):
    from sqlmodel import Session

    Project, Shot, Task = snippet_define_models()

    with Session(engine) as session:
        project = Project(name="Sandbox", code="SND")
        shot = Shot(name="SH010", project=project)
        task = Task(name="anim", status="wip", shot=shot)

        session.add(project)  # relationship cascade: shot/task linked in memory
        session.commit()
        session.refresh(project)
        return project.id


def snippet_select_all_shots(engine):
    from sqlmodel import Session, select

    _, Shot, _ = snippet_define_models()

    with Session(engine) as session:
        statement = select(Shot)
        return list(session.exec(statement).all())


def snippet_select_where(engine, project_name: str = "Sandbox"):
    from sqlmodel import Session, select

    Project, Shot, _ = snippet_define_models()

    with Session(engine) as session:
        statement = (
            select(Shot)
            .join(Project)
            .where(Project.name == project_name)
        )
        return list(session.exec(statement).all())


def snippet_update_task_status(engine, task_id: int, status: str = "done"):
    from sqlmodel import Session, select

    _, _, Task = snippet_define_models()

    with Session(engine) as session:
        task = session.exec(select(Task).where(Task.id == task_id)).one()
        task.status = status
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


def snippet_delete_shot(engine, shot_id: int):
    from sqlmodel import Session, select

    _, Shot, _ = snippet_define_models()

    with Session(engine) as session:
        shot = session.exec(select(Shot).where(Shot.id == shot_id)).one()
        session.delete(shot)
        session.commit()


# ---------------------------------------------------------------------------
# SNIPPETS — read via Relationship (must be inside open Session)
# ---------------------------------------------------------------------------

def snippet_walk_project_tree(engine, project_id: int):
    from sqlmodel import Session, select

    Project, _, _ = snippet_define_models()

    with Session(engine) as session:
        project = session.exec(
            select(Project).where(Project.id == project_id)
        ).one()
        # Lazy-load works while session is open:
        for shot in project.shots:
            task_names = [t.name for t in shot.tasks]
            print(project.name, shot.name, task_names)


# ---------------------------------------------------------------------------
# CHEAT — create local sqlite + one sandbox row
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        from sqlmodel import SQLModel  # noqa: F401
    except ImportError:
        print("Install: pip install sqlmodel")
        raise SystemExit(1)

    eng = snippet_connect(echo=False)
    snippet_create_tables(eng)
    pid = snippet_create_rows(eng)
    print("created project id:", pid)
    print("shots:", [s.name for s in snippet_select_all_shots(eng)])
    snippet_walk_project_tree(eng, pid)
