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

