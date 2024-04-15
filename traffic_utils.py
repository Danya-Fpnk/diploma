def sum_values_by_key_pattern(data, pattern):
    return sum(value for key, value in data.items() if re.search(pattern, key))
