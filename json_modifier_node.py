import json
from typing import Any

class JSONModifierNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_input": ("STRING", {"multiline": True}),
                "path": ("STRING", {"default": ""}),
                "new_value": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("modified_json",)
    FUNCTION = "modify_json"
    CATEGORY = "utils"

    def modify_json(self, json_input: str, path: str, new_value: str) -> tuple[str]:
        try:
            data = json.loads(json_input)
            try:
                new_val = json.loads(new_value)
            except json.JSONDecodeError:
                new_val = new_value
                
            if not path:
                return (json.dumps(new_val, indent=2),)
                
            self._set_by_path(data, path, new_val)
            return (json.dumps(data, indent=2),)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input")

    def _set_by_path(self, data: Any, path: str, value: Any) -> None:
        keys = path.split('.')
        current = data

        for i, raw_key in enumerate(keys[:-1]):
            if '[' in raw_key and ']' in raw_key:
                list_key, index = raw_key[:-1].split('[')
                index = int(index)

                if isinstance(current, dict):
                    if list_key not in current:
                        raise ValueError(f"Path {'.'.join(keys[:i+1])} does not exist")
                    current = current[list_key]
                elif isinstance(current, list):
                    if list_key:
                        raise ValueError(f"Path {'.'.join(keys[:i+1])} is not valid for a list")
                else:
                    raise ValueError(f"Path {'.'.join(keys[:i+1])} does not exist")

                if not isinstance(current, list):
                    raise ValueError(f"Path {'.'.join(keys[:i+1])} is not a list")
                if index >= len(current):
                    raise ValueError(f"List index out of range at {'.'.join(keys[:i+1])}")

                current = current[index]
                continue

            if raw_key.isdigit():
                index = int(raw_key)
                if not isinstance(current, list):
                    raise ValueError(f"Path {'.'.join(keys[:i+1])} is not a list")
                if index >= len(current):
                    raise ValueError(f"List index out of range at {'.'.join(keys[:i+1])}")
                current = current[index]
                continue

            if not isinstance(current, dict) or raw_key not in current:
                raise ValueError(f"Path {'.'.join(keys[:i+1])} does not exist")
            
            current = current[raw_key]

        last_key = keys[-1]

        if '[' in last_key and ']' in last_key:
            list_key, index = last_key[:-1].split('[')
            index = int(index)

            if isinstance(current, dict):
                if list_key not in current:
                    raise ValueError(f"Path {path} does not exist")
                current = current[list_key]
            elif isinstance(current, list):
                if list_key:
                    raise ValueError(f"Path {path} is not valid for a list")
            else:
                raise ValueError(f"Path {path} does not exist")

            if not isinstance(current, list):
                raise ValueError(f"Path {path} is not a list")
            if index >= len(current):
                raise ValueError(f"List index out of range at {path}")

            current[index] = value
            return

        if last_key.isdigit():
            index = int(last_key)
            if not isinstance(current, list):
                raise ValueError(f"Path {path} is not a list")
            if index >= len(current):
                raise ValueError(f"List index out of range at {path}")
            current[index] = value
            return

        if not isinstance(current, dict):
            raise ValueError(f"Cannot assign key {last_key!r} on a non-dict value")

        current[last_key] = value