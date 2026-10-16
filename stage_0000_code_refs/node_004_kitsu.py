"""
node_004_kitsu — gazu mind map (learn what the Kitsu/Zou Python client does)

Install:  pip install gazu
Docs:     https://gazu.cg-wire.com/examples
SDK:      https://dev.kitsu.cloud/references/gazu

Host is the Zou API root (note the /api suffix):
  gazu.set_host("https://your-kitsu-host/api")
  gazu.log_in("user@studio.com", "password")

Mental model (production hierarchy):
  Project
    ├── AssetType -> Asset -> Task
    └── Episode? -> Sequence -> Shot -> Task
  Task has TaskType + TaskStatus; comments / previews attach to tasks.
"""

# ---------------------------------------------------------------------------
# MIND MAP (API surface)
# ---------------------------------------------------------------------------
#
# gazu
# ├── set_host / log_in / log_out          # session bootstrap
# ├── project   # all_projects, get_project, get_project_by_name, new_project
# ├── asset     # all_assets_for_project, get_asset, new_asset, all_asset_types
# ├── shot      # episodes / sequences / shots CRUD + getters
# ├── task      # all_tasks_for_*, get_task, new_task, task types/statuses
# ├── person    # all_persons, get_person_by_email
# ├── files     # working files / outputs (when used)
# └── client    # low-level GET/POST if a helper is missing
#
# Almost every entity is a dict with at least: id, name, ...
# Helpers accept either the dict or the id string.
#

# ---------------------------------------------------------------------------
# SNIPPETS — connect
# ---------------------------------------------------------------------------

def snippet_connect(host: str, email: str, password: str):
    import gazu

    gazu.set_host(host)  # e.g. "https://kitsu.example.com/api"
    gazu.log_in(email, password)
    return gazu


# ---------------------------------------------------------------------------
# SNIPPETS — projects / assets / shots (read)
# ---------------------------------------------------------------------------

def snippet_list_projects():
    import gazu

    return gazu.project.all_projects()


def snippet_get_project(name: str = "Agent 327"):
    import gazu

    return gazu.project.get_project_by_name(name)


def snippet_assets_for_project(project):
    import gazu

    return gazu.asset.all_assets_for_project(project)


def snippet_shots_for_project(project):
    import gazu

    return gazu.shot.all_shots_for_project(project)


def snippet_get_shot(sequence, shot_name: str = "SH01"):
    import gazu

    return gazu.shot.get_shot_by_name(sequence, shot_name)


# ---------------------------------------------------------------------------
# SNIPPETS — create hierarchy (write; use a sandbox project)
# ---------------------------------------------------------------------------

def snippet_create_project(name: str = "Sandbox"):
    import gazu

    return gazu.project.new_project(name)


def snippet_create_asset(project, asset_type_name: str = "Characters", name: str = "hero"):
    import gazu

    asset_type = gazu.asset.get_asset_type_by_name(asset_type_name)
    if asset_type is None:
        asset_type = gazu.asset.new_asset_type(asset_type_name)

    return gazu.asset.new_asset(
        project,
        asset_type,
        name,
        description="learning snippet",
    )


def snippet_create_shot_chain(project, episode_name="E01", seq_name="SQ01", shot_name="SH01"):
    import gazu

    episode = gazu.shot.new_episode(project, episode_name)
    sequence = gazu.shot.new_sequence(project, seq_name, episode=episode)
    shot = gazu.shot.new_shot(
        project,
        sequence,
        shot_name,
        frame_in=1001,
        frame_out=1100,
        data={"note": "learning snippet"},
    )
    return episode, sequence, shot


# ---------------------------------------------------------------------------
# SNIPPETS — tasks (tracking heart of Kitsu)
# ---------------------------------------------------------------------------

def snippet_tasks_for_shot(shot):
    import gazu

    return gazu.task.all_tasks_for_shot(shot)


def snippet_get_task_type_and_status():
    import gazu

    # Names depend on your studio setup (Animation, Lighting, Todo, Done, ...)
    task_types = gazu.task.all_task_types()
    statuses = gazu.task.all_task_statuses()
    return task_types, statuses


def snippet_set_task_status(task, status_name: str = "Done"):
    import gazu

    status = gazu.task.get_task_status_by_name(status_name)
    return gazu.task.update_task_status(task, status)


# ---------------------------------------------------------------------------
# CHEAT — list project names (needs live host + login)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Fill host/email/password in snippet_connect(), then call snippet_list_projects().")
    print("Typical host form: https://YOUR_KITSU_HOST/api")
    try:
        import gazu  # noqa: F401

        print("gazu import: OK")
    except ImportError:
        print("Install: pip install gazu")
