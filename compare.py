import os
import sys
import zipfile
import urllib.request
import filecmp
import shutil
import errno
import typing
import orjson

VERSIONS_JSON = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
RELEASE_TYPES = typing.Literal["release", "snapshot"]


def fetch_json(url: str):
    response = urllib.request.urlopen(url)
    return orjson.loads(response.read())


def get_urls(type: RELEASE_TYPES, number: int) -> list[str]:
    global VERSIONS_JSON
    urls = {}

    for item in fetch_json(VERSIONS_JSON)["versions"]:
        if len(urls) < (number + 1) and item["type"] == type:
            urls[item["id"]] = item["url"]

    return list(urls.values())


def save_temp(urls: list[str]) -> list[str]:
    names = []
    if not os.path.exists("temp"):
        os.mkdir("temp")

    for url in urls:
        name = fetch_json(url)["id"]
        names.append(name)

        os.mkdir(f"temp/{name}")
        with open(f"temp/{name}.zip", "wb") as f:
            f.write(
                urllib.request.urlopen(
                    fetch_json(url)["downloads"]["client"]["url"]
                ).read()
            )

        zip_ref = zipfile.ZipFile(f"temp/{name}.zip", "r")
        zip_ref.extractall(f"temp/{name}")
        zip_ref.close()

    return names


def diff_folders(new: str, old: str, type: RELEASE_TYPES, delete_folder: bool = False):
    added = []
    changed = []
    deleted = []

    if not delete_folder:
        diff_folders(old, new, type, delete_folder=True)

    for root, _, files in os.walk(f"temp/{new}"):
        for name in files:
            src = os.path.join(root, name)
            if f"temp/{new}/assets/minecraft/textures/" in src:
                dest = src.replace(new, old, 1)

                if not delete_folder:
                    if not os.path.exists(dest):
                        added.append(src)
                    elif not filecmp.cmp(src, dest):
                        changed.append(src)
                elif not os.path.exists(dest):
                    deleted.append(src)

    for item in added:
        save_diff(new, f"../{type.capitalize()}s/{new}/added", item)

    for item in changed:
        save_diff(new, f"../{type.capitalize()}s/{new}/changed", item)

    for item in deleted:
        save_diff(new, f"../{type.capitalize()}s/{old}/deleted", item)


def save_diff(base_folder: str, new_folder: str, item: str):
    src = item
    dest = item.replace(f"{base_folder}/assets/minecraft/textures/", f"{new_folder}/")

    try:
        shutil.copy(src, dest)
    except IOError as e:
        if e.errno != errno.ENOENT:
            raise

        os.makedirs(os.path.dirname(dest))
        e = shutil.copy(src, dest)


def main():
    release_type = sys.argv[1]
    number = int(sys.argv[2])

    if release_type not in {"release", "snapshot"}:
        print("Invalid release type")
        return

    if typing.TYPE_CHECKING:
        release_type = typing.cast(RELEASE_TYPES, release_type)

    print("Getting files...")
    urls = get_urls(release_type, number)
    folders = save_temp(urls)

    print("Comparing files...")
    for x in range(number):
        diff_folders(folders[x], folders[x + 1], release_type)


if __name__ == "__main__":
    main()
