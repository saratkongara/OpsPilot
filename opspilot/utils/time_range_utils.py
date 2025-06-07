from typing import List, Tuple

class TimeRangeUtils:
    @staticmethod
    def to_minute_ranges(start_str: str, end_str: str) -> List[Tuple[int, int]]:
        def time_to_min(t: str) -> int:
            h, m = map(int, t.split(":"))
            return h * 60 + m

        start = time_to_min(start_str)
        end = time_to_min(end_str)

        if end <= start:
            return [(start, 1440), (0, end)]
        else:
            return [(start, end)]

    @staticmethod
    def to_minute_ranges_from_minutes(start: int, end: int) -> List[Tuple[int, int]]:
        """
        Converts minute values (0–1439) into a list of ranges.
        Supports ranges that span midnight.
        """
        if end <= start:
            return [(start, 1440), (0, end)]
        else:
            return [(start, end)]

    @staticmethod
    def has_overlap(ranges1: List[Tuple[int, int]], ranges2: List[Tuple[int, int]]) -> bool:
        for s1, e1 in ranges1:
            for s2, e2 in ranges2:
                if max(s1, s2) < min(e1, e2):
                    return True
                
        return False

    @staticmethod
    def are_fully_covered(target_ranges: List[Tuple[int, int]], cover_ranges: List[Tuple[int, int]]) -> bool:
        """
        Returns True if every interval in `target_ranges` is fully covered by at least one interval in `cover_ranges`.
        """
        for t_start, t_end in target_ranges:
            if not any(c_start <= t_start and c_end >= t_end for c_start, c_end in cover_ranges):
                return False
            
        return True
    
    @staticmethod
    def is_fully_covered(coverage_ranges: List[Tuple[int, int]], target_range: Tuple[int, int]) -> bool:
        """
        Check if any of the coverage ranges fully contains the target range.
        """
        t_start, t_end = target_range
        for c_start, c_end in coverage_ranges:
            if c_start <= t_start and c_end >= t_end:
                return True
            
        return False

    @staticmethod
    def has_available_time(all_shift_intervals: List[Tuple[int, int]], assigned_intervals: List[Tuple[int, int]]) -> bool:
        """
        Checks if there is any available time in the shift intervals after accounting for assigned intervals.

        Args:
            all_shift_intervals: List of tuples representing the start and end minutes of shift intervals.
            assigned_intervals: List of tuples representing the start and end minutes of assigned intervals.

        Returns:
            bool: True if there is available time, False otherwise.

        Implementation:
        - Merges all assigned intervals into a single list.The has_available_time method determines if there is any unoccupied time in the shift intervals after accounting for assigned intervals. Here's the step-by-step logic with an example:

        Logic:
        1. Merge Assigned Intervals:

        - Combine all assigned intervals into a single list.
        - Sort the intervals by their start times.
        - Merge overlapping or adjacent intervals into a single interval.
        
        2. Check for Gaps in Shift Intervals:

        - Iterate through each shift interval.
        - For each shift interval, check if there is a gap between the current position in the shift and the start of the next assigned interval.
        - If a gap is found, return True (indicating available time).
        - If no gaps are found, check if there is remaining time at the end of the shift interval.
        
        3. Return Result:

        If no available time is found in any shift interval, return False.
        
        Example:
        
        Input:
        Shift Intervals: [(0, 480), (540, 1020)]
        (Two shifts: Midnight to 8:00 AM, and 9:00 AM to 5:00 PM)
        
        Assigned Intervals: [(60, 120), (300, 360), (600, 660)]
        (Assigned tasks: 1:00 AM to 2:00 AM, 5:00 AM to 6:00 AM, and 10:00 AM to 11:00 AM)
        
        Step-by-Step Execution:
        Merge Assigned Intervals:

        Input: [(60, 120), (300, 360), (600, 660)]
        Sorted: [(60, 120), (300, 360), (600, 660)]
        Merged: [(60, 120), (300, 360), (600, 660)]
        (No overlapping intervals to merge)
        
        Check for Gaps in Shift Intervals:

        First Shift (0, 480):
        Current position: 0
        Gap between 0 and 60 → Available time found.
        Return True.
        
        Output:
        
        Result: True (There is available time in the shifts).
        
        Key Points:
        - The method efficiently merges assigned intervals to simplify the comparison.
        - It checks for gaps between the current position in the shift and the next assigned interval.
        - If any gap is found, it immediately returns True, ensuring optimal performance.
        
        Another Example:
        Input:
        Shift Intervals: [(0, 720)]
        (One shift: Midnight to 12:00 PM)

        Assigned Intervals: [(0, 120), (300, 360)]
        (Assigned tasks: Midnight to 2:00 AM, and 5:00 AM to 6:00 AM)

        Step-by-Step Execution:

        Merge Assigned Intervals:

        Input: [(0, 120), (300, 360)]
        Sorted: [(0, 120), (300, 360)]
        No overlapping intervals to merge.
        Merged Assigned Intervals: [(0, 120), (300, 360)]

        Check for Gaps in Shift Intervals:

        Shift Interval (0, 720):
        Current position: 0
        No gap between 0 and 120 (time is occupied).
        Move to the end of the first assigned interval: 120
        Gap between 120 and 300 → Available time found.
        Return True.
        """
        # Merge all assigned intervals into a single list
        merged_assigned = []
        for start, end in assigned_intervals:
            merged_assigned.append((start, end))

        # Sort and merge overlapping assigned intervals
        merged_assigned.sort()
        merged_intervals = []
        for start, end in merged_assigned:
            if not merged_intervals or merged_intervals[-1][1] < start:
                merged_intervals.append((start, end))
            else:
                merged_intervals[-1] = (merged_intervals[-1][0], max(merged_intervals[-1][1], end))

        # Check for gaps in the shift intervals
        for shift_start, shift_end in all_shift_intervals:
            current_start = shift_start
            for assigned_start, assigned_end in merged_intervals:
                if assigned_start > current_start:
                    return True  # Found available time
                current_start = max(current_start, assigned_end)

            if current_start < shift_end:
                return True  # Remaining time in the shift is available

        return False

