class Helpers:
    @staticmethod
    def attach_to_object_by_key(array, value, key="", offset=0):
        keys = key.split(".")

        if keys[offset] not in array:
            array[keys[offset]] = {}

        if len(keys) > offset + 1:
            Helpers.attach_to_object_by_key(array[keys[offset]], value, key, offset + 1)
            return

        array[keys[offset]] = value
