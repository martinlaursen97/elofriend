from . import models, schemas


class Service:
    def __init__(self, db):
        self.db = db

    def get_member_by_discord_id(self, discord_id: str):
        return self.db.query(models.Member).filter(models.Member.discord_id == discord_id).first()

    def member_exists_by_discord_id(self, discord_id: str):
        return self.get_member_by_discord_id(discord_id) is not None

    def create_member(self, member: schemas.MemberBase):
        db_member = models.Member(**member.dict())
        if not self.member_exists_by_discord_id(member.discord_id):
            self.db.add(db_member)
            self.db.commit()
            return f'<@{member.discord_id}> successfully registered!'
        else:
            return f'<@{member.discord_id}> already registered!'
