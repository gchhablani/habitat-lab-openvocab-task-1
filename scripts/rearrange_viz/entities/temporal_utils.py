from collections import defaultdict

def update_object_recep_and_room(initial_object_to_recep, initial_object_to_room, evaluation_propositions, evaluation_constraints=None):
    # Initialize dictionaries to hold potential solutions
    potential_recep = defaultdict(set)
    potential_room = defaultdict(set)
    
    # Track processed objects to handle fallback
    processed_objects = set()
    
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
                            intersect_recep = (potential_recep.get(obj_name_a,  set([initial_object_to_recep[obj_name_a]])) & potential_recep.get(obj_name_b, set([initial_object_to_recep[obj_name_b]])))
                            intersect_room = (potential_room.get(obj_name_a,  set([initial_object_to_room[obj_name_a]])) & potential_room.get(obj_name_b, set([initial_object_to_room[obj_name_b]])))
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