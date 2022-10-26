from . import models, schemas
from .response import Response


class Service:
    def __init__(self, db):
        self.db = db

    def create_member(self, member: schemas.MemberBase):
        db_member = models.Member(**member.dict())
        if not self.member_exists_by_id(member.id):
            self.db.add(db_member)
            self.db.commit()
            return f'User: {member.id} registered'
        else:
            return f'User: {member.id} already registered'

    def create_server(self, server: schemas.ServerBase):
        db_server = models.Server(**server.dict())
        if not self.server_exists_by_id(server.id):
            self.db.add(db_server)
            self.db.commit()
            return f'Server: {server.id} registered'
        else:
            return f'Server: {server.id} already registered'

    def create_member_item(self, member_item: schemas.MemberItemBase):
        db_member_item = models.MemberItem(**member_item.dict())
        if self.can_register(db_member_item.member_id, db_member_item.server_id):
            self.db.add(db_member_item)
            self.db.commit()
            return f'<@{db_member_item.member_id}> successfully registered!'
        else:
            return f'<@{db_member_item.member_id}> already registered!'

    def get_member_by_id(self, id: int):
        return self.db.query(models.Member).filter(models.Member.id == id).first()

    def get_server_by_id(self, id: int):
        return self.db.query(models.Server).filter(models.Server.id == id).first()

    def get_member_item_by_member_id_and_server_id(self, member_id: int, server_id: int):
        return self.db.query(models.MemberItem).filter(
            models.MemberItem.member_id == member_id and models.MemberItem.server_id == server_id).first()

    def can_register(self, member_id, server_id):
        member = self.db.query(models.MemberItem).filter(models.MemberItem.member_id == member_id).first()
        server = self.get_server_by_id(server_id)
        return (member is None) and server is not None

    def member_exists_by_id(self, id: int):
        return self.get_member_by_id(id) is not None

    def server_exists_by_id(self, id: int):
        return self.get_server_by_id(id) is not None

    def member_item_exists_by_member_id_and_server_id(self, member_id: int, server_id: int):
        return self.get_member_item_by_member_id_and_server_id(member_id, server_id)

    def get_member_item_info(self, member_id: int, server_id):
        if self.member_item_exists_by_member_id_and_server_id(member_id, server_id):
            return self.get_member_item_by_member_id_and_server_id(member_id, server_id)
        else:
            return None
