import v4.helpers as hlp
import math


class Neurogenesis:
    @staticmethod
    def get_connection_points(
            from_location,
            to_location,
            connection_generation_frequency,
    ):
        connection_generation_frequency += 1

        from_caret = (from_location.x, from_location.y, from_location.z)
        to_caret = (to_location.x, to_location.y, to_location.z)

        mult_increment = hlp.multiplier_increment(
            from_caret,
            to_caret,
            connection_generation_frequency,
        )

        arr = []
        for i in range(1, connection_generation_frequency):
            arr.append(
                (
                    math.ceil(from_location.x * (mult_increment[0] * i)),
                    math.ceil(from_location.y * (mult_increment[1] * i)),
                    math.ceil(from_location.z * (mult_increment[2] * i)),
                )
            )

        return arr


class Location:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


print(
    Neurogenesis.get_connection_points(
        Location(1, 1, 1),
        Location(11, 31, 47),
        5,
    )
)