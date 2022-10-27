from . import models, schemas
from sqlalchemy import and_
from .constants import StartConfig
import src.elo_calc as calc


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

        if not self.member_item_exists_by_member_id_and_server_id(db_member_item.member_id, db_member_item.server_id):
            self.db.add(db_member_item)
            self.db.commit()
            return f'<@{db_member_item.member_id}> successfully registered!'
        else:
            return f'Error: <@{db_member_item.member_id}> already registered!'

    def get_member_by_id(self, id: int):
        return self.db.query(models.Member).filter(models.Member.id == id).first()

    def get_server_by_id(self, id: int):
        return self.db.query(models.Server).filter(models.Server.id == id).first()

    def get_member_item_by_member_id_and_server_id(self, member_id: int, server_id: int):
        return self.db.query(models.MemberItem).filter(and_(models.MemberItem.member_id == member_id,
                                                            models.MemberItem.server_id == server_id)).first()

    def get_member_items_by_server_id(self, server_id: int):
        return self.db.query(models.MemberItem).filter(models.MemberItem.server_id == server_id).all()

    def member_exists_by_id(self, id: int):
        return self.get_member_by_id(id) is not None

    def server_exists_by_id(self, id: int):
        return self.get_server_by_id(id) is not None

    def member_item_exists_by_member_id_and_server_id(self, member_id: int, server_id: int):
        return self.get_member_item_by_member_id_and_server_id(member_id, server_id) is not None

    def get_member_item_info(self, member_id: int, server_id):
        if self.member_item_exists_by_member_id_and_server_id(member_id, server_id):
            return self.get_member_item_by_member_id_and_server_id(member_id, server_id)
        else:
            return None

    def adjust_elo(self, winners, losers, server_id):
        winners_avg_elo = self.get_avg_elo(winners, server_id)
        losers_avg_elo = self.get_avg_elo(losers, server_id)

        winners_win_prop = calc.win_prop(avg=winners_avg_elo, opponent_avg=losers_avg_elo)
        losers_win_prop = calc.win_prop(avg=losers_avg_elo, opponent_avg=winners_avg_elo)

        K = 20

        elo_change = []

        for w in winners:
            member = self.get_member_item_by_member_id_and_server_id(w.id, server_id)
            change = self.adjust(member, K, winners_win_prop, win=True)
            elo_change.append(change)

        for l in losers:
            member = self.get_member_item_by_member_id_and_server_id(l.id, server_id)
            change = self.adjust(member, K, losers_win_prop, win=False)
            elo_change.append(change)

        return [elo_change]

    def adjust(self, member, K, win_prop, win=True):
        old_elo = member.elo_2v2
        new_elo = calc.new_elo(old_elo, K, win_prop, win=win)
        member.elo_2v2 = new_elo
        member.wins += 1

        self.db.commit()
        return f'{old_elo}>{new_elo}'

    def get_avg_elo(self, team, server_id):
        sum = 0
        for i in team:
            item = self.get_member_item_by_member_id_and_server_id(i.id, server_id)
            if len(team) == 2:
                sum += item.elo_2v2
            elif len(team) == 3:
                sum += item.elo_3v3
        return sum / len(team)

    def reset_elo_by_member_id_and_server_id(self, member_id, server_id):
        member_item = self.get_member_item_by_member_id_and_server_id(member_id, server_id)
        member_item.elo_2v2 = StartConfig.STARTING_ELO
        member_item.elo_3v3 = StartConfig.STARTING_ELO
        member_item.wins = StartConfig.STARTING_WINS
        member_item.losses = StartConfig.STARTING_LOSSES
        self.db.commit()
