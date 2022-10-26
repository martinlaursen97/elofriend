from . import models, schemas
from sqlalchemy import and_


class Service:
    def __init__(self, db):
        self.db = db

    def create_member(self, member: schemas.MemberBase):
        db_member = models.Member(**member.dict())
        if not self.member_exists_by_id(member.id):
            self.db.add(db_member)
            self.db.commit()
            return f'Member: {member.id} registered'
        else:
            return f'Member: {member.id} already registered'

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
        print(db_member_item.member_id)
        print(db_member_item.server_id)

        if not self.member_item_exists_by_member_id_and_server_id(db_member_item.member_id, db_member_item.server_id):

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
        return self.db.query(models.MemberItem).filter(and_(models.MemberItem.member_id == member_id,
                                                            models.MemberItem.server_id == server_id)).first()

    def member_exists_by_id(self, id: int):
        return self.get_member_by_id(id) is not None

    def server_exists_by_id(self, id: int):
        return self.get_server_by_id(id) is not None

    def member_item_exists_by_member_id_and_server_id(self, member_id: int, server_id: int):
        print(self.get_member_item_by_member_id_and_server_id(member_id, server_id))
        return self.get_member_item_by_member_id_and_server_id(member_id, server_id) is not None

    def get_member_item_info(self, member_id: int, server_id):
        if self.member_item_exists_by_member_id_and_server_id(member_id, server_id):
            return self.get_member_item_by_member_id_and_server_id(member_id, server_id)
        else:
            return None
