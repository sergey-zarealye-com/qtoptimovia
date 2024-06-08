from models.sql.montage_materials import MontageMaterialsModelSQL


class MontageMaterialsModel:

    def __init__(self):
        self.fields = MontageMaterialsModelSQL.setup_db()