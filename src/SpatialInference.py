import datetime
from typing import List, Dict, Optional, Any
import re

# Placeholder imports for dependencies.
# Ensure that these classes are properly defined in your Python project.
# from spatial_adjustment import SpatialAdjustment
# from spatial_predicate_categories import SpatialPredicateCategories
# from spatial_object import SpatialObject
# from spatial_relation import SpatialRelation
# from spatial_reasoner import SpatialReasoner

class SpatialInference:
    def __init__(self, input_indices: List[int], operation: str, fact: 'SpatialReasoner'):
        self.input: List[int] = input_indices  # Indices to fact.base["objects"]
        self.output: List[int] = []            # Indices to fact.base["objects"]
        self.operation: str = operation
        self.succeeded: bool = False
        self.error: str = ""
        self.fact: 'SpatialReasoner' = fact

        # Parse and execute the operation
        try:
            if self.operation.startswith("filter(") and self.operation.endswith(")"):
                condition = self.operation[7:-1].strip()
                self.filter(condition)
            elif self.operation.startswith("pick(") and self.operation.endswith(")"):
                relations = self.operation[5:-1].strip()
                self.pick(relations)
            elif self.operation.startswith("select(") and self.operation.endswith(")"):
                terms = self.operation[7:-1].strip()
                self.select(terms)
            elif self.operation.startswith("sort(") and self.operation.endswith(")"):
                attribute = self.operation[5:-1].strip()
                self.sort(attribute)
            elif self.operation.startswith("slice(") and self.operation.endswith(")"):
                range_str = self.operation[6:-1].strip()
                self.slice(range_str)
            elif self.operation.startswith("produce(") and self.operation.endswith(")"):
                terms = self.operation[8:-1].strip()
                self.produce(terms)
            elif self.operation.startswith("calc(") and self.operation.endswith(")"):
                assignments = self.operation[5:-1].strip()
                self.calc(assignments)
            elif self.operation.startswith("map(") and self.operation.endswith(")"):
                assignments = self.operation[4:-1].strip()
                self.map(assignments)
            elif self.operation.startswith("reload(") and self.operation.endswith(")"):
                self.reload()
            else:
                self.error = f"Unknown inference operation: {self.operation}"
        except Exception as e:
            self.error = f"Exception during operation '{self.operation}': {str(e)}"

    def add(self, index: int):
        if index not in self.output:
            self.output.append(index)

    def filter(self, condition: str):
        predicate = SpatialInference.attribute_predicate(condition)
        if predicate is None:
            self.error = f"Invalid filter condition: {condition}"
            return

        base_objects = self.fact.base.get("objects", [])
        for i in self.input:
            obj = base_objects[i]
            try:
                result = predicate(obj)
                if result:
                    self.add(i)
            except Exception as e:
                self.error = f"Filter evaluation error for object {i}: {str(e)}"
                return
        self.succeeded = True

    def pick(self, relations: str):
        predicates = SpatialInference.extract_keywords(relations)
        for i in self.input:
            for j, subject in enumerate(self.fact.objects):
                if i != j:
                    cond = relations
                    for predicate in predicates:
                        if self.fact.does(subject=self.fact.objects[j], have=predicate, with_obj_idx=i):
                            cond = cond.replace(predicate, "True")
                        else:
                            cond = cond.replace(predicate, "False")
                    try:
                        result = eval(cond)
                        if result:
                            self.add(j)
                    except Exception as e:
                        self.error = f"Pick evaluation error for relation '{relations}' between {i} and {j}: {str(e)}"
                        return
        self.succeeded = bool(self.output)

    def select(self, terms: str):
        parts = [part.strip() for part in terms.split("?")]
        if len(parts) == 1:
            relations = parts[0]
            conditions = ""
        elif len(parts) == 2:
            relations, conditions = parts
        else:
            self.error = "Invalid select query format."
            return

        predicates = SpatialInference.extract_keywords(relations)
        base_objects = self.fact.base.get("objects", [])
        for i in self.input:
            for j, subject in enumerate(self.fact.objects):
                if i != j:
                    cond = relations
                    for predicate in predicates:
                        if self.fact.does(subject=self.fact.objects[j], have=predicate, with_obj_idx=i):
                            cond = cond.replace(predicate, "True")
                        else:
                            cond = cond.replace(predicate, "False")
                    try:
                        result = eval(cond)
                        if result:
                            if conditions:
                                attr_predicate = SpatialInference.attribute_predicate(conditions)
                                if attr_predicate and attr_predicate(base_objects[j]):
                                    self.add(i)
                            else:
                                self.add(i)
                    except Exception as e:
                        self.error = f"Select evaluation error for object {i}: {str(e)}"
                        return
        self.succeeded = bool(self.output)

    def map(self, assignments: str):
        self.assign(assignments, self.input)
        self.fact.load()  # Reload the fact base after mapping
        self.output = self.input.copy()
        self.succeeded = bool(self.output)

    def assign(self, assignments: str, indices: List[int]):
        assignment_list = [assignment.strip() for assignment in assignments.split(";")]
        base_objects = self.fact.base.get("objects", [])

        for i in indices:
            obj_dict = dict(base_objects[i])  # Create a copy to modify
            data_dict = self.fact.base.get("data", {}).copy()
            obj_dict.update(data_dict)

            for assignment in assignment_list:
                if "=" in assignment:
                    key, expr = [part.strip() for part in assignment.split("=", 1)]
                    try:
                        # Prepare the local variables for eval
                        local_vars = obj_dict.copy()
                        value = eval(expr, {"__builtins__": {}}, local_vars)
                        if value is not None:
                            obj_dict[key] = value
                    except Exception as e:
                        self.error = f"Assign evaluation error for object {i}, assignment '{assignment}': {str(e)}"
                        return

            # Update the SpatialObject with the new dictionary
            self.fact.objects[i].from_any(obj_dict)
            # Also update the fact base
            self.fact.base["objects"][i] = obj_dict

    def calc(self, assignments: str):
        assignment_list = [assignment.strip() for assignment in assignments.split(";")]
        for assignment in assignment_list:
            if "=" in assignment:
                key, expr = [part.strip() for part in assignment.split("=", 1)]
                try:
                    # Prepare the local variables for eval
                    local_vars = self.fact.base.copy()
                    value = eval(expr, {"__builtins__": {}}, local_vars)
                    if value is not None:
                        self.fact.set_data(key, value)
                except Exception as e:
                    self.error = f"Calc evaluation error for assignment '{assignment}': {str(e)}"
                    return
        self.output = self.input.copy()
        self.succeeded = bool(self.output)

    def slice(self, range_str: str):
        # Replace ".." with "." to handle inclusive ranges
        range_str = range_str.replace("..", ".")
        parts = [part.strip() for part in range_str.split(".")]
        lower = 0
        upper = 0

        if len(parts) >= 1 and parts[0]:
            lower = int(parts[0])
            if lower >= len(self.input):
                lower = len(self.input)
            if lower < 0:
                lower = len(self.input) + lower
            else:
                lower = lower - 1

        if len(parts) >= 2 and parts[1]:
            upper = int(parts[1])
            if upper >= len(self.input):
                upper = len(self.input)
            if upper < 0:
                upper = len(self.input) + upper
            else:
                upper = upper - 1
        else:
            upper = lower

        if lower > upper:
            lower, upper = upper, lower

        # Clamp the range within valid indices
        lower = max(0, lower)
        upper = min(len(self.input) - 1, upper)

        idx_range = range(lower, upper + 1)
        self.output = [self.input[i] for i in idx_range]
        self.succeeded = bool(self.output)

    def sort(self, attribute: str):
        ascending = False
        sorted_objects = []
        input_objects = [self.fact.objects[i] for i in self.input]
        sorted_objects = input_objects.copy()

        # Check for ascending order if specified
        match = re.match(r"(\w+)\s*([<>])", attribute)
        if match:
            attr_name, order = match.groups()
            if order == "<":
                ascending = True
            else:
                ascending = False
            attr_name = attr_name.strip()
        else:
            attr_name = attribute.strip()

        # Determine the sorting key
        def sort_key(obj: 'SpatialObject'):
            if "." in attr_name:
                # Sort by relation value
                return obj.relation_value(attr_name, pre=self.fact.backtrace())
            else:
                # Sort by attribute value
                return obj.get_attribute_value(attr_name)

        try:
            sorted_objects.sort(key=sort_key, reverse=not ascending)
        except Exception as e:
            self.error = f"Sort evaluation error for attribute '{attribute}': {str(e)}"
            return

        # Update the output indices based on sorted order
        self.output = []
        for obj in sorted_objects:
            idx = self.fact.objects.index(obj)
            self.add(idx)
        self.succeeded = bool(self.output)

    def sort_by_relation(self, attribute: str):
        ascending = False
        sorted_objects = []
        pre_indices = self.fact.backtrace()
        input_objects = [self.fact.objects[i] for i in self.input]
        sorted_objects = input_objects.copy()

        # Check for ascending order if specified
        match = re.match(r"(\w+)\s*([<>])", attribute)
        if match:
            attr_name, order = match.groups()
            if order == "<":
                ascending = True
            else:
                ascending = False
            attr_name = attr_name.strip()
        else:
            attr_name = attribute.strip()

        # Determine the sorting key
        def sort_key(obj: 'SpatialObject'):
            try:
                return obj.relation_value(attr_name, pre=pre_indices)
            except Exception:
                return 0  # Default value if relation_value fails

        try:
            sorted_objects.sort(key=sort_key, reverse=not ascending)
        except Exception as e:
            self.error = f"Sort by relation error for attribute '{attribute}': {str(e)}"
            return

        # Update the output indices based on sorted order
        self.output = []
        for obj in sorted_objects:
            idx = self.fact.objects.index(obj)
            self.add(idx)
        self.succeeded = bool(self.output)

    def produce(self, terms: str):
        print(terms)  # Debug print, can be removed or replaced with logging
        parts = [part.strip() for part in terms.split(":")]
        if not parts:
            self.error = "Invalid produce terms."
            return

        rule = parts[0]
        assignments = parts[1] if len(parts) > 1 else ""
        indices: List[int] = []
        new_objects: List[Dict[str, Any]] = []

        if rule in ["group", "aggregate"]:
            if self.input:
                input_objects = [self.fact.objects[i] for i in self.input]
                sorted_objects = sorted(input_objects, key=lambda o: o.volume, reverse=True)
                largest_object = sorted_objects[0] if sorted_objects else None

                if largest_object:
                    min_y = 0.0
                    max_y = largest_object.height
                    min_x = -largest_object.width / 2.0
                    max_x = largest_object.width / 2.0
                    min_z = -largest_object.depth / 2.0
                    max_z = largest_object.depth / 2.0
                    group_id = f"group:{largest_object.id}"

                    for obj in sorted_objects[1:]:
                        local_pts = largest_object.into_local(obj.points(local=False))
                        for pt in local_pts:
                            min_x = min(min_x, float(pt.x))
                            max_x = max(max_x, float(pt.x))
                            min_y = min(min_y, float(pt.y))
                            max_y = max(max_y, float(pt.y))
                            min_z = min(min_z, float(pt.z))
                            max_z = max(max_z, float(pt.z))
                        group_id += f"+{obj.id}"

                    w = max_x - min_x
                    h = max_y - min_y
                    d = max_z - min_z
                    dx = min_x + w / 2.0
                    dy = min_y + h / 2.0
                    dz = min_z + d / 2.0

                    obj_idx = self.fact.index_of_id(group_id) or -1
                    group = self.fact.objects[obj_idx] if obj_idx >= 0 else SpatialObject(id=group_id)
                    group.set_position(largest_object.pos)
                    group.rot_shift(-largest_object.angle, dx, dy, dz)
                    group.angle = largest_object.angle
                    group.width = w
                    group.height = h
                    group.depth = d
                    group.cause = "rule_produced"

                    if obj_idx < 0:
                        new_objects.append(group.as_dict())
                        indices.append(len(self.fact.objects))
                        self.fact.objects.append(group)

        elif rule in ["copy", "duplicate"]:
            for i in self.input:
                copy_id = f"copy:{self.fact.objects[i].id}"
                idx = self.fact.index_of_id(copy_id)
                if idx is None:
                    copy_obj = SpatialObject(id=copy_id)
                    copy_obj.from_any(self.fact.objects[i].to_any())
                    copy_obj.cause = "rule_produced"
                    copy_obj.set_position(self.fact.objects[i].pos)
                    copy_obj.angle = self.fact.objects[i].angle
                    new_objects.append(copy_obj.as_dict())
                    indices.append(len(self.fact.objects))
                    self.fact.objects.append(copy_obj)
                else:
                    indices.append(idx)

        elif rule == "by":
            processed_bys = set()
            for i in self.input:
                rels = self.fact.relations_with(i, predicate="by")
                for rel in rels:
                    subject_idx = self.fact.index_of_id(rel.subject.id)
                    if subject_idx is not None and subject_idx in self.input:
                        key = f"{self.fact.objects[i].id}-{rel.subject.id}"
                        if key not in processed_bys:
                            nearest_pts = self.fact.objects[i].pos.nearest(rel.subject.points())
                            by_id = f"by:{self.fact.objects[i].id}-{rel.subject.id}"
                            obj_idx = self.fact.index_of_id(by_id) or -1
                            obj = self.fact.objects[obj_idx] if obj_idx >= 0 else SpatialObject(id=by_id)
                            obj.cause = "rule_produced"
                            if nearest_pts:
                                obj.set_position(nearest_pts[0])
                                obj.angle = self.fact.objects[i].angle
                                obj.width = max(rel.delta, self.fact.adjustment.maxGap)
                                obj.depth = max(rel.delta, self.fact.adjustment.maxGap)
                                obj.height = rel.subject.height
                                new_objects.append(obj.as_dict())
                                indices.append(len(self.fact.objects))
                                self.fact.objects.append(obj)
                            processed_bys.add(key)

        else:
            self.error = f"Unknown rule '{rule}' in produce()"
            return

        if indices:
            self.fact.base["objects"].extend(new_objects)
            if assignments:
                self.assign(assignments, indices)
            self.output = self.input.copy()
            for idx in indices:
                if idx not in self.output:
                    self.output.append(idx)
        else:
            self.output = self.input.copy()

        self.fact.load()
        self.succeeded = not self.error

    def reload(self):
        self.fact.sync_to_objects()
        self.fact.load()
        self.output = list(range(len(self.fact.objects)))
        self.succeeded = bool(self.output)

    def has_failed(self) -> bool:
        return bool(self.error)

    def is_manipulating(self) -> bool:
        operations = ["filter", "pick", "select", "produce", "slice"]
        return any(self.operation.startswith(op) for op in operations)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "input": self.input,
            "output": self.output,
            "error": self.error,
            "succeeded": self.succeeded
        }

    @staticmethod
    def attribute_predicate(condition: str) -> Optional[Any]:
        """
        Convert a condition string into a callable predicate function.
        For security reasons, using eval is dangerous. Consider using a safe parser.
        """
        try:
            # Replace attribute names with dictionary access
            # e.g., "width > 2" becomes "obj['width'] > 2"
            # Assuming all attributes are accessed via 'obj'
            # This is a simplistic approach and may need to be expanded
            pattern = re.compile(r'\b\w+\b')
            condition_converted = pattern.sub(lambda match: f"obj.get('{match.group(0)}', 0)", condition)
            # Compile the condition into a lambda function
            predicate = eval(f"lambda obj: {condition_converted}", {"__builtins__": {}})
            return predicate
        except Exception as e:
            print(f"Error creating attribute predicate: {e}")
            return None

    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """
        Extract lowercase letter sequences as keywords from a given text.
        """
        return re.findall(r'\b[a-z]+\b', text)

# Helper function to safely evaluate expressions
def safe_eval(expression: str, variables: Dict[str, Any]) -> Any:
    """
    Safely evaluate an expression using only the provided variables.
    This function restricts the available built-ins for security.
    """
    try:
        return eval(expression, {"__builtins__": {}}, variables)
    except Exception as e:
        raise ValueError(f"Error evaluating expression '{expression}': {str(e)}")
