import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import copy
from src.Vector2 import Vector2
from src.SpatialBasics import (
    SpatialAdjustment,
    SpatialPredicateCategories,
)
from src.SpatialPredicate import (
    SpatialPredicate,
    SpatialTerms,
    connectivity
)
from .SpatialObject import SpatialObject
from .SpatialRelation import SpatialRelation
from .SpatialInference import SpatialInference


class SpatialReasoner:
    def __init__(self):
        # === Settings ===
        self.adjustment = SpatialAdjustment()
        self.deduce = SpatialPredicateCategories()
        self.north = Vector2(x=0.0, y=-1.0)  # North direction, e.g., defined by ARKit

        # === Data ===
        self.objects: List[SpatialObject] = []
        self.observer: Optional[SpatialObject] = None
        self.relMap: Dict[int, List[SpatialRelation]] = {}  # index: [SpatialRelation]
        self.chain: List[SpatialInference] = []
        self.base: Dict[str, Any] = (
            {}
        )  # Fact base for read/write access of expression evaluation
        self.snapTime: datetime.datetime = (
            datetime.datetime.now()
        )  # Load or update time of fact base

        # === Logging ===
        self.pipeline: str = ""  # Last used inference pipeline
        self.name: str = ""  # Used as title for log
        self.description: str = ""  # Used in log output
        self.logCnt: int = 0
        self.logFolder: Optional[Path] = None  # If None, Downloads folder will be used

    # === Loading Methods ===

    def load(self, objs: Optional[List[SpatialObject]] = None):
        """
        Load SpatialObjects into the reasoner.
        """
        if objs is not None:
            self.objects = objs
        self.observer = None
        self.relMap = {}
        self.base["objects"] = []

        if self.objects:
            objList = []
            for obj in self.objects:
                obj.context = self
                objList.append(obj.asDict())
                if obj.observing:
                    self.observer = obj
            self.base["objects"] = objList

        self.snapTime = datetime.datetime.now()
        self.base["snaptime"] = self.snapTime.isoformat()

    def object_with_id(self, id: str) -> Optional[SpatialObject]:
        """
        Retrieve a SpatialObject by its ID.
        """
        for obj in self.objects:
            if obj.id == id:
                return obj
        return None

    def index_of_id(self, id: str) -> Optional[int]:
        """
        Retrieve the index of a SpatialObject by its ID.
        """
        for idx, obj in enumerate(self.objects):
            if obj.id == id:
                return idx
        return None

    def set_data(self, key: str, value: Any):
        """
        Set additional arbitrary data in the fact base.
        """
        dict_data = self.base.get("data", {})
        dict_data[key] = value
        self.base["data"] = dict_data

    def sync_to_objects(self):
        """
        Synchronize the fact base to SpatialObjects.
        """
        self.objects = []
        self.observer = None
        self.relMap = {}
        obj_dicts = self.base.get("objects", [])

        for obj_dict in obj_dicts:
            obj = SpatialObject(id=obj_dict["id"])
            obj.fromAny(obj_dict)
            self.objects.append(obj)
            if obj.observing:
                self.observer = obj

    def load_from_dicts(self, objs: List[Dict[str, Any]]):
        """
        Load SpatialObjects from a list of dictionaries.
        """
        self.base["objects"] = objs
        self.sync_to_objects()
        self.base["snaptime"] = self.snapTime.isoformat()
        self.snapTime = datetime.datetime.now()

    def load_from_json(self, json_str: str):
        """
        Load SpatialObjects from a JSON string.
        """
        try:
            data = json.loads(json_str)
            if isinstance(data, list):
                self.load_from_dicts(data)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")

    def take_snapshot(self) -> Dict[str, Any]:
        """
        Take a snapshot of the current fact base.
        """
        return copy.deepcopy(self.base)

    def load_snapshot(self, snapshot: Dict[str, Any]):
        """
        Load a snapshot into the fact base.
        """
        self.base = copy.deepcopy(snapshot)
        self.sync_to_objects()

    # === Recording and Backtracing ===

    def record(self, inference: SpatialInference):
        """
        Record a SpatialInference in the chain and fact base.
        """
        self.chain.append(inference)
        chain_list = self.base.get("chain", [])
        chain_list.append(inference.asDict())
        self.base["chain"] = chain_list

    def backtrace(self, steps: int = 1) -> List[int]:
        """
        Backtrace to find the input indices of the Nth-last manipulating inference.
        If steps=1 (default), returns the last one; steps=2 returns the second-last, etc.
        """
        cnt = 0
        for inference in reversed(self.chain):
            if inference.is_manipulating():
                cnt += 1
                if cnt == abs(steps):
                    # return a copy to avoid downstream mutation
                    return list(inference.input)
        return []

    # === Running the Inference Pipeline ===

    def run(self, pipeline: str) -> bool:
        """
        Run the spatial reasoning pipeline.
        """
        self.pipeline = pipeline
        self.logCnt = 0
        self.chain = []
        self.base["chain"] = []

        operations = [op.strip() for op in pipeline.split("|")]
        indices = list(range(len(self.objects)))

        for op in operations:
            if op.startswith("log(") and op.endswith(")"):
                content = op[4:-1].strip()
                self.log(content)
            elif op.startswith("adjust(") and op.endswith(")"):
                content = op[7:-1].strip()
                ok = self.adjust(content)
                if not ok:
                    self.log_error()
                    break
            elif op.startswith("deduce(") and op.endswith(")"):
                # toggle the predicate‐category flags (no SpatialInference recorded)
                content = op[7:-1].strip()
                self.deduce_categories(content)
                continue
            elif op.startswith("halt("):
                break
            else:
                input_chain = self.chain[-1].output if self.chain else indices
                inference = SpatialInference(
                    input_indices=input_chain, operation=op, fact=self
                )
                self.record(inference)
                if inference.has_failed():
                    print("Inference Error:", inference.error)
                    self.log_error()
                    break

        self.sync_to_objects()

        if self.chain:
            return self.chain[-1].succeeded
        # if the only operations were deduce(...) or log(...), consider it a success
        if any(op.startswith("deduce(") for op in operations) or any(
            op.startswith("log(") for op in operations
        ):
            return True
        return False

    # === Retrieving Results ===

    def result(self) -> List[SpatialObject]:
        """
        Retrieve the resulting SpatialObjects after running the pipeline.
        """
        if self.chain:
            return [self.objects[idx] for idx in self.chain[-1].output]
        return []

    # === Logging Methods ===

    def log_error(self):
        """
        Log the last error from the inference chain.
        """
        if self.chain:
            error_string = f"Error occured in the inference chain: \nOperation: {self.chain[-1].operation} \nError: {self.chain[-1].error}"
            print(error_string)

    @staticmethod
    def print_relations(relations: List[SpatialRelation]):
        """
        Print a list of SpatialRelations in a readable format.
        """
        for relation in relations:
            print(
                f"{relation.subject.id} {relation.predicate} {relation.object.id} | Δ:{relation.delta:.2f}  α:{relation.yaw:.1f}°"
            )

    def relations_of(self, idx: int) -> List[SpatialRelation]:
        """
        Retrieve all SpatialRelations for the object at the given index.
        """
        if idx in self.relMap:
            return self.relMap[idx]
        relations = []
        for subject in self.objects:
            if subject != self.objects[idx]:
                relations.extend(self.objects[idx].relate(subject=subject))
        self.relMap[idx] = relations
        return relations

    def relations_with(self, obj_idx: int, predicate: str) -> List[SpatialRelation]:
        """
        Retrieve SpatialRelations with a specific predicate for the object at obj_idx.
        """
        rels = []
        if obj_idx >= 0:
            for relation in self.relations_of(obj_idx):
                if relation.predicate.value == predicate:
                    rels.append(relation)
        return rels

    def does(self, subject: SpatialObject, have: str, with_obj_idx: int) -> bool:
        """
        Check if the subject has a specific predicate relation with the object at with_obj_idx.
        """
        for relation in self.relations_of(with_obj_idx):
            if relation.subject == subject and relation.predicate.value == have:
                return True
        return False

    # === Adjustment and Deduction ===

    def adjust(self, settings: str) -> bool:
        """
        Adjust the reasoning engine's settings based on a settings string.
        """
        error = ""
        settings_list = [s.strip() for s in settings.split(";")]

        for setting in settings_list:
            parts = setting.split()
            first = parts[0] if len(parts) > 0 else ""
            second = parts[1] if len(parts) > 1 else ""
            number = parts[2] if len(parts) > 2 else ""

            if first == "max":
                if second == "gap":
                    if number:
                        try:
                            val = float(number)
                            self.adjustment.maxGap = val
                        except ValueError:
                            error = f"Invalid max gap value: {number}"
                elif second in ["angle", "delta"]:
                    if number:
                        try:
                            val = float(number)
                            self.adjustment.maxAngleDelta = val
                        except ValueError:
                            error = f"Invalid max angle value: {number}"
                else:
                    error = f"Unknown max setting: {second}"

            elif first == "sector":
                set_factor = True
                if second == "fixed":
                    self.adjustment.sectorSchema = "fixed"
                elif second == "dimension":
                    self.adjustment.sectorSchema = "dimension"
                elif second == "perimeter":
                    self.adjustment.sectorSchema = "perimeter"
                elif second == "area":
                    self.adjustment.sectorSchema = "area"
                elif second == "nearby":
                    self.adjustment.sectorSchema = "nearby"
                elif second == "factor":
                    set_factor = True
                elif second == "limit":
                    set_factor = False
                    if number:
                        try:
                            val = float(number)
                            self.adjustment.sectorLimit = val
                        except ValueError:
                            error = f"Invalid sector limit value: {number}"
                else:
                    error = f"Unknown sector setting: {second}"

                if set_factor and number:
                    try:
                        val = float(number)
                        self.adjustment.sectorLimit = val
                    except ValueError:
                        error = f"Invalid sector limit value: {number}"

            elif first == "nearby":
                set_factor = True
                if second == "fixed":
                    self.adjustment.nearbySchema = "fixed"
                elif second == "circle":
                    self.adjustment.nearbySchema = "circle"
                elif second == "sphere":
                    self.adjustment.nearbySchema = "sphere"
                elif second == "perimeter":
                    self.adjustment.nearbySchema = "perimeter"
                elif second == "area":
                    self.adjustment.nearbySchema = "area"
                elif second == "factor":
                    set_factor = True
                elif second == "limit":
                    set_factor = False
                    if number:
                        try:
                            val = float(number)
                            self.adjustment.nearbyLimit = val
                        except ValueError:
                            error = f"Invalid nearby limit value: {number}"
                else:
                    error = f"Unknown nearby setting: {second}"

                if set_factor and number:
                    try:
                        val = float(number)
                        self.adjustment.nearbyFactor = val
                    except ValueError:
                        error = f"Invalid nearby factor value: {number}"

            elif first == "long":
                if second == "ratio":
                    if number:
                        try:
                            val = float(number)
                            self.adjustment.longRatio = val
                        except ValueError:
                            error = f"Invalid long ratio value: {number}"

            elif first == "thin":
                if second == "ratio":
                    if number:
                        try:
                            val = float(number)
                            self.adjustment.thinRatio = val
                        except ValueError:
                            error = f"Invalid thin ratio value: {number}"

            else:
                error = f"Unknown adjust setting: {first}"

        if error:
            print(f"Error: {error}")
            error_state = SpatialInference(
                input_indices=[], operation=f"adjust({settings})", fact=self
            )
            error_state.error = error
            return False
        return True

    def deduce_categories(self, categories: str):
        """
        Deduce which spatial predicate categories to enable based on input string.
        """
        print("Deduce categories:", categories)
        self.deduce.topology = "topo" in categories
        self.deduce.connectivity = "connect" in categories
        self.deduce.comparability = "compar" in categories
        self.deduce.similarity = "simil" in categories
        self.deduce.sectoriality = "sector" in categories
        self.deduce.visibility = "visib" in categories
        self.deduce.geography = "geo" in categories

    # === Logging Implementation ===

    def log(self, predicates: str):
        """
        Log the specified predicates to a Markdown file, exactly as in the Swift version.
        """
        # --- 1) initialize log folder ---
        if self.logFolder is None:
            downloads = Path.home() / "Downloads"
            if downloads.exists():
                self.logFolder = downloads
            else:
                self.logFolder = Path.home()

        # --- 2) bump counter & pick indices ---
        self.logCnt += 1
        all_indices = list(range(len(self.objects)))
        if self.chain:
            indices = self.chain[-1].output
        else:
            indices = all_indices

        # --- 3) split out "base" and "3D" tokens ---
        toks = [t.strip() for t in predicates.split()]
        if "base" in toks:
            toks.remove("base")
            self.log_base()
        if "3D" in toks:
            toks.remove("3D")
            # pass
            # self.log_3D()   # assume you’ve implemented this stub in Python

        # --- 4) start building Markdown ---
        md = "# " + (self.name or "Spatial Reasoning Log") + "\n"
        if self.description:
            md += self.description
        md += "\n\n"

        # pipeline block
        md += "## Inference Pipeline\n\n```\n"
        md += self.pipeline + "\n```\n\n"

        # chain block
        md += "## Inference Chain\n\n```\n"
        for i, inf in enumerate(self.chain):
            if i > 0:
                md += "| "
            md += f"{inf.operation}  ->  {inf.output}\n"
        md += "```\n\n"

        # fact base
        md += "## Spatial Objects\n\n### Fact Base\n\n"
        for i in all_indices:
            obj = self.objects[i]
            md += f"{i}.  __{obj.id}__: {obj.desc()}\n"
        md += "\n\n"

        # resulting objects
        md += "### Resulting Objects (Output)\n\n"
        mmd_objs = ""
        mmd_rels = ""
        mmd_contacts = ""
        rels = ""
        for i in indices:
            obj = self.objects[i]
            md += f"{i}.  __{obj.id}__: {obj.desc()}\n"
            mmd_objs += f"    {obj.id}\n"

            for relation in self.relations_of(i):
                # predicate-filter
                include = (not toks) or (relation.predicate.value in toks)
                if include:
                    left_link = " -- "
                    if SpatialTerms.symmetric(relation.predicate):
                        left_link = " <-- "
                        mirror = f"{relation.object.id}{left_link}{relation.predicate.value} --> {relation.subject.id}"
                        if mirror in mmd_rels:
                            include = False
                    if include:
                        mmd_rels += f"    {relation.subject.id}{left_link}{relation.predicate.value} --> {relation.object.id}\n"

                # connectivity graph
                if relation.predicate in SpatialPredicate.connectivity:
                    do_add = True
                    left_link = " -- "
                    if relation.predicate == SpatialPredicate.by:
                        left_link = " <-- "
                        mirror = f"{relation.object.id}{left_link}{relation.predicate.value} --> {relation.subject.id}"
                        if mirror in mmd_contacts:
                            do_add = False
                    if do_add:
                        mmd_contacts += f"    {relation.subject.id}{left_link}{relation.predicate.value} --> {relation.object.id}\n"

                # flat list
                rels += f"* {relation.desc()}\n"

        # mermaid spatial-relations graph
        if mmd_rels:
            md += "\n## Spatial Relations Graph\n\n"
            md += "```mermaid\ngraph LR;\n" + mmd_objs + mmd_rels + "```\n"

        # mermaid connectivity graph
        if mmd_contacts:
            md += "\n## Connectivity Graph\n\n"
            md += "```mermaid\ngraph TD;\n" + mmd_contacts + "```\n"

        # detailed list
        md += "\n## Spatial Relations\n\n" + rels + "\n"

        # --- 5) write file ---
        multiple = self.pipeline.count("log(") > 1
        suffix = str(self.logCnt) if multiple else ""
        filename = f"log{suffix}.md"
        path = self.logFolder / filename
        try:
            path.write_text(md, encoding="utf-16")
        except Exception as e:
            print(f"Error writing log file: {e}")

    def log_base(self):
        """
        Log the fact base to a JSON file.
        """
        try:
            log_base_path = self.logFolder / "logBase.json"
            with open(log_base_path, "w", encoding="utf-8") as f:
                json.dump(self.base, f, indent=4)
        except Exception as e:
            print(f"Error writing log base: {e}")

    @staticmethod
    def print_relations(relations: List[SpatialRelation]):
        """
        Print a list of SpatialRelations in a readable format.
        """
        for relation in relations:
            print(
                f"{relation.subject.id} {relation.predicate} {relation.object.id} | Δ:{relation.delta:.2f}  α:{relation.yaw:.1f}°"
            )

    def log(self, predicates: str):
        """
        Log the specified predicates to a Markdown file, exactly as in the Swift version.
        """
        # --- 1) initialize log folder ---
        if self.logFolder is None:
            downloads = Path.home() / "Downloads"
            if downloads.exists():
                self.logFolder = downloads
            else:
                self.logFolder = Path.home()

        # --- 2) bump counter & pick indices ---
        self.logCnt += 1
        all_indices = list(range(len(self.objects)))
        if self.chain:
            indices = self.chain[-1].output
        else:
            indices = all_indices

        # --- 3) split out "base" and "3D" tokens ---
        toks = [t.strip() for t in predicates.split()]
        if "base" in toks:
            toks.remove("base")
            self.log_base()
        if "3D" in toks:
            toks.remove("3D")
            self.log_3D()  # assume you’ve implemented this stub in Python

        # --- 4) start building Markdown ---
        md = "# " + (self.name or "Spatial Reasoning Log") + "\n"
        if self.description:
            md += self.description
        md += "\n\n"

        # pipeline block
        md += "## Inference Pipeline\n\n```\n"
        md += self.pipeline + "\n```\n\n"

        # chain block
        md += "## Inference Chain\n\n```\n"
        for i, inf in enumerate(self.chain):
            if i > 0:
                md += "| "
            md += f"{inf.operation}  ->  {inf.output}\n"
        md += "```\n\n"

        # fact base
        md += "## Spatial Objects\n\n### Fact Base\n\n"
        for i in all_indices:
            obj = self.objects[i]
            md += f"{i}.  __{obj.id}__: {obj.desc()}\n"
        md += "\n\n"

        # resulting objects
        md += "### Resulting Objects (Output)\n\n"
        mmd_objs = ""
        mmd_rels = ""
        mmd_contacts = ""
        rels = ""
        for i in indices:
            obj = self.objects[i]
            md += f"{i}.  __{obj.id}__: {obj.desc()}\n"
            mmd_objs += f"    {obj.id}\n"

            for relation in self.relations_of(i):
                # predicate-filter
                include = (not toks) or (relation.predicate.value in toks)
                if include:
                    left_link = " -- "
                    if SpatialTerms.symmetric(relation.predicate):
                        left_link = " <-- "
                        mirror = f"{relation.object.id}{left_link}{relation.predicate.value} --> {relation.subject.id}"
                        if mirror in mmd_rels:
                            include = False
                    if include:
                        mmd_rels += f"    {relation.subject.id}{left_link}{relation.predicate.value} --> {relation.object.id}\n"

                # connectivity graph
                print("Connectivity: ", connectivity)
                if relation.predicate in connectivity:
                    do_add = True
                    left_link = " -- "
                    if relation.predicate == SpatialPredicate.by:
                        left_link = " <-- "
                        mirror = f"{relation.object.id}{left_link}{relation.predicate.value} --> {relation.subject.id}"
                        if mirror in mmd_contacts:
                            do_add = False
                    if do_add:
                        mmd_contacts += f"    {relation.subject.id}{left_link}{relation.predicate.value} --> {relation.object.id}\n"

                # flat list
                rels += f"* {relation.desc()}\n"

        # mermaid spatial-relations graph
        if mmd_rels:
            md += "\n## Spatial Relations Graph\n\n"
            md += "```mermaid\ngraph LR;\n" + mmd_objs + mmd_rels + "```\n"

        # mermaid connectivity graph
        if mmd_contacts:
            md += "\n## Connectivity Graph\n\n"
            md += "```mermaid\ngraph TD;\n" + mmd_contacts + "```\n"

        # detailed list
        md += "\n## Spatial Relations\n\n" + rels + "\n"

        # --- 5) write file ---
        multiple = self.pipeline.count("log(") > 1
        suffix = str(self.logCnt) if multiple else ""
        filename = f"log{suffix}.md"
        path = Path(self.logFolder) / filename
        try:
            path.write_text(md, encoding="utf-16")
        except Exception as e:
            print(f"Error writing log file: {e}")

    def log_base(self):
        """
        Write out the full `self.base` dict as JSON.
        """
        try:
            path = self.logFolder / "logBase.json"
            with path.open("w", encoding="utf-8") as f:
                json.dump(self.base, f, indent=4)
        except Exception as e:
            print(f"Error writing base JSON: {e}")

    def log_3D(self):
        """
        Log the 3D representation of the spatial objects.
        """
        # This is a placeholder for the 3D logging functionality.
        # You can implement this method to log the 3D representation of the spatial objects.
        pass
