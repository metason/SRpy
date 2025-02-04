import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import json

# Import the SpatialObject and dependencies
from src.vector3 import Vector3
from src.Vector2 import Vector2
from src.SpatialBasics import (
    NearbySchema,
    SectorSchema,
    SpatialAdjustment,
    SpatialPredicateCategories,
    ObjectConfidence,
    SpatialAtribute,
    SpatialExistence,
    ObjectCause,
    MotionState,
    ObjectShape,
    ObjectHandling,
    defaultAdjustment
)
from src.SpatialPredicate import (
    SpatialPredicate,
    PredicateTerm,
    SpatialTerms,
    proximity,
    directionality,
    adjacency,
    orientations,
    assembly,
    topology,
    contacts,
    connectivity,
    comparability,
    similarity,
    visibility,
    geography,
    sectors,
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
        self.base: Dict[str, Any] = {}  # Fact base for read/write access of expression evaluation
        self.snapTime: datetime.datetime = datetime.datetime.now()  # Load or update time of fact base

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
        return self.base.copy()

    def load_snapshot(self, snapshot: Dict[str, Any]):
        """
        Load a snapshot into the fact base.
        """
        self.base = snapshot.copy()
        self.sync_to_objects()

    # === Recording and Backtracing ===

    def record(self, inference: SpatialInference):
        """
        Record a SpatialInference in the chain and fact base.
        """
        self.chain.append(inference)
        chain_list = self.base.get("chain", [])
        chain_list.append(inference.as_dict())
        self.base["chain"] = chain_list

    def backtrace(self) -> List[int]:
        """
        Backtrace to find the input indices of the last manipulating inference.
        """
        for inference in reversed(self.chain):
            if inference.is_manipulating():
                return inference.input
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
                content = op[7:-1].strip()
                self.deduce_categories(content)
            else:
                input_chain = self.chain[-1].output if self.chain else indices
                inference = SpatialInference(input=input_chain, operation=op, reasoner=self)
                self.record(inference)
                if inference.has_failed():
                    self.log_error()
                    break

        self.sync_to_objects()

        if self.chain:
            return self.chain[-1].succeeded
        elif "log(" in pipeline:
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
            print(self.chain[-1].error)

    @staticmethod
    def print_relations(relations: List[SpatialRelation]):
        """
        Print a list of SpatialRelations in a readable format.
        """
        for relation in relations:
            print(f"{relation.subject.id} {relation.predicate} {relation.object.id} | Δ:{relation.delta:.2f}  α:{relation.yaw:.1f}°")

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
            error_state = SpatialInference(input=[], operation=f"adjust({settings})", reasoner=self)
            error_state.error = error
            return False
        return True

    def deduce_categories(self, categories: str):
        """
        Deduce which spatial predicate categories to enable based on input string.
        """
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
        Log the specified predicates. Excludes visualization-related logging.
        """
        # Initialize log folder if not set
        if self.logFolder is None:
            try:
                self.logFolder = Path.home() / "Downloads"
                if not self.logFolder.exists():
                    self.logFolder = Path.home()
            except Exception as e:
                self.logFolder = Path.home()

        self.logCnt += 1
        all_indices = list(range(len(self.objects)))
        indices = self.chain[-1].output if self.chain else all_indices
        predicates_list = [p.strip() for p in predicates.split(" ")]

        if "base" in predicates_list:
            predicates_list.remove("base")
            self.log_base()
        if "3D" in predicates_list:
            predicates_list.remove("3D")
            # Visualization code for 3D logging is omitted as per instruction

        # Build Markdown content
        md = f"# {self.name if self.name else 'Spatial Reasoning Log'}\n"
        md += f"{self.description if self.description else ''}\n\n"
        md += "## Inference Pipeline\n\n```\n" + self.pipeline + "\n```\n\n"
        md += "## Inference Chain\n\n```\n"
        for idx, inference in enumerate(self.chain):
            if idx > 0:
                md += "| "
            md += f"{inference.operation}  ->  {inference.output}\n"
        md += "```\n\n"

        md += "## Spatial Objects\n\n### Fact Base\n\n"
        for i in all_indices:
            obj = self.objects[i]
            md += f"{i}.  __{obj.id}__: {obj.desc()}\n"

        md += "\n### Resulting Objects (Output)\n\n"
        mmd_objs = ""
        mmd_rels = ""
        mmd_contacts = ""
        rels = ""
        for i in indices:
            obj = self.objects[i]
            mmd_objs += f"    {obj.id}\n"
            md += f"{i}.  __{obj.id}__: {obj.desc()}\n"

            for relation in self.relations_of(i):
                do_add = False
                if predicates_list:
                    if relation.predicate.value in predicates_list:
                        do_add = True
                else:
                    do_add = True

                if do_add:
                    left_link = " -- "
                    #if relation.predicate.is_symmetric():
                    if SpatialTerms.symmetric(relation.predicate):
                        left_link = " <-- "
                        search_by = f"{relation.object.id}{left_link}{relation.predicate.value} --> {relation.subject.id}"
                        if search_by in mmd_rels:
                            do_add = False
                    if do_add:
                        mmd_rels += f"    {relation.subject.id}{left_link}{relation.predicate.value} --> {relation.object.id}\n"

                if relation.predicate in contacts:
                    do_add_contact = True
                    left_link = " -- "
                    if relation.predicate == SpatialPredicate.by:
                        left_link = " <-- "
                        search_by = f"{relation.object.id}{left_link}{relation.predicate.value} --> {relation.subject.id}"
                        if search_by in mmd_contacts:
                            do_add_contact = False
                    if do_add_contact:
                        mmd_contacts += f"    {relation.subject.id}{left_link}{relation.predicate.value} --> {relation.object.id}\n"

                if relation.predicate in contacts:
                    rels += f"* {relation.desc()}\n"

        # Append Spatial Relations Graph
        if mmd_rels:
            md += "\n## Spatial Relations Graph\n\n```mermaid\ngraph LR;\n" + mmd_objs + mmd_rels + "```\n"

        # Append Connectivity Graph
        if mmd_contacts:
            md += "\n## Connectivity Graph\n\n```mermaid\ngraph TD;\n" + mmd_contacts + "```\n"

        # Append Spatial Relations List
        md += "\n## Spatial Relations\n\n" + rels + "\n"

        # Determine log file name
        multiple_logs = self.pipeline.count("log(") > 2
        counter_str = str(self.logCnt) if multiple_logs else ""
        log_filename = f"log{counter_str}.md"
        log_path = self.logFolder / log_filename

        # Write Markdown to file
        try:
            with open(log_path, "w", encoding="utf-16") as f:
                f.write(md)
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

    # === Visualization Methods ===
    # All visualization-related methods (e.g., log3D) are omitted as per instruction.

    # === Additional Methods ===

    @staticmethod
    def print_relations(relations: List[SpatialRelation]):
        """
        Print a list of SpatialRelations in a readable format.
        """
        for relation in relations:
            print(f"{relation.subject.id} {relation.predicate} {relation.object.id} | Δ:{relation.delta:.2f}  α:{relation.yaw:.1f}°")