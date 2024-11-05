class DevCards:
    def __init__(
        self,
        id,
        activity_at_nine,
        activity_at_ten,
        activity_at_eleven,
        item,
        attack_points,
    ):
        self.id = id
        self.activity_at_nine = activity_at_nine
        self.activity_at_ten = activity_at_ten
        self.activity_at_eleven = activity_at_eleven
        self.item = item
        self.attack_points = attack_points

    def get_id(self):
        return self.id

    def get_activity_at_nine(self):
        return self.activity_at_nine

    def get_activity_at_ten(self):
        return self.activity_at_ten

    def get_activity_at_eleven(self):
        return self.activity_at_eleven

    def get_item(self):
        return self.item

    def get_attack_points(self):
        return self.attack_points

    def to_string(self):
        return (
            f"Card ID: {self.id}, 9:00: {self.activity_at_nine}, "
            f"10:00: {self.activity_at_ten}, "
            f"11:00: {self.activity_at_eleven}, "
            f"Item: {self.item}")
