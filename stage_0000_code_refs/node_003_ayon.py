"""
node_003_ayon — ayon_api mind map (learn what the AYON Python API does)

Install:  pip install ayon-python-api
Docs:     https://docs.ayon.dev/ayon-python-api/
Guide:    https://community.ynput.io/t/ayon-python-api-first-steps/1278

Auth via env (required before get_server_api_connection):
  AYON_SERVER_URL  e.g. https://your-studio.ayon.app
  AYON_API_KEY     service / user API key from AYON

Mental model (entity hierarchy in a project):
  Project
    └── Folder (asset / shot / episode / ... — typed folders)
          └── Task
          └── Product (publishable family, e.g. model, render)
                └── Version
                      └── Representation (files: abc, exr, blend, ...)
"""

# ---------------------------------------------------------------------------
# MIND MAP (API surface)
# ---------------------------------------------------------------------------
#
# ayon_api
# ├── get_server_api_connection()  # ServerAPI from env credentials
# └── ServerAPI (con)
#     ├── projects: get_projects / get_project / get_project_names / create_project
#     ├── folders:  get_folders / get_folder_by_id / get_folders_hierarchy / create_folder
#     ├── tasks:    get_tasks / get_task_by_id / create_task
#     ├── products: get_products / get_product_by_id / create_product
#     ├── versions: get_versions / get_version_by_id / create_version
#     └── reps:     get_representationsations / create_representation
#
# Entities are usually dicts with keys like: id, name, path, folderType, attrib, data
#

# ---------------------------------------------------------------------------
# SNIPPETS — connect + read (safe to explore)
# ---------------------------------------------------------------------------

def snippet_connect():
    import os

    # Prefer real env vars in your shell; placeholders only for learning
    os.environ.setdefault("AYON_SERVER_URL", "https://YOUR_SERVER")
    os.environ.setdefault("AYON_API_KEY", "YOUR_API_KEY")

    import ayon_api

    con = ayon_api.get_server_api_connection()
    return con


def snippet_list_projects(con=None):
    import ayon_api

    con = con or ayon_api.get_server_api_connection()
    names = []
    for project in con.get_projects():
        names.append(project["name"])
    return names


def snippet_get_project(project_name: str, con=None):
    import ayon_api

    con = con or ayon_api.get_server_api_connection()
    project = con.get_project(project_name)  # dict or None
    return project


def snippet_walk_folders(project_name: str, con=None):
    """Folders = assets/shots/etc. Hierarchy is the production tree."""
    import ayon_api

    con = con or ayon_api.get_server_api_connection()

    # Flat iterator of folder dicts
    for folder in con.get_folders(project_name):
        # typical keys: id, name, path, folderType, parentId
        yield folder

    # Tree shape (parent/children) — useful to visualize structure
    # hierarchy = con.get_folders_hierarchy(project_name)


def snippet_get_folder_by_path_idea(project_name: str, folder_path: str, con=None):
    """Common pipeline need: resolve '/assets/characters/hero' -> folder id."""
    import ayon_api

    con = con or ayon_api.get_server_api_connection()
    for folder in con.get_folders(project_name):
        if folder.get("path") == folder_path:
            return folder
    return None


def snippet_products_and_versions(project_name: str, folder_id: str, con=None):
    import ayon_api

    con = con or ayon_api.get_server_api_connection()

    products = list(con.get_products(project_name, folder_ids=[folder_id]))
    for product in products:
        versions = list(
            con.get_versions(project_name, product_ids=[product["id"]])
        )
        yield product, versions


# ---------------------------------------------------------------------------
# SNIPPETS — create (write side; use a sandbox project)
# ---------------------------------------------------------------------------

def snippet_create_folder_example(project_name: str, con=None):
    import ayon_api

    con = con or ayon_api.get_server_api_connection()
    folder_id = con.create_folder(
        project_name,
        name="hero",
        folder_type="Asset",  # must exist in project anatomy
        # parent_id="...",
    )
    return folder_id


def snippet_create_version_example(project_name: str, product_id: str, con=None):
    import ayon_api

    con = con or ayon_api.get_server_api_connection()
    version_id = con.create_version(
        project_name,
        version=1,
        product_id=product_id,
        # task_id="...",
        # author="pipeline",
    )
    return version_id


# ---------------------------------------------------------------------------
# CHEAT — print project names (needs live credentials)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        connection = snippet_connect()
        print("projects:", snippet_list_projects(connection))
    except Exception as exc:
        print("Set AYON_SERVER_URL + AYON_API_KEY, then re-run.")
        print("error:", type(exc).__name__, exc)
