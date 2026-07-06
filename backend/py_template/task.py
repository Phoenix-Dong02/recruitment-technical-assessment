from flask import Flask, request
from typing import List, Dict, Union
from collections import defaultdict

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
# collects the total resources names and quantities needed to build a project
def collect(project_name, multiplier, totals):
    entry = project_registry[project_name]
    for dep in entry["requiredResources"]:
        dep_name = dep["name"]
        dep_qty = dep["quantity"]
        if dep_name not in project_registry:
            raise KeyError(dep_name) # raise KeyError if the dependency is not found in the registry
        elif project_registry[dep_name]["type"] == "resource":
            totals[dep_name] += dep_qty * multiplier    
        else:
            collect(dep_name, multiplier * dep_qty, totals) 

# ==== Task 3 =================================================================
@app.route("/summary", methods=["GET"])
def get_summary():
    name = request.args.get("name")
    resource_counts = defaultdict(int)
    build_times = 0
    # check if the project name exists in the registry and is of type "project"
    if name not in project_registry:
        return "", 400
    if project_registry[name]["type"] != "project":
        return "", 400
    # collect the total resources needed to build the project
    try:
        collect(name, 1, resource_counts)
    except KeyError:
        return "", 400
    # calculate the total build time based on the resources collected
    for resource_name, quantity in resource_counts.items():
        build_times += project_registry[resource_name]["buildTime"] * quantity
    # create the summary dictionary with the project name, total build time, and resources needed
    summary = {
        "name": name,
        "buildTime": build_times,
        "resources": [{"name": n, "quantity": q} for n, q in resource_counts.items()]
    }
    return summary, 200
    


# ==== DO NOT CHANGE ==========================================================
if __name__ == "__main__":
    app.run(debug=True, port=8080)
