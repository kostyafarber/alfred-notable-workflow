import sys
from workflow import Workflow3
import os
import glob

# set paths
# DATA_DIRECTORY = '/Users/kostyafarber/Dropbox/notes'
DATA_DIRECTORY = os.getenv("notes_location")
note_files = glob.glob(DATA_DIRECTORY + "/*.md")

# icons
ICON_MD = "markdown-icon.png"
ICON_WARNING = "warning-icon.png"
ICON_UPDATE = 'update-icon.png'

# notable uri
NOTABLE_URI = "notable://"
NOTABLE_NOTE = "note/"

UPDATE_SETTINGS = {'github_slug': 'kostyafarber/alfred-notable-workflow'}

log = None

def get_notes() -> list:
    """Generate notes list from data dictionary
    provided by the user

    Returns:
        returns a list
    """
    import frontmatter as fm

    notes_data = []
    for f in note_files:
        path = os.path.join(DATA_DIRECTORY, f)
        log.info(f"loading note at {path}")

        with open(path, "r") as f:
            content = fm.load(f)
            title = content.get("title")
            log.info(f"Extract title: {title}")

            tags = content.get("tags")
            if isinstance(tags, list):
                tags = "/".join(tags)

            if not tags:
                tags = ""

            log.info(f"Extracted tags: {tags}")

        note = dict(title=title, tags=tags, path=path)
        notes_data.append(note)

    return notes_data


def search_key_notes(note: dict) -> str:
    """Creates a search key based on the title and tags
    to filter results

    Args:
        note: A dict with title and tags

    Returns:
        key: A search string
    """
    keys = []
    keys.append(note["title"])

    key = " ".join(keys)
    log.info(f"Key built: {key}")
    return key


def main(wf):
    # is update available?
    if wf.update_available:
        wf.add_item('A newer version is available',
                    '↩ to install update',
                    autocomplete='workflow:update',
                    icon=ICON_UPDATE)

    # Get query from Alfred
    if len(wf.args):
        query = wf.args[0]
    else:
        query = None

    log.info(query)

    notes = wf.cached_data("notes", get_notes, max_age=0, session=True)

    # If script was passed a query, use it to filter posts
    if query:
        notes = wf.filter(query, notes, key=search_key_notes, min_score=20)

    if not notes:  # we have no data to show, so show a warning and stop
         wf.add_item('No notes found sorry 😔', icon=ICON_WARNING)
         wf.send_feedback()
         return 0

    for note in notes:
        # open note using URI
        open_note_notable = NOTABLE_URI + NOTABLE_NOTE + note["path"]

        item = wf.add_item(
            title=note["title"],
            subtitle=note["tags"],
            icon=ICON_MD,
            arg=open_note_notable,
            valid=True,
        )

        # let user open note in deafult editor instead
        item.add_modifier(key="cmd", arg=note["path"], valid=True)

    wf.send_feedback()


if __name__ == "__main__":
    wf = Workflow3(libraries=["./lib"], 
                    update_settings=UPDATE_SETTINGS)
    log = wf.logger
    sys.exit(wf.run(main))
