from . import models, schemas


class Service:
    def __init__(self, db):
        self.db = db

    def create_member(self, member: schemas.MemberBase):
        db_member = models.Member(**member.dict())
        if not self.member_exists_by_discord_id(member.discord_id):
            self.db.add(db_member)
            self.db.commit()
            return f'<@{member.discord_id}> successfully registered!'
        else:
            return f'<@{member.discord_id}> already registered!'

    def create_server(self, server: schemas.ServerBase):
        db_server = models.Server(**server.dict())
        if not self.server_exists_by_server_id(server.server_id):
            self.db.add(db_server)
            self.db.commit()
            return f'<@{server.server_id}> successfully registered!'
        else:
            return f'<@{server.server_id}> already registered!'

    def get_member_by_discord_id(self, discord_id: str):
        return self.db.query(models.Member).filter(models.Member.discord_id == discord_id).first()

    def get_server_by_server_id(self, server_id: str):
        return self.db.query(models.Server).filter(models.Server.server_id == server_id).first()

    def member_exists_by_discord_id(self, discord_id: str):
        return self.get_member_by_discord_id(discord_id) is not None

    def server_exists_by_server_id(self, server_id: str):
        return self.get_server_by_server_id(server_id) is not None
