import sqlite3 as lite
import csv
import re
import pandas as pd
import argparse
import collections
import json
import glob
import math
import os
import requests
import string
import sqlite3
import sys
import time
import xml


class Movie_db(object):
    def __init__(self, db_name):
        #db_name: "cs1656-public.db"
        self.con = lite.connect(db_name)
        self.cur = self.con.cursor()
    
    #q0 is an example 
    def q0(self):
        query = '''SELECT COUNT(*) FROM Actors'''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q1(self):
        query = '''
            SELECT a.fname, a.lname
            FROM Actors a
            JOIN Cast c ON a.aid = c.aid
            JOIN Movies m ON c.mid = m.mid
            GROUP BY a.aid, a.fname, a.lname
            HAVING SUM(CASE WHEN m.year BETWEEN 1980 AND 1990 THEN 1 ELSE 0 END) > 0
            AND SUM(CASE WHEN m.year >= 2000 THEN 1 ELSE 0 END) > 0
            ORDER BY a.lname, a.fname;
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows
        

    def q2(self):
        query = '''
            SELECT m.title, m.year
            FROM Movies m
            WHERE m.year = (Select year From Movies Where title = "Rogue One: A Star Wars Story")
            AND m.rank > (Select rank From Movies Where title = "Rogue One: A Star Wars Story")
            ORDER BY m.title
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q3(self):
        query = '''
            SELECT a.fname, a.lname, COUNT(DISTINCT m.mid) as numMovies
            FROM Actors as a
            JOIN Cast c ON a.aid = c.aid
            JOIN Movies m ON c.mid = m.mid
            WHERE title LIKE '%Star Wars%'
            GROUP BY a.fname, a.lname, a.aid
            ORDER BY numMovies DESC, a.lname, a.fname
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows


    def q4(self):
        query = '''
            SELECT a.fname, a.lname
            FROM Actors as a
            JOIN Cast c ON c.aid = a.aid
            JOIN Movies m ON m.mid = c.mid
            GROUP BY a.fname, a.lname
            HAVING MAX(m.year) < 1990
            ORDER BY a.lname, a.fname

        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q5(self):
        query = '''
            SELECT d.fname, d.lname, COUNT(md.mid) as count
            FROM Directors d
            JOIN Movie_Director md ON d.did = md.did
            GROUP BY d.fname, d.lname, d.did
            ORDER BY count DESC, d.lname, d.fname
            LIMIT 10
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q6(self):
        query = '''
            SELECT m.title, COUNT(c.aid) as count
            FROM Movies as m
            JOIN Cast c ON m.mid = c.mid
            GROUP BY m.title
            ORDER BY count DESC
            LIMIT 10
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q7(self):
        query = '''
            SELECT m.title,
                (SELECT COUNT(*) FROM Actors a JOIN Cast c ON a.aid = c.aid WHERE c.mid = m.mid AND a.gender = 'Male') AS countM,
                (SELECT COUNT(*) FROM Actors a JOIN Cast c ON a.aid = c.aid WHERE c.mid = m.mid AND a.gender = 'Female') AS countF
            FROM Movies as m
            JOIN Cast c ON m.mid = c.mid
            JOIN Actors a ON c.aid = a.aid
            GROUP BY m.title
            HAVING countM > countF
            ORDER BY m.title 
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q8(self):
        query = '''
            SELECT a.fname, a.lname, COUNT(DISTINCT md.did) AS count
            FROM Actors as a
            JOIN Cast c ON a.aid = c.aid
            JOIN Movie_Director md ON c.mid = md.mid
            JOIN Directors d ON md.did = d.did
            GROUP BY a.fname, a.lname
            HAVING count > 7
   
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows


    def q9(self):
        query = '''
            SELECT a.fname, a.lname, COUNT(m.mid) as count
            FROM Actors as a
            JOIN Cast c ON a.aid = c.aid
            JOIN Movies m ON c.mid = m.mid
            WHERE a.fname LIKE 'B%' AND
            m.year = (SELECT MIN(m1.year) FROM Movies as m1 JOIN Cast c1 ON m1.mid = c1.mid WHERE c1.aid = a.aid)
            GROUP BY a.fname, a.lname
            ORDER BY count DESC, a.fname, a.lname
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q10(self):
        query = '''
            SELECT a.lname, m.title
            FROM Actors as a
            JOIN Cast as c ON a.aid = c.aid
            JOIN Movie_Director as md ON c.mid = md.mid
            JOIN Directors as d ON md.did = d.did
            JOIN Movies as m ON md.mid = m.mid
            WHERE a.lname = d.lname
            AND a.fname != d.fname
            GROUP BY a.lname, m.title
            ORDER BY a.lname, m.title
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q11(self):
        query = '''
            SELECT DISTINCT a2.fname, a2.lname
            FROM Actors a1
            JOIN Cast c1 ON a1.aid = c1.aid
            JOIN Movies m1 ON c1.mid = m1.mid
            JOIN Cast c2 ON m1.mid = c2.mid
            JOIN Actors a2 ON c2.aid = a2.aid
            WHERE a1.aid IN (
                SELECT a.aid
                FROM Actors a
                JOIN Cast c ON a.aid = c.aid
                JOIN Movies m ON c.mid = m.mid
                JOIN Cast c2 ON m.mid = c2.mid
                JOIN Actors a2 ON c2.aid = a2.aid
                WHERE a2.fname = 'Kevin' AND a2.lname = 'Bacon'
            )
            AND a2.fname != 'Kevin' AND a2.lname != 'Bacon'
            AND a2.aid NOT IN (
                SELECT a.aid
                FROM Actors a
                JOIN Cast c ON a.aid = c.aid
                JOIN Movies m ON c.mid = m.mid
                JOIN Cast c2 ON m.mid = c2.mid
                JOIN Actors a2 ON c2.aid = a2.aid
                WHERE a2.fname = 'Kevin' AND a2.lname = 'Bacon'
            )
            ORDER BY a2.lname, a2.fname;
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

    def q12(self):
        query = '''
            SELECT a.fname, a.lname, COUNT(m.mid) as totM, AVG(m.rank) as pop
            FROM Actors a
            JOIN Cast c ON a.aid = c.aid
            JOIN Movies m ON c.mid = m.mid
            GROUP BY a.aid
            ORDER BY pop DESC, totM DESC
            LIMIT 20
        '''
        self.cur.execute(query)
        all_rows = self.cur.fetchall()
        return all_rows

if __name__ == "__main__":
    task = Movie_db("cs1656-public.db")
    rows = task.q0()
    print(rows)
    print()
    rows = task.q1()
    print(rows)
    print()
    rows = task.q2()
    print(rows)
    print()
    rows = task.q3()
    print(rows)
    print()
    rows = task.q4()
    print(rows)
    print()
    rows = task.q5()
    print(rows)
    print()
    rows = task.q6()
    print(rows)
    print()
    rows = task.q7()
    print(rows)
    print()
    rows = task.q8()
    print(rows)
    print()
    rows = task.q9()
    print(rows)
    print()
    rows = task.q10()
    print(rows)
    print()
    rows = task.q11()
    print(rows)
    print()
    rows = task.q12()
    print(rows)
    print()
