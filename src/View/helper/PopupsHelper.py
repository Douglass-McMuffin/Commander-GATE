from src.Control.ControlAPI import ControlAPI

class PopupsHelper():

    @staticmethod
    def uniqueName(name: str, existingNames: list[str]):
        # ensure unique name (foo, foo_2, foo_3, …)
        base = name
        i = 2
        while name in existingNames:
            name = f"{base}_{i}"
            i += 1

        return name