import re
import keyword
import re
from .SpatialObject import SpatialObject
from typing import Any, Dict, List, Optional
from .SpatialObject import SpatialObject
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



class SpatialInference:
    def __init__(self, input_indices: List[int], operation: str, fact: 'SpatialReasoner'):
        """
        Perform a single pipeline operation (e.g., filter(...), produce(...)) on the
        objects in `fact`, given their indices in `input_indices`.
        """
        self.input: List[int] = input_indices      # Indices to fact.base["objects"]
        self.output: List[int] = []               # Indices to fact.base["objects"]
        self.operation: str = operation
        self.succeeded: bool = False
        self.error: str = ""
        self.fact: 'SpatialReasoner' = fact

        # Parse and execute the operation
        try:
            op = self.operation.strip()
            # Check which operation we have and call the matching method:
            if op.startswith("filter(") and op.endswith(")"):
                condition = op[7:-1].strip()
                self.filter(condition)

            elif op.startswith("pick(") and op.endswith(")"):
                relations = op[5:-1].strip()
                self.pick(relations)

            elif op.startswith("select(") and op.endswith(")"):
                terms = op[7:-1].strip()
                self.select(terms)

            elif op.startswith("sort(") and op.endswith(")"):
                attribute = op[5:-1].strip()
                self.sort(attribute)

            elif op.startswith("slice(") and op.endswith(")"):
                range_str = op[6:-1].strip()
                self.slice(range_str)

            elif op.startswith("produce(") and op.endswith(")"):
                terms = op[8:-1].strip()
                self.produce(terms)

            elif op.startswith("calc(") and op.endswith(")"):
                assignments = op[5:-1].strip()
                self.calc(assignments)

            elif op.startswith("map(") and op.endswith(")"):
                assignments = op[4:-1].strip()
                self.map(assignments)

            elif op.startswith("reload(") and op.endswith(")"):
                self.reload()

            else:
                # Unrecognized operation
                self.error = f"Unknown inference operation: '{op}'"
        except Exception as e:
            self.error = f"Exception during operation '{self.operation}': {str(e)}"

    def add(self, index: int):
        """Utility to add an index to self.output if not already present."""
        if index not in self.output:
            self.output.append(index)

    # ----------------------------------------------------------------------
    #                            PIPELINE METHODS
    # ----------------------------------------------------------------------

    def filter(self, condition: str):
        """
        Keep only objects that satisfy a boolean condition on attributes.
        Example: filter("label=='Wall' and confidence.label > 0.7")
        """
        predicate = SpatialInference.attribute_predicate(condition)
        if predicate is None:
            self.error = f"Invalid filter condition: {condition}"
            return

        base_objects = self.fact.base.get("objects", [])
        for i in self.input:
            obj_data = base_objects[i]  # Typically a dict describing object
            try:
                result = predicate(obj_data)
                if result:
                    self.add(i)
            except Exception as e:
                self.error = f"Filter evaluation error for object {i}: {str(e)}"
                return

        self.succeeded = True

    def pick(self, relations: str):
        """
        Keep objects whose relationship with other objects satisfies some boolean expression.
        E.g. pick("adjacent or above") might check adjacency or vertical relation.
        This simplistic example tries to interpret each relation as a keyword in `fact.does(...)`.
        """
        predicates = SpatialInference.extract_keywords(relations)

        for i in self.input:
            # i is the "reference" object
            for j, subject in enumerate(self.fact.objects):
                if i == j:
                    continue

                # Replace each predicate in `relations` with True/False
                cond = relations
                for predicate in predicates:
                    if self.fact.does(subject=subject, have=predicate, with_obj_idx=i):
                        cond = cond.replace(predicate, "True")
                    else:
                        cond = cond.replace(predicate, "False")

                # Evaluate the final condition string
                # e.g. "True or False" => True
                try:
                    result = eval(cond)
                    if result:
                        self.add(j)
                except Exception as e:
                    self.error = f"Pick evaluation error for relation '{relations}' between {i} and {j}: {str(e)}"
                    return

        self.succeeded = bool(self.output)

    def select(self, terms: str):
        """
        A more advanced pick + attribute check.
        Typically: "relations ? conditions"
          e.g. select("adjacent or above ? label=='Target'")
        If the relation expression is True, we further check the attribute `conditions`.
        """
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
                if i == j:
                    continue

                # Evaluate the relationship expression
                cond = relations
                for predicate in predicates:
                    if self.fact.does(subject=subject, have=predicate, with_obj_idx=i):
                        cond = cond.replace(predicate, "True")
                    else:
                        cond = cond.replace(predicate, "False")
                try:
                    rel_result = eval(cond)
                    if rel_result:
                        # If there's a second attribute condition, check that too
                        if conditions:
                            attr_predicate = SpatialInference.attribute_predicate(conditions)
                            obj_data = base_objects[j]
                            if attr_predicate and attr_predicate(obj_data):
                                self.add(i)
                        else:
                            self.add(i)
                except Exception as e:
                    self.error = f"Select evaluation error for object {i}: {str(e)}"
                    return

        self.succeeded = bool(self.output)

    def sort(self, attribute: str):
        """
        Sort the input objects by a numeric attribute or relation-based value.
        Example: sort("width"), sort("volume <"), sort("distanceTo=someObj <")
        If we see a trailing '<', that implies ascending order. Otherwise descending.
        """
        ascending = attribute.endswith("<")
        # Remove any trailing symbol like "<" or ">"
        cleaned_attr = attribute.replace("<", "").replace(">", "").strip()

        input_objs = [self.fact.objects[i] for i in self.input]

        # Decide if it's a direct attribute sort or a 'relationValue' sort.
        # For simplicity, check if there's a dot or known relation pattern:
        # Or we can parse "distanceTo=otherObj" if needed.
        # Here we do a simple fallback: if `cleaned_attr` is in (width, height, volume, etc.), we do a direct attribute read.
        # Otherwise we might do a more advanced approach (like `obj.get_attribute_value`).
        try:
            # Example custom sorting:
            if cleaned_attr == "width":
                sorted_objs = sorted(input_objs, key=lambda o: o.width, reverse=not ascending)
            elif cleaned_attr == "height":
                sorted_objs = sorted(input_objs, key=lambda o: o.height, reverse=not ascending)
            elif cleaned_attr == "volume":
                sorted_objs = sorted(input_objs, key=lambda o: o.volume, reverse=not ascending)
            else:
                # Fallback: dynamic accessor
                sorted_objs = sorted(
                    input_objs,
                    key=lambda o: o.dataValue(cleaned_attr),
                    reverse=not ascending
                )

        except Exception as e:
            self.error = f"Sort evaluation error for attribute '{attribute}': {str(e)}"
            return

        # Convert sorted objects back to their indices
        self.output = []
        for obj in sorted_objs:
            idx = self.fact.objects.index(obj)
            self.add(idx)

        self.succeeded = bool(self.output)

    def slice(self, range_str: str):
        """
        Subset the input list by a 1-based inclusive slice, e.g. slice("1..3").
        Negative numbers can be used from the end, e.g. slice("-2..-1").
        """
        # Replace ".." with "." for consistency
        range_str = range_str.replace("..", ".")
        parts = [p.strip() for p in range_str.split(".")]

        # Default slice is a single element
        lower = 1
        upper = 1
        if len(parts) >= 1 and parts[0]:
            lower = int(parts[0])
        if len(parts) >= 2 and parts[1]:
            upper = int(parts[1])
        else:
            upper = lower

        # Convert 1-based to 0-based, handle negatives
        # E.g. -1 means the last index in self.input
        def _to_python_index(x: int) -> int:
            if x < 0:
                return len(self.input) + x
            return x - 1

        start_idx = _to_python_index(lower)
        end_idx = _to_python_index(upper)

        # Ensure order
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx

        # Clamp
        start_idx = max(0, start_idx)
        end_idx = min(len(self.input) - 1, end_idx)

        self.output = self.input[start_idx:end_idx+1]
        self.succeeded = bool(self.output)

    def produce(self, terms: str):
        """
        Create new objects or group/aggregate existing ones, based on a rule.
        E.g. produce("group"), produce("copy"), produce("by"), etc.
        You can also handle 'produce("group: color='blue'")' for assignment.
        """
        # Example: "group: color='blue'; label='Cluster'"
        parts = [part.strip() for part in terms.split(":")]
        rule = parts[0]
        assignments = parts[1] if len(parts) > 1 else ""

        new_indices: List[int] = []
        new_objects: List[Dict[str, Any]] = []
        base_objs = self.fact.base.get("objects", [])

        if rule in ("group", "aggregate"):
            # Simple example: Combine bounding extents of input objects into one "group" object.
            input_objs = [self.fact.objects[i] for i in self.input]
            if not input_objs:
                self.output = self.input[:]
                self.succeeded = True
                return

            # Sort by volume
            sorted_objs = sorted(input_objs, key=lambda o: o.volume, reverse=True)
            largest:SpatialObject = sorted_objs[0]

            # Very naive bounding box approach
            # Suppose each object has .points(local=False) returning a list of 3D coords
            min_x = -largest.width / 2.0
            max_x = +largest.width / 2.0
            min_y = 0
            max_y = largest.height
            min_z = -largest.depth / 2.0
            max_z = +largest.depth / 2.0

            group_id = f"group:{largest.id}"

            for obj in sorted_objs[1:]:
                local_pts = largest.intoLocal_pts(obj.points(local=False))
                for pt in local_pts:
                    min_x = min(min_x, pt.x)
                    max_x = max(max_x, pt.x)
                    min_y = min(min_y, pt.y)
                    max_y = max(max_y, pt.y)
                    min_z = min(min_z, pt.z)
                    max_z = max(max_z, pt.z)
                group_id += f"+{obj.id}"

            # Build or update the group object
            w = max_x - min_x
            h = max_y - min_y
            d = max_z - min_z

            obj_idx = self.fact.index_of_id(group_id)
            if obj_idx is not None:
                group_obj = self.fact.objects[obj_idx]
            else:
                from .SpatialObject import SpatialObject
                group_obj = SpatialObject(id=group_id)
                self.fact.objects.append(group_obj)
                new_indices.append(len(self.fact.objects)-1)

            
            dx = min_x + (w / 2.0)
            dy = min_y / 2.0
            dz = min_z + (d / 2.0)
            
                
            group_obj.setPosition(largest.position)
            group_obj.rotShift(largest.angle, dx=dx, dy=dy, dz=dz)
            group_obj.angle = largest.angle
            group_obj.width = w
            group_obj.height = h
            group_obj.depth = d
            group_obj.cause = ObjectCause.rule_produced   
            
            # Sync back to base
            if obj_idx is None:
                new_objects.append(group_obj.asDict())

        elif rule in ("copy", "duplicate"):
            # Make copies of each input object
            for i in self.input:
                original = self.fact.objects[i]
                copy_id = f"copy:{original.id}"
                # If a copy already exists, skip
                if self.fact.index_of_id(copy_id) is not None:
                    continue
                # Otherwise create new
                from .SpatialObject import SpatialObject
                copy_obj = SpatialObject(id=copy_id)
                copy_obj.fromAny(original.asDict())
                copy_obj.cause = ObjectCause.rule_produced
                self.fact.objects.append(copy_obj)
                new_indices.append(len(self.fact.objects)-1)
                new_objects.append(copy_obj.asDict())

        elif rule == "by":
            # Example: produce bridging objects by "by" relationships
            processed = set()
            for i in self.input:
                rels = self.fact.relations_with(i, predicate="by")
                for rel in rels:
                    subj_id = rel.subject.id
                    subj_idx = self.fact.index_of_id(subj_id)
                    if subj_idx is not None and subj_idx in self.input:
                        key = f"{self.fact.objects[i].id}-{subj_id}"
                        if key not in processed:
                            # Build bridging object
                            by_id = f"by:{self.fact.objects[i].id}-{subj_id}"
                            if self.fact.index_of_id(by_id) is not None:
                                # Already exists
                                continue
                            from .SpatialObject import SpatialObject
                            new_obj = SpatialObject(id=by_id)
                            new_obj.cause = "rule_produced"
                            # Very naive placement:
                            new_obj.set_position(self.fact.objects[i].position)
                            new_obj.width = max(rel.delta, self.fact.adjustment.maxGap)
                            new_obj.height = self.fact.objects[i].height
                            new_obj.depth = max(rel.delta, self.fact.adjustment.maxGap)

                            self.fact.objects.append(new_obj)
                            new_indices.append(len(self.fact.objects) - 1)
                            new_objects.append(new_obj.asDict())
                            processed.add(key)

        else:
            self.error = f"Unknown rule '{rule}' in produce()"
            return

        # If any new objects were created, add them to base
        if new_objects:
            base_objs.extend(new_objects)
            self.fact.base["objects"] = base_objs

        # Apply optional assignments if present
        if assignments and new_indices:
            self.assign(assignments, new_indices)

        # Final output is the original input plus any new
        self.output = list(self.input)
        for ni in new_indices:
            if ni not in self.output:
                self.output.append(ni)

        # Reload to sync
        self.fact.load()
        self.succeeded = not self.error

    def map(self, assignments: str):
        """
        For each object in input, evaluate the assignments (like "color='red'; label='wall'")
        and set them. Then reload.
        """
        self.assign(assignments, self.input)
        self.fact.load()
        self.output = self.input.copy()
        self.succeeded = bool(self.output)

    def assign(self, assignments: str, indices: List[int]):
        """
        Helper: evaluate multiple key=expr pairs (e.g. "color='red'; score=confidence*2").
        We read each object as a dict, evaluate expr with that dict as local vars, then
        store the result back into the object.
        """
        assignment_list = [a.strip() for a in assignments.split(";") if a.strip()]
        base_objects = self.fact.base.get("objects", [])

        for i in indices:
            obj_dict = dict(base_objects[i])  # local copy
            # We can also unify with 'data' dict:
            data_dict = self.fact.base.get("data", {})
            merged = dict(obj_dict)
            merged.update(data_dict)

            for assignment in assignment_list:
                if "=" in assignment:
                    key, expr = assignment.split("=", 1)
                    key = key.strip()
                    expr = expr.strip()
                    try:
                        # Evaluate with no built-ins, passing merged as local vars
                        value = eval(expr, {"__builtins__": {}}, merged)
                        if value is not None:
                            obj_dict[key] = value
                    except Exception as e:
                        self.error = f"Assign evaluation error for object {i}, assignment '{assignment}': {str(e)}"
                        return

            # Update the actual SpatialObject
            self.fact.objects[i].fromAny(obj_dict)
            # Also update the fact base
            base_objects[i] = obj_dict
        self.fact.base["objects"] = base_objects

    def calc(self, assignments: str):
        """
        Evaluate expressions at the global 'fact.base' level, storing results in base["data"].
        E.g. calc("avgWidth = sum(o.width for o in objects)/len(objects)")
        """
        class ObjectsProxy:
            """
            A proxy that allows:
            - indexing (objects[0]) => the actual SpatialObject
            - attribute access (objects.height) => [o.height for o in self._real_objects]
            """
            def __init__(self, real_objects):
                self._real_objects = real_objects

            def __getitem__(self, index):
                # Return the actual SpatialObject so that .volume etc. works
                return self._real_objects[index]

            def __getattr__(self, name):
                # Return a list of that attribute from all objects
                # e.g. objects.height => [o.height for o in self._real_objects]
                return [getattr(o, name) for o in self._real_objects]

        assignment_list = [a.strip() for a in assignments.split(";") if a.strip()]
        for assignment in assignment_list:
            if "=" in assignment:
                key, expr = assignment.split("=", 1)
                key = key.strip()
                expr = expr.strip()
                try:
                    local_vars = {
                        "base": self.fact.base,
                        # Inject our special proxy as "objects"
                        "objects": ObjectsProxy(self.fact.objects),
                        # Provide a simple average function
                        "average": lambda seq: sum(seq) / len(seq) if seq else 0.0
                    }
                    # Evaluate the expression using a restricted built-in environment
                    value = eval(expr, {"__builtins__": {}}, local_vars)

                    if value is not None:
                        self.fact.set_data(key, value)
                except Exception as e:
                    self.error = f"Calc evaluation error for assignment '{assignment}': {str(e)}"
                    return

        self.output = self.input.copy()
        self.succeeded = bool(self.output)

    def reload(self):
        """
        Reload objects from the base to apply changes.
        """
        self.fact.sync_to_objects()
        self.fact.load()
        self.output = list(range(len(self.fact.objects)))
        self.succeeded = bool(self.output)

    # ----------------------------------------------------------------------
    #                            UTILITY METHODS
    # ----------------------------------------------------------------------

    def has_failed(self) -> bool:
        return bool(self.error)

    def is_manipulating(self) -> bool:
        """
        Return True if this operation changes or filters the set of objects in a non-trivial way.
        Used in backtrace logic, for example.
        """
        ops = ["filter", "pick", "select", "produce", "slice", "map"]
        return any(self.operation.startswith(op + "(") for op in ops)

    def as_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of this inference."""
        return {
            "operation": self.operation,
            "input": self.input,
            "output": self.output,
            "error": self.error,
            "succeeded": self.succeeded
        }

    @staticmethod
    def attribute_predicate(condition: str):
        """
        Convert a condition string into a Python-evaluable lambda that returns bool.
        Example:
            condition = "label == 'Wall' and confidence > 0.8"
        We'll create a function predicate(dict_or_obj) -> bool
        - We do a basic token-based approach: tokens become `obj.get('token', 0)`
        """
        try:
            if not condition:
                return lambda _: True  # No condition => always True

            def is_number(s: str) -> bool:
                try:
                    float(s)
                    return True
                except ValueError:
                    return False

            parts = re.split(r"('.*?')", condition)
            processed_parts = []
            token_pattern = r'\b(?:\w+\.)*\w+\b'

            def token_repl(m: re.Match) -> str:
                token = m.group(0)
                lower = token.lower()
                
                if lower in {"and", "or", "not"}:
                    return lower
                # Python built-ins or keywords
                if token in keyword.kwlist or token in {"True", "False", "None"}:
                    return token
                if is_number(token):
                    return token

                # Possibly a dot chain, e.g. "confidence.value"
                if '.' in token:
                    chain_parts = token.split('.')
                    expr = "obj.get('" + chain_parts[0] + "', {})"
                    for sub in chain_parts[1:]:
                        expr += f".get('{sub}', 0)"
                    return expr
                else:
                    return f"obj.get('{token}', 0)"

            for i, part in enumerate(parts):
                # odd indices => quoted string
                if i % 2 == 1:
                    processed_parts.append(part)
                else:
                    # Replace tokens outside quotes
                    processed_parts.append(re.sub(token_pattern, token_repl, part))

            final_expr = "".join(processed_parts)
            compiled_expr = compile(final_expr, "<string>", "eval")

            def predicate(obj):
                # If the object is a SpatialObject, convert to dict or
                # if we already have a dict, use directly.
                if hasattr(obj, "asDict") and callable(obj.asDict):
                    obj_data = obj.asDict()
                else:
                    obj_data = obj
                return bool(eval(compiled_expr, {"__builtins__": {}}, {"obj": obj_data}))
            return predicate

        except Exception as e:
            print(f"Error in attribute_predicate: {e}")
            return None

    @staticmethod
    def extract_keywords(condition: str) -> List[str]:
        """
        Helper to parse relations (like 'adjacent or by') into distinct tokens
        that we replace with True/False in the pick/select steps.
        Very naive approach that scans for sequences of lowercase letters.
        """
        scanner = re.Scanner([
            (r"[a-z]+", lambda s, t: t),
            (r"[^a-z]+", None)  # skip anything else
        ])
        tokens, remainder = scanner.scan(condition.lower())
        # Return unique tokens in the order encountered
        return list(dict.fromkeys(tokens))
