# mc-texture-change

> 🎨 Automatic Texture Changes script for Minecraft.

This script will automatically download the client.jar and find the changes in textures with the previous version of Minecraft when a new version is released.

This is a up-to-date fork of [Kraineff's version](https://github.com/Kraineff/mc-texture-changes), who seems to have abandoned their version.

## How it works

Every couple of hours, a script will be run comparing the latest Minecraft versions.
If there is a new version and it contains any texture changes, a folder with the name of the version and subfolders (Added - new files, Changed - modified files, Deleted - deleted files) will appear. Otherwise, the folder will not be created.
