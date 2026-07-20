class FileMatcher:

    def __init__(self, file_index):
        self.file_index = file_index

    def find_files(self, value, mode):

        if value is None:
            return []

        value = str(value).strip().casefold()

        if value == "":
            return []

        matches = []

        # -----------------------
        # Exact Match
        # -----------------------

        if mode == "Exact Match":

            if value in self.file_index:

                matches.extend(
                    self.file_index[value]
                )

        # -----------------------
        # Starts With
        # -----------------------

        elif mode == "Starts With":

            for key, files in self.file_index.items():

                if key.startswith(value):

                    matches.extend(files)

        # -----------------------
        # Contains
        # -----------------------

        elif mode == "Contains":

            for key, files in self.file_index.items():

                if value in key:

                    matches.extend(files)

        return matches
