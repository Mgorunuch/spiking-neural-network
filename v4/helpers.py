import math


def distance(p1, p2):
    return math.sqrt(
        (p1[0] - p2[0])**2 +
        (p1[1] - p2[1])**2 +
        (p1[2] - p2[2])**2
    )


def multiplier_increment(p1, p2, nm):
    return (
        (p2[0] - p1[0]) / nm,
        (p2[1] - p1[1]) / nm,
        (p2[2] - p1[2]) / nm,
    )
