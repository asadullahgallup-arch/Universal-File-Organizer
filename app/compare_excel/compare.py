import os
import pandas as pd


class CompareEngine:

    def __init__(self):
        pass

    def compare(
        self,
        file_a,
        file_b,
        key_column,
        output_folder
    ):

        # Read Excel files
        df_a = pd.read_excel(file_a)
        df_b = pd.read_excel(file_b)

        # Remove blank IDs
        df_a = df_a[df_a[key_column].notna()]
        df_b = df_b[df_b[key_column].notna()]

        # Convert IDs to string
        df_a[key_column] = df_a[key_column].astype(str)
        df_b[key_column] = df_b[key_column].astype(str)

        # Duplicate IDs
        duplicates = df_b[df_b.duplicated(key_column, keep=False)]

        # Sets
        ids_a = set(df_a[key_column])
        ids_b = set(df_b[key_column])

        matched_ids = ids_a.intersection(ids_b)
        missing_ids = ids_a - ids_b
        new_ids = ids_b - ids_a

        matched = df_b[df_b[key_column].isin(matched_ids)]
        missing = df_a[df_a[key_column].isin(missing_ids)]
        new = df_b[df_b[key_column].isin(new_ids)]

        os.makedirs(output_folder, exist_ok=True)

        matched.to_excel(
            os.path.join(output_folder, "Matched.xlsx"),
            index=False
        )

        missing.to_excel(
            os.path.join(output_folder, "Missing.xlsx"),
            index=False
        )

        new.to_excel(
            os.path.join(output_folder, "New.xlsx"),
            index=False
        )

        duplicates.to_excel(
            os.path.join(output_folder, "Duplicates.xlsx"),
            index=False
        )

        summary = pd.DataFrame(
            {
                "Result": [
                    "Matched",
                    "Missing",
                    "New",
                    "Duplicate IDs"
                ],
                "Count": [
                    len(matched),
                    len(missing),
                    len(new),
                    len(duplicates)
                ]
            }
        )

        summary.to_excel(
            os.path.join(output_folder, "Summary.xlsx"),
            index=False
        )

        return {

            "matched": len(matched),

            "missing": len(missing),

            "new": len(new),

            "duplicates": len(duplicates)

        }