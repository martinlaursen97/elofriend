from . import models, schemas
from sqlalchemy.sql import and_, exists
from .constants import StartConfig, GameType
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

        if self.member_item_exists_by_member_id_and_server_id(db_member_item.member_id, db_member_item.server_id):
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

    def adjust_elo(self, winners, losers, game_type, server_id):
        winners_avg_elo = self.get_avg_elo(winners, server_id, game_type)
        losers_avg_elo = self.get_avg_elo(losers, server_id, game_type)

        winners_win_prob = calc.win_probability(avg=winners_avg_elo, opponent_avg=losers_avg_elo)
        losers_win_prob = calc.win_probability(avg=losers_avg_elo, opponent_avg=winners_avg_elo)

        K = 20

        elo_change = []

        for winner in winners:
            member = self.get_member_item_by_member_id_and_server_id(winner.id, server_id)
            change = self.adjust(member, K, winners_win_prob, game_type=game_type, win=True)
            elo_change.append(change)

        for loser in losers:
            member = self.get_member_item_by_member_id_and_server_id(loser.id, server_id)
            change = self.adjust(member, K, losers_win_prob, game_type=game_type, win=False)
            elo_change.append(change)

        return [elo_change]

    def adjust(self, member, K, win_prop, game_type, win=True):
        if game_type == GameType.ONE_VS_ONE:
            if win:
                member.wins_1v1 += 1
            else:
                member.losses_1v1 += 1

            old_elo = member.elo_1v1
            new_elo = calc.new_elo(old_elo, K, win_prop, win=win)
            member.elo_1v1 = new_elo
        elif game_type == GameType.TWO_VS_TWO:
            if win:
                member.wins_2v2 += 1
            else:
                member.losses_2v2 += 1

            old_elo = member.elo_2v2
            new_elo = calc.new_elo(old_elo, K, win_prop, win=win)
            member.elo_2v2 = new_elo
        else:
            if win:
                member.wins_3v3 += 1
            else:
                member.losses_3v3 += 1

            old_elo = member.elo_3v3
            new_elo = calc.new_elo(old_elo, K, win_prop, win=win)
            member.elo_3v3 = new_elo

        self.db.commit()
        return f'{old_elo}>{new_elo}'

    def get_avg_elo(self, team, server_id, game_type):
        elo_sum = 0
        for member in team:
            item = self.get_member_item_by_member_id_and_server_id(member.id, server_id)
            if game_type == GameType.ONE_VS_ONE:
                elo_sum += item.elo_1v1
            elif game_type == GameType.TWO_VS_TWO:
                elo_sum += item.elo_2v2
            else:
                elo_sum += item.elo_3v3
        return elo_sum / len(team)

    def reset_member_item_by_member_id_and_server_id(self, member_id, server_id):
        member_item = self.get_member_item_by_member_id_and_server_id(member_id, server_id)
        member_item.elo_1v1 = StartConfig.STARTING_ELO
        member_item.elo_2v2 = StartConfig.STARTING_ELO
        member_item.elo_3v3 = StartConfig.STARTING_ELO
        member_item.wins_1v1 = StartConfig.STARTING_WINS
        member_item.wins_2v2 = StartConfig.STARTING_WINS
        member_item.wins_3v3 = StartConfig.STARTING_WINS
        member_item.losses_1v1 = StartConfig.STARTING_LOSSES
        member_item.losses_2v2 = StartConfig.STARTING_LOSSES
        member_item.losses_3v3 = StartConfig.STARTING_LOSSES
        self.db.commit()
