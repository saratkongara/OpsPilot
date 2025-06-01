from datetime import datetime

class ParserUtil:
    @staticmethod
    def extract_time(dt_str: str) -> str:
        """
        Extracts time from a string in the format '2025-05-23T05:15:00' and returns a str in 'HH:MM' format like '05:15'.
        """
        # Parse the string into a datetime object
        dt = datetime.fromisoformat(dt_str)

        # Get time part as HH:MM
        return dt.strftime('%H:%M')