# F3D - Pseudo-3D generative SVG film scenes


## File Format (.f3d.json)
The setting is stored in JSON. 
For easier discovery files should end with `.f3d.json` file type.
Default setting name is `setting.f3d.json` and is assumed to be in the current working directory.

**Definition**
```json
{
  "meta": {
    "name": "PROJECT_NAME",
    "author": "AUTHOR_NAME",
    "revision": 1
  },
```
The settings are available through Settings object/class later, all global configuration ought to go here.

The `project_identifier` is used for the output sub-directory. (Can't currently be overridden.)
```json
  "settings": {
    "project_identifier": "SHORT_UNIQUE_STRING",
    "paths": {
      "svg_resources": "textures",
      "svg_output": "svg",
      "png_output": "output"
    },
    "timing": {
      "in": 0.0,
      "out": 5.0
    },
    "image": {
      "size": {
        "width": 1920,
        "height": 1080
      }
    },
    "frames_per_second": 30
  },
  "camera": {
    "position": {
      "x": 0,
      "y": 0,
      "z": -1000
    },
    "focal_length": 55
  },
  "surfaces": [
    {
      "identifier": "bouncing-circle",
      "meta": {
        "name": "Bouncing circle"
      },

      "position": {
        "x": -980,
        "y": -540,
        "z": 1000
      },

      "type": "animated",
      "baseFrame": "circle",
      "frames": [
        {
          "path": "experiment1/circle.svg",
          "name": "circle",
          "identifier": "texture"
        },
        {
          "path": "experiment1/ellipse-vertical.svg",
          "name": "ellipse-vertical",
          "identifier": "texture"
        },
        {
          "path": "experiment1/ellipse-horizontal.svg",
          "name": "ellipse-horizontal",
          "identifier": "texture"
        }
      ],
      "animations": [
        {
          "type": "interpolation",
          "loop": false,
          "boundaryBehavior": "natural",
          "identifiers": [
            {
              "element": "ellipsoid",
              "properties": ["d"]
            }
          ],
          "keyframes": [
            {
              "time": 0.0,
              "frame": "circle"
            },
            {
              "time": 1.0,
              "frame": "ellipse-vertical"
            },
            {
              "time": 2.0,
              "frame": "circle"
            },
            {
              "time": 3.5,
              "frame": "ellipse-horizontal"
            },
            {
              "time": 5.0,
              "frame": "circle"
            }
          ]
        }
      ]
    }
  ]
}
```


## File Structure
*(The structure can be renamed, but restructured through the setting.)*

```plain
setting.f3d.json
textures/
   (your input SVG files)
svg/
   project-identifier/
       frame-0000.svg
       ...
       (output SVG)
output/
    project-identifier/
       frame-0000.png
       ...
       (output PNG, use for video)
```

