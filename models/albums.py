from PySide6.QtGui import QStandardItem

class AlbumsModel():
    albums_tree = {
        "By events": {
            "Wedding": {},
            "Birthday": {},
        },
        "By filming date": {
            "2024": {
                "April 1": {},
                "June 9": {},
            },
            "2023": {
                "April 10": {},
                "June 19": {},
            },
        },
        "By import date": {
            "2024": {
                "January 1": {},
                "February 9": {},
            },
            "2023": {
                "March 10": {},
                "April 19": {},
            },
        }
    }

    def fill_model_from_dict(parent, d):
        if isinstance(d, dict):
            for key, value in d.items():
                it = QStandardItem(str(key))
                if isinstance(value, dict):
                    parent.appendRow(it)
                    AlbumsModel.fill_model_from_dict(it, value)
                else:
                    it2 = QStandardItem(str(value))
                    parent.appendRow([it, it2])