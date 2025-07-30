# hs-blender

A Python project for manipulating Blender files and scenes using the Blender Python API.

## Project Structure

```
src/
  blender/
    helper.py
    scene.py
    bill_scene.py
  main.py
assets/
  blender/
    Legislative_Watch_Demo1.blend
```

## How to Run

1. **Install Blender**  
   Make sure [Blender](https://www.blender.org/download/) is installed on your system.

2. **Run the Script**  
   Use the following command to run your script in Blender's background mode:
   ```sh
  /Applications/Blender.app/Contents/MacOS/Blender --background --python src/main.py -- --no-debug
  ```

  Debug mode:
  ```sh
  /Applications/Blender.app/Contents/MacOS/Blender --background --python src/main.py
  ```

---

## Debugging with VS Code and debugpy

### 1. Install `debugpy` in Blender's Python

Run this command in your terminal to install `debugpy` inside Blender's Python environment:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python-expr "import ensurepip; ensurepip.bootstrap(); import pip; pip.main(['install', 'debugpy'])"
```

### 2. Add debugpy to your script

At the top of `src/main.py`, ensure you have:

```python
import debugpy

debugpy.listen(("localhost", 5678))
print("Waiting for debugger attach...")
debugpy.wait_for_client()
```

### 3. Configure VS Code

Create or add the follwing into `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Attach to Blender debugpy",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "justMyCode": false
        }
    ]
}
```

Create or add the follwing into `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Blender Script",
            "type": "shell",
            "command": "/Applications/Blender.app/Contents/MacOS/Blender",
            "args": [
                "--background",
                "--python",
                "${workspaceFolder}/src/main.py"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
```

### 4. Debug Workflow

- Start Blender with your script as shown above.
- Wait for the message: `Waiting for debugger attach...`
- In VS Code, go to the Run & Debug panel and start **Attach to Blender debugpy**.
- Set breakpoints and debug as usual!

---

## Notes

- Make sure your `src/blender` folder contains an empty `__init__.py` file so Python treats it as a package.
- Adjust paths as needed for your system and Blender version.