from time import sleep
import requests
import bs4
import datetime
import html
import re

import sqlalchemy as db
from sqlalchemy import Column, Integer, String, Date, MetaData, Table, and_, func, not_


class WYRDatabase():

    def __init__(self):
        self.engine = db.create_engine('sqlite:///wyr.sqlite')
        self.connection = self.engine.connect()
        self.metadata = db.MetaData()

    def new(self, question):
        if not self.if_exists(question):
            table = db.Table('wyr', self.metadata,
                             autoload=True, autoload_with=self.engine)

            ins = table.insert().values(
                questions=question)
            self.connection.execute(ins)
            print(question)
            return 0
        else:
            print("Already in DB")
            return 1

    def remove(self, question):
        wyr = db.Table('wyr', self.metadata,
                       autoload=True, autoload_with=self.engine)

        del_st = wyr.delete().where(wyr.columns.questions == question)
        self.connection.execute(del_st)

    def create_db(self):
        wyr = Table('wyr', self.metadata,
                    Column('questions', String)
                    )
        wyr.create(self.engine)

    def random(self):
        wyr = db.Table('wyr', self.metadata,
                       autoload=True, autoload_with=self.engine)
        query = db.select([wyr]).order_by(func.RANDOM()).limit(1)
        ResultProxy = self.connection.execute(query)
        return ResultProxy.fetchall()[0][0]

    def if_exists(self, question):
        wyr = db.Table('wyr', self.metadata,
                       autoload=True, autoload_with=self.engine)
        query = db.select([wyr]).where(
            wyr.columns.questions == question)
        ResultProxy = self.connection.execute(query)
        if ResultProxy.fetchall():
            return True
        else:
            return False

    def containsOR(self):
        """Removes all wyr's without or"""
        wyr = db.Table('wyr', self.metadata,
                       autoload=True, autoload_with=self.engine)
        del_st = wyr.delete().where(not_(wyr.columns.questions.contains(" or ")))
        self.connection.execute(del_st)

    def count(self):
        wyr = db.Table('wyr', self.metadata,
                       autoload=True, autoload_with=self.engine)
        query = db.select([wyr])
        ResultProxy = self.connection.execute(query)
        return len(ResultProxy.fetchall())

    def doubleWYR(self):
        """Removes all wyr's without or"""
        wyr = db.Table('wyr', self.metadata,
                       autoload=True, autoload_with=self.engine)
        query = db.select([wyr]).where(
            (wyr.columns.questions.ilike('%Would you rather%Would you rather%')))
        ResultProxy = self.connection.execute(query)
        return ResultProxy.fetchall()
        # del_st = wyr.delete().where((wyr.columns.questions.ilike('%Would you rather%')))
        # self.connection.execute(del_st)


def getQuestion(page):
    response = requests.get("http://either.io/" + str(page))
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    preface = soup.findAll("h3", {"class": "preface"})
    options = soup.findAll("div", {"class": "option"})
    option1 = ""
    option2 = ""
    for option in options:
        tag = option.findAll("a")
        if tag:
            if not option1:
                option1 = tag[0].contents[0].replace("\n", "")
            elif not option2:
                option2 = tag[0].contents[0].replace("\n", "")

    return preface[0].contents[0] + option1 + "or " + option2


def main(WYR):
    for page in range(2000, 30000):
        try:
            WYR.new(getQuestion(page))
            sleep(0.5)
        except:
            pass


def clean(question):
    new_question = question.replace("would you rather...", "", 1)
    if new_question[0] == ",":
        new_question = new_question.replace(", ", "", 1)
    return new_question


if __name__ == "__main__":
    WYR = WYRDatabase()
    # main(WYR)
    print(WYR.count())

    # removing rows with two would you rathers in the string
    # for row in WYR.doubleWYR():
    #     new_question = clean(row[0])
    #     WYR.new(new_question)
    #     WYR.remove(row[0])
