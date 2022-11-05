from . import models, schemas
from sqlalchemy.sql import and_, exists
from .constants import StartConfig, TeamSize
import src.elo_calc as calc


class CrudService:
    def __init__(self, db):
        self.db = db

    def create_member(self, member: schemas.Member):
        db_member = models.Member(**member.dict())

        if self.member_exists_by_id(member.id):
            return f'Member: {member.id} already registered'

        self.db.add(db_member)
        self.db.commit()
        return f'Member: {member.id} registered'

    def create_server(self, server: schemas.Server):
        db_server = models.Server(**server.dict())
        if self.server_exists_by_id(server.id):
            return f'Server: {server.id} already registered'

        self.db.add(db_server)
        self.db.commit()
        return f'Server: {server.id} registered'

    def create_member_item(self, member_item: schemas.MemberItem):
        db_member_item = models.MemberItem(**member_item.dict())

        if not self.member_item_exists_by_member_id_and_server_id(db_member_item.member_id, db_member_item.server_id):
            return f'Error: <@{db_member_item.member_id}> already registered!'

        self.db.add(db_member_item)
        self.db.commit()
        return f'<@{db_member_item.member_id}> successfully registered!'

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
        return self.db.query(exists().where(models.Member.id == id)).scalar()

    def server_exists_by_id(self, id: int):
        return self.db.query(exists().where(models.Server.id == id)).scalar()

    def member_item_exists_by_member_id_and_server_id(self, member_id: int, server_id: int):
        return self.db.query(exists().where(and_(models.MemberItem.member_id == member_id,
                                                 models.MemberItem.server_id == server_id))).scalar()

    def adjust_elo(self, winners, losers, server_id):
        winners_avg_elo = self.get_avg_elo(winners, server_id)
        losers_avg_elo = self.get_avg_elo(losers, server_id)

        winners_win_prob = calc.win_probability(avg=winners_avg_elo, opponent_avg=losers_avg_elo)
        losers_win_prob = calc.win_probability(avg=losers_avg_elo, opponent_avg=winners_avg_elo)

        K = 20
        team_size = len(winners)

        elo_change = []

        for winner in winners:
            member = self.get_member_item_by_member_id_and_server_id(winner.id, server_id)
            change = self.adjust(member, K, winners_win_prob, team_size=team_size, win=True)
            elo_change.append(change)

        for loser in losers:
            member = self.get_member_item_by_member_id_and_server_id(loser.id, server_id)
            change = self.adjust(member, K, losers_win_prob, team_size=team_size, win=False)
            elo_change.append(change)

        return [elo_change]

    def adjust(self, member, K, win_prop, team_size, win=True):
        if win:
            member.wins += 1
        else:
            member.losses += 1

        if team_size == TeamSize.TWO_VS_TWO:
            old_elo = member.elo_2v2
            new_elo = calc.new_elo(old_elo, K, win_prop, win=win)
            member.elo_2v2 = new_elo
        else:
            old_elo = member.elo_3v3
            new_elo = calc.new_elo(old_elo, K, win_prop, win=win)
            member.elo_3v3 = new_elo

        self.db.commit()
        return f'{old_elo}>{new_elo}'

    def get_avg_elo(self, team, server_id):
        sum = 0
        team_size = len(team)
        for member in team:
            item = self.get_member_item_by_member_id_and_server_id(member.id, server_id)
            if team_size == TeamSize.TWO_VS_TWO:
                sum += item.elo_2v2
            elif team_size == TeamSize.THREE_VS_THREE:
                sum += item.elo_3v3
        return sum / team_size

    def reset_member_item_by_member_id_and_server_id(self, member_id, server_id):
        member_item = self.get_member_item_by_member_id_and_server_id(member_id, server_id)
        member_item.elo_2v2 = StartConfig.STARTING_ELO
        member_item.elo_3v3 = StartConfig.STARTING_ELO
        member_item.wins = StartConfig.STARTING_WINS
        member_item.losses = StartConfig.STARTING_LOSSES
        self.db.commit()
