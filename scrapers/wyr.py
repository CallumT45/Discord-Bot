from selenium import webdriver
from selenium.webdriver.common.keys import Keys
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


def setup():
    webdriver.get(
        'https://randomwordgenerator.com/would-you-rather-question.php')
    sleep(1)

    qinput = webdriver.find_element_by_tag_name("input")
    qinput.clear()
    qinput.send_keys("50")
    return qinput


def loop(qinput, WYR):
    qinput.send_keys(Keys.RETURN)
    sleep(1)
    questions = webdriver.find_elements_by_class_name('support-sentence')
    flag = False
    for question in questions:
        count = WYR.new(question.get_attribute('innerHTML'))
        if count == 0:
            flag = True
    return flag


if __name__ == "__main__":
    WYR = WYRDatabase()
    # WYR.create_db()
    # chromedriver_path = 'C:\\Users\\callu_000\\Desktop\\chromedriver_win32\\chromedriver.exe'
    # webdriver = webdriver.Chrome(executable_path=chromedriver_path)
    # qinput = setup()

    # flag = True
    # while flag:
    #     flag = loop(qinput, WYR)
    #     sleep(1)
    # webdriver.close()

    # WYR.containsOR()
    print(WYR.random())
