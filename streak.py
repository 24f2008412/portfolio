def longest_positive_streak(nums: list[int]) -> int:
    """
    Calculates the length of the longest consecutive run of positive numbers.

    Args:
        nums: A list of integers.

    Returns:
        The length of the longest positive streak.
    """
    max_streak = 0
    current_streak = 0
    for num in nums:
        if num > 0:
            current_streak += 1
            if current_streak > max_streak:
                max_streak = current_streak
        else:
            current_streak = 0
    return max_streak

# retrigger workflow
