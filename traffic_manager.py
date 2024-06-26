from datetime import datetime, timedelta
from traffic_analyzer import analyze_ojects_stats, calculate_min_time


def manage_traffic_light(objects_in_areas_stats, env):
    direction_priorities = analyze_ojects_stats(objects_in_areas_stats, env.priority)
    max_priority_direction = max(direction_priorities, key=direction_priorities.get)
    current_time = datetime.now()
    elapsed_time_since_last_change = current_time - env.traffic_light.last_status_changed_at

    if (elapsed_time_since_last_change > timedelta(seconds=env.min_change_time)
            and env.traffic_light.priority_direction != max_priority_direction):
        env.min_change_time = calculate_min_time(objects_in_areas_stats, max_priority_direction)
        env.traffic_light.change_colors(max_priority_direction, application=env)

    if elapsed_time_since_last_change < timedelta(seconds=env.min_change_time):
        time_to_access_changing_traffic_signal = timedelta(seconds=env.min_change_time) - elapsed_time_since_last_change
    else:
        time_to_access_changing_traffic_signal = timedelta(seconds=0)

    return direction_priorities, time_to_access_changing_traffic_signal
