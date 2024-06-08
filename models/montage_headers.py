from models.sql.montage_headers import MontageHeadersModelSQL


class MontageHeadersModel:

    def __init__(self):
        self.fields = MontageHeadersModelSQL.setup_db()