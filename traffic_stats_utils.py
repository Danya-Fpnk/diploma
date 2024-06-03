from copy import deepcopy


def reset_objects_in_areas_stats():
    return {
        'detect_time': {}
    }


def merge_stats(objects_in_areas_stats, new_stats, model_name):
    objects_in_areas_stats_copy = deepcopy(objects_in_areas_stats)
    for area_key in new_stats['detect_time']:
        if area_key not in objects_in_areas_stats_copy['detect_time']:
            objects_in_areas_stats_copy['detect_time'][area_key] = {}
        for obj_class in new_stats['detect_time'][area_key].keys():
            if obj_class not in objects_in_areas_stats_copy['detect_time'][area_key]:
                objects_in_areas_stats_copy['detect_time'][area_key][obj_class] = {}
            for track_id, detect_time in new_stats['detect_time'][area_key][obj_class].items():
                objects_in_areas_stats_copy['detect_time'][area_key][obj_class][
                    f'{model_name}_{track_id}'] = detect_time

    return objects_in_areas_stats_copy
