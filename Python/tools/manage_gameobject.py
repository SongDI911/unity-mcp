from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any, List, Union
from unity_connection import get_unity_connection

def register_manage_gameobject_tools(mcp: FastMCP):
    """Register all GameObject management tools with the MCP server."""

    @mcp.tool()
    def manage_gameobject(
        ctx: Context,
        action: str,
        target: Optional[Union[str, int]] = None,
        search_method: Optional[str] = None,
        # --- Parameters for 'create' ---
        name: Optional[str] = None,
        tag: Optional[str] = None,
        parent: Optional[Union[str, int]] = None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        components_to_add: Optional[List[Union[str, Dict[str, Any]]]] = None,
        primitive_type: Optional[str] = None,
        save_as_prefab: Optional[bool] = False,
        prefab_path: Optional[str] = None,
        prefab_folder: Optional[str] = "Assets/Prefabs",
        # --- Parameters for 'modify' ---
        new_name: Optional[str] = None,
        new_parent: Optional[Union[str, int]] = None,
        set_active: Optional[bool] = None,
        new_tag: Optional[str] = None,
        new_layer: Optional[Union[str, int]] = None,
        components_to_remove: Optional[List[str]] = None,
        component_properties: Optional[Dict[str, Dict[str, Any]]] = None,
        # --- Parameters for 'find' ---
        search_term: Optional[str] = None,
        find_all: Optional[bool] = False,
        search_in_children: Optional[bool] = False,
        search_inactive: Optional[bool] = False,
        # -- Component Management Arguments --
        component_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Manages GameObjects: create, modify, delete, find, and component operations.

        Args:
            action: Operation (e.g., 'create', 'modify', 'find', 'add_component', 'remove_component', 'set_component_property').
            target: GameObject identifier (name, path, ID) for modify/delete/component actions.
            search_method: How to find objects ('by_name', 'by_id', 'by_path', etc.). Used with 'find' and some 'target' lookups.
            component_properties: Dict mapping Component names to their properties to set.
                                  Example: {"Rigidbody": {"mass": 10.0, "useGravity": True}},
                                  To set references:
                                  - Use asset path string for Prefabs/Materials, e.g., {"MeshRenderer": {"material": "Assets/Materials/MyMat.mat"}}
                                  - Use a dict for scene objects/components, e.g.:
                                    {"MyScript": {"otherObject": {"find": "Player", "method": "by_name"}}} (assigns GameObject)
                                    {"MyScript": {"playerHealth": {"find": "Player", "component": "HealthComponent"}}} (assigns Component)
            Action-specific arguments (e.g., name, parent, position for 'create';
                     component_name for component actions;
                     search_term, find_all for 'find').

        Returns:
            Dictionary with operation results ('success', 'message', 'data').
        """
        try:
            # --- Early check for attempting to modify a prefab asset ---
            # ----------------------------------------------------------

            # Prepare parameters, removing None values
            params = {
                "action": action,
                "target": target,
                "searchMethod": search_method,
                "name": name,
                "tag": tag,
                "parent": parent,
                "position": position,
                "rotation": rotation,
                "scale": scale,
                "componentsToAdd": components_to_add,
                "primitiveType": primitive_type,
                "saveAsPrefab": save_as_prefab,
                "prefabPath": prefab_path,
                "prefabFolder": prefab_folder,
                "newName": new_name,
                "newParent": new_parent,
                "setActive": set_active,
                "newTag": new_tag,
                "newLayer": new_layer,
                "componentsToRemove": components_to_remove,
                "componentProperties": component_properties,
                "searchTerm": search_term,
                "findAll": find_all,
                "searchInChildren": search_in_children,
                "searchInactive": search_inactive,
                "componentName": component_name
            }
            params = {k: v for k, v in params.items() if v is not None}
            
            # --- Handle Prefab Path Logic ---
            if action == "create" and params.get("saveAsPrefab"): # Check if 'saveAsPrefab' is explicitly True in params
                if "prefabPath" not in params:
                    if "name" not in params or not params["name"]:
                        return {"success": False, "message": "Cannot create default prefab path: 'name' parameter is missing."}
                    # Use the provided prefab_folder (which has a default) and the name to construct the path
                    constructed_path = f"{prefab_folder}/{params['name']}.prefab"
                    # Ensure clean path separators (Unity prefers '/')
                    params["prefabPath"] = constructed_path.replace("\\", "/")
                elif not params["prefabPath"].lower().endswith(".prefab"):
                    return {"success": False, "message": f"Invalid prefab_path: '{params['prefabPath']}' must end with .prefab"}
            # Ensure prefab_folder itself isn't sent if prefabPath was constructed or provided
            # The C# side only needs the final prefabPath
            params.pop("prefab_folder", None) 
            # --------------------------------
            
            # Send the command to Unity via the established connection
            # Use the get_unity_connection function to retrieve the active connection instance
            # Changed "MANAGE_GAMEOBJECT" to "manage_gameobject" to potentially match Unity expectation
            response = get_unity_connection().send_command("manage_gameobject", params)

            # Check if the response indicates success
            # If the response is not successful, raise an exception with the error message
            if response.get("success"):
                return {"success": True, "message": response.get("message", "GameObject operation successful."), "data": response.get("data")}
            else:
                return {"success": False, "message": response.get("error", "An unknown error occurred during GameObject management.")}

        except Exception as e:
            return {"success": False, "message": f"Python error managing GameObject: {str(e)}"} 