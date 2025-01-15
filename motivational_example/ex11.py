def merge_intervals(intervals):
    
    if not intervals:
        return []

    # 1) Sort intervals by start time
    intervals.sort(key=lambda x: x[0])

    merged = [intervals[0]]

    for i in range(1, len(intervals)):
        current_start, current_end = intervals[i]
        last_start, last_end = merged[-1]

        # BUG: We used '>' instead of '>='
        # This code fails to merge intervals that share endpoints.
        if current_start > last_end:
            # No overlap or boundary contact => append as new interval
            merged.append(intervals[i])
        else:
            # Overlapping or adjacent intervals => merge them
            # (But because we used '>', intervals that only 'touch'
            # won't merge here, which is a bug given the requirement.)
            merged[-1][1] = max(last_end, current_end)

    return merged