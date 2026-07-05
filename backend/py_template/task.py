from flask import Flask, request
from typing import List, Dict, Union

# ==== DO NOT CHANGE ==========================================================
app = Flask(__name__)

# ==== Type Definitions, feel free to add or modify ===========================
project_registry: Dict[str, Dict] = {}

class Slug:
    def __init__(self, slug: str):
        self.slug = slug


class ProjectEntry:
    def __init__(self, name: str, requiredResources: List[Dict[str, Union[str, int]]]):
        self.type = "project"
        self.name = name
        self.requiredResources = requiredResources


class ResourceEntry:
    def __init__(self, name: str, buildTime: int):
        self.type = "resource"
        self.name = name
        self.buildTime = buildTime

def convert(slug):
    strs = slug.split("-") # Split the slug by hyphens
    words = []
    minor_words = {"a", "an", "the", "and", "but", "or", "for", "nor", "on", "at", "to", "from", "by"}

    # Capitalize the first word and any word not in the minor_words set
    # capitalize() covers all three word types in the spec:
    #   letters only:    "meet" -> "Meet"
    #   letter + digits: "s1"   -> "S1"  
    #   digits only:     "2025" -> "2025"
    for i in strs:
        if i.lower() in minor_words:
            words.append(i.lower())
        else:
            words.append(i.capitalize())

    # Join the capitalized words with spaces to form the final title
    result = " ".join(words)
    return result
git status
# ==== Task 1 =================================================================
@app.route("/slugToTitle", methods=["GET"])
def slug_to_title():
    slug = request.args.get("slug", "")
    return convert(slug), 200

# ==== Task 2 =================================================================
@app.route("/projectEntry", methods=["POST"])
def add_project_entry():
    data = request.get_json()
   # check if the data is a valid project entry
    if "type" in data and data["type"] == "project" and "name" in data and "requiredResources" in data and isinstance(data["requiredResources"], list):
        # check if the project name already exists in the registry
        if data["name"] not in project_registry:
            # check if there are any duplicate resource names in the requiredResources list
            resource_names = [resource.get("name") for resource in data["requiredResources"]]
            if len(resource_names) == len(set(resource_names)):
                # add the project entry to the registry
                project_registry[data["name"]] = data
                return "", 200
    
    # check if the data is a valid resource entry
    if "type" in data and data["type"] == "resource" and "name" in data and "buildTime" in data:
        # check if the resource name already exists in the registry and if buildTime is greater than and equal to 0
        if data["name"] not in project_registry and isinstance(data["buildTime"], int) and data["buildTime"] >= 0:
            # add the resource entry to the registry
            project_registry[data["name"]] = data
            return "", 200
    
    return "", 400


# ==== Task 3 =================================================================
@app.route("/summary", methods=["GET"])
def get_summary():
    name = request.args.get("name")
    # TODO: Lookup entry and compute total build time and base resources
    return "", 200


# ==== DO NOT CHANGE ==========================================================
if __name__ == "__main__":
    app.run(debug=True, port=8080)
