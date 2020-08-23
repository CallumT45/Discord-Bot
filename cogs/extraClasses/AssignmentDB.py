import sqlalchemy as db
from sqlalchemy import Column, Integer, String, Date, MetaData, Table, and_, func
from datetime import datetime, date, timedelta


class AssignmentDatabase():

    def __init__(self):
        self.engine = db.create_engine('sqlite:///database/assignments.sqlite')
        self.connection = self.engine.connect()
        self.metadata = db.MetaData()

    def due(self, guild_id):
        assignments = db.Table('assignments', self.metadata,
                               autoload=True, autoload_with=self.engine)
        query = db.select([assignments]).where(
            assignments.columns.guild_id == guild_id)
        ResultProxy = self.connection.execute(query)
        return ResultProxy.fetchall()

    def new(self, due_date, assignment_details, guild_id, channel_id):
        if not self.if_exists(assignment_details, guild_id):
            table = db.Table('assignments', self.metadata,
                             autoload=True, autoload_with=self.engine)

            ins = table.insert().values(
                due_date=datetime.strptime(due_date, '%d/%m/%Y'),
                assignment_details=assignment_details,
                guild_id=guild_id,
                channel_id=channel_id)
            self.connection.execute(ins)
            return "OK"
        else:
            return "Already in DB"

    def remove(self, assignment_details, guild_id):
        assignments = db.Table('assignments', self.metadata,
                               autoload=True, autoload_with=self.engine)

        del_st = assignments.delete().where(and_(assignments.columns.assignment_details ==
                                                 assignment_details, assignments.columns.guild_id == guild_id))
        self.connection.execute(del_st)

    def past_due(self, guild_id):
        """[Removes all rows where the due date is in the past]

        Args:
            guild_id ([int]): [server identifier]
        """
        assignments = db.Table('assignments', self.metadata,
                               autoload=True, autoload_with=self.engine)

        del_st = assignments.delete().where(and_(assignments.columns.due_date <
                                                 date.today(), assignments.columns.guild_id == guild_id))
        self.connection.execute(del_st)

    def create_db(self):
        assignments = Table('assignments', self.metadata,
                            Column('due_date', Date),
                            Column('assignment_details', String(
                                100), primary_key=True),
                            Column('guild_id', Integer, primary_key=True),
                            Column('channel_id', Integer),
                            )
        assignments.create(self.engine)

    def check_due(self):
        """[Returns any assignments due in the next day for the given server]

        Args:
            guild_id ([int]): [Server ID]

        Returns:
            [list]:
        """
        tomorrow = date.today()+timedelta(days=1)
        day_after = date.today()+timedelta(days=2)

        assignments = db.Table('assignments', self.metadata,
                               autoload=True, autoload_with=self.engine)
        query = db.select([assignments]).where(and_(assignments.columns.due_date >= tomorrow,
                                                    assignments.columns.due_date < day_after))
        ResultProxy = self.connection.execute(query)
        return ResultProxy.fetchall()

    def if_exists(self, assignment_details, guild_id):
        """[Checks if assignment already exists]

        Args:
            assignment_details ([String]): [String to be matched]
            guild_id ([int]): [int to limit to specific server]

        Returns:
            [boolean]: [True if value exists]
        """
        assignments = db.Table('assignments', self.metadata,
                               autoload=True, autoload_with=self.engine)
        query = db.select([assignments]).where(and_(assignments.columns.assignment_details ==
                                                    assignment_details, assignments.columns.guild_id == guild_id))
        ResultProxy = self.connection.execute(query)
        if ResultProxy.fetchall():
            return True
        else:
            return False


if __name__ == "__main__":
    adb = AssignmentDatabase()
    adb.create_db()
    # adb.new("23/08/2020", "Test4", 693142919921664080)
    # adb.new("23/08/2020", "Test32", 6)
    # adb.new("1/08/2020", "Test4", 6)
    # adb.check_due(6)
    # adb.remove("Test4", 6)
    # adb.past_due(6)
    # print(adb.due(693142919921664080))
