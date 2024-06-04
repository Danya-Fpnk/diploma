import time


def calculate_min_time(objects_cnt, direction):
    base_time = 10
    extra_time_per_object = 1

    total_objects = sum(
        1
        for lane in objects_cnt['detect_time'][direction].values()
        for track_ids in lane.values()
    )
    return base_time + extra_time_per_object * total_objects


def calculate_priority(current_unixtime, objects, priority):
    total_priority = 0
    for obj_class, track_ids in objects.items():
        for track_id, detect_time in track_ids.items():
            wait_time = current_unixtime - detect_time
            wait_time_bonus = (wait_time // 5)
            total_priority += (priority.get(obj_class, 0) + wait_time_bonus)
    return total_priority


def analyze_ojects_stats(objects_in_areas_stats, priority):
    current_unixtime = int(time.time())
    direction_priorities = {
        direction: calculate_priority(current_unixtime, objects, priority)
        for direction, objects in objects_in_areas_stats['detect_time'].items()
    }
    max_priority_direction = max(direction_priorities, key=direction_priorities.get)
    return direction_priorities
