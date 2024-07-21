from collections import defaultdict
import random

def get_arg_name_from_arg_name(arg_name):
    if arg_name == 'room_ids':
        arg_name = 'room_names'
    elif arg_name == 'object_handles':
        arg_name = 'object_handles'
    elif arg_name == 'receptacle_handles':
        arg_name = 'receptacle_names'
    elif arg_name == 'entity_handles_a':
        arg_name = 'entity_handles_a_names_and_types'
    else:
        arg_name = 'entity_handles_b_names_and_types'
    return arg_name

def update_object_recep_and_room(initial_object_to_recep, initial_object_to_room, evaluation_propositions, evaluation_constraints=None, global_to_local_idx=None):
    # Initialize dictionaries to hold potential solutions
    potential_recep = defaultdict(set)
    potential_room = defaultdict(set)
    
    # Track processed objects to handle fallback
    processed_objects = set()
    
    # Process SameArgConstraints
    if evaluation_constraints:
        for constraint in evaluation_constraints:
            if constraint["type"] == "SameArgConstraint":
                prop_indices = constraint["args"]["proposition_indices"]
                arg_names = constraint["args"]["arg_names"]
                
                # Collect common intersecting values
                common_values = defaultdict(set)
                for idx, arg_name in zip(prop_indices, arg_names):
                    arg_name = get_arg_name_from_arg_name(arg_name)
                    if idx in global_to_local_idx:
                        curr_idx = global_to_local_idx[idx]
                        if curr_idx < len(evaluation_propositions):
                            prop = evaluation_propositions[curr_idx]
                            values = set(prop["args"][arg_name])
                            if common_values[arg_name]:
                                common_values[arg_name] &= values
                            else:
                                common_values[arg_name] = values
                    
                # Update propositions with intersecting values
                for idx, arg_name in zip(prop_indices, arg_names):
                    if idx in global_to_local_idx:
                        curr_idx = global_to_local_idx[idx]
                        if curr_idx < len(evaluation_propositions):
                            evaluation_propositions[curr_idx]["args"][arg_name] = list(common_values[arg_name])

    # Process each proposition
    for proposition in evaluation_propositions:
        func_name = proposition["function_name"]
        args = proposition["args"]
        
        if func_name == "is_inside":
            number = args["number"]
            objects = args["object_names"][:number]
            receptacles = args["receptacle_names"]
            
            for obj_name in objects:
                for receptacle_name in receptacles:
                    potential_recep[obj_name].add(receptacle_name)
                processed_objects.add(obj_name)
        
        elif func_name == "is_on_top":
            number = args["number"]
            objects = args["object_names"][:number]
            receptacles = args["receptacle_names"]
            
            for obj_name in objects:
                for receptacle_name in receptacles:
                    potential_recep[obj_name].add(receptacle_name)
                processed_objects.add(obj_name)

        elif func_name == "is_next_to":
            number = args["number"]
            entities_a = args["entity_handles_a_names_and_types"][:number]
            entities_b = args["entity_handles_b_names_and_types"]
            
            for (obj_name_a, obj_type_a) in entities_a:
                if obj_type_a == "object":
                    for (obj_name_b, obj_type_b) in entities_b:
                        if obj_type_b == "object":
                            intersect_recep = potential_recep.get(
                                obj_name_a, set(
                                    [initial_object_to_recep.get(obj_name_a)] if obj_name_a in initial_object_to_recep else []
                                )
                            ) & potential_recep.get(
                                obj_name_b, set(
                                    [initial_object_to_recep.get(obj_name_b)] if obj_name_b in initial_object_to_recep else []
                                )
                            )
                            intersect_room = potential_room.get(
                                obj_name_a, set(
                                    [initial_object_to_room.get(obj_name_a)] if obj_name_a in initial_object_to_room else []
                                )
                            ) & potential_room.get(
                                obj_name_b, set(
                                    [initial_object_to_room.get(obj_name_b)] if obj_name_b in initial_object_to_room else []
                                )
                            )
                            if intersect_recep or intersect_room:
                                potential_recep[obj_name_a] = intersect_recep
                                potential_recep[obj_name_b] = intersect_recep
                                potential_room[obj_name_a] = intersect_room
                                potential_room[obj_name_b] = intersect_room
                                processed_objects.add(obj_name_a)
                                processed_objects.add(obj_name_b)
    
        elif func_name == "is_in_room":
            number = args["number"]
            objects = args["object_names"][:number]
            rooms = args["room_names"]
            
            for obj_name in objects:
                for room_name in rooms:
                    potential_room[obj_name].add(room_name)
                processed_objects.add(obj_name)
        
        elif func_name == "is_on_floor":
            objects = args["object_names"]
            for obj_name in objects:
                potential_recep.pop(obj_name, None)
                potential_room[obj_name].clear()
                processed_objects.add(obj_name)
    
    # Update the object_to_recep and object_to_room dictionaries
    new_object_to_recep = {}
    new_object_to_room = {}
    
    # Process potential solutions
    for obj_name in set(initial_object_to_recep.keys()).union(potential_recep.keys()):
        if obj_name in processed_objects:
            if potential_recep[obj_name]:
                new_object_to_recep[obj_name] = next(iter(potential_recep[obj_name]))
            else:
                new_object_to_recep[obj_name] = "unknown"
        else:
            new_object_to_recep[obj_name] = initial_object_to_recep.get(obj_name, "unknown")
    
    for obj_name in set(initial_object_to_room.keys()).union(potential_room.keys()):
        if obj_name in processed_objects:
            if potential_room[obj_name]:
                new_object_to_room[obj_name] = next(iter(potential_room[obj_name]))
            else:
                new_object_to_room[obj_name] = "unknown"
        else:
            new_object_to_room[obj_name] = initial_object_to_room.get(obj_name, "unknown")
    
    # Remove entries with "unknown"
    new_object_to_recep = {k: v for k, v in new_object_to_recep.items() if v != "unknown"}
    new_object_to_room = {k: v for k, v in new_object_to_room.items() if v != "unknown"}

    return new_object_to_recep, new_object_to_room