import json


class ProfileManager:

    def save_profile(
        self,
        filepath,
        data
    ):

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )


    def load_profile(
        self,
        filepath
    ):

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)