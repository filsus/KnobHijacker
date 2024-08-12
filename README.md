## KnobHijacker

![Title](/images/title.gif)

KnobHijacker is a Nuke (Foundry) plugin, that enables the user to "hijack" chosen knobs and their QWidget container on a selected node, by either pressing a keyboard shortcut or a mouse button right-click. The behaviour of the QWidget container can be modified thus automating the value input from the user. For example, the size knob on the Blur node can be hijacked instantly prompting the user to enter the size value and confirm by pressing the Return key.

To view a detailed breakdown, visit my [blog page](https://filipsuska.com/blog/knobhijacker).

## Installation
> Note: For more information on how to install custom plugins simply navigate to the official Foundry [website](https://learn.foundry.com/nuke/developers/151/pythondevguide/installing_plugins.html).
### 1. Copy the repository to your `NUKE_PLUGIN_PATH`
Make sure the full folder is copied over. For solo users copy all files in this repository to `Users/[my_user_name]/.nuke/KnobHijacker` directory.

### 2. Add the plugin to Nuke
Open your `init.py` file inside a valid `NUKE_PLUGIN_PATH directory` and add the following code:

```python
import nuke
nuke.pluginAddPath("KnobHijacker")
```
## Supported Versions
> Note: This plugin has been only tested with the below setup. It might not work on different OS or Nuke version.

| Nuke15.0v4    |     Windows 10/11      |
|:------------------:|:------------------:|
| :heavy_check_mark: | :heavy_check_mark: |

## Changelog
### 1.0.0
- Initial Release

## License
Licensed under MIT License. See [LICENSE.md](LICENSE.md) for more.
