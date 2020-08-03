#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Tue May  5 00:05:45 2020

@author: yang
"""
import pymysql
from  pymysql.err import InterfaceError
from Career_Platform.parser.catalog import Person,WorkExperience


class DBInterface:
    """ a utility class that provide an interface with database """
    def __init__(self,db_options):
        self.db_options =   db_options
        self.connect()

    def connect(self):
        try:
            self.conn = pymysql.connect(**self.db_options)
        except Exception as e:
            print('Error connecting to database:{0}'.format(e))
            print('Reconnecting...')
            self.connect()


    def query(self,sql,args=None,commit=False ):
        try:
            cursor = self.conn.cursor()

            if not args:
                res = cursor.execute(sql,[])
            else:
                res = cursor.execute(sql,args)
        except  InterfaceError: #pymysql.OperationalError:
            print('MySQL connection not found. reconnecting...')
            self.connect()
            cursor = self.conn.cursor()

            if not args:
                res = cursor.execute(sql)
            else:
                res = cursor.execute(sql,args)
        if commit:
            self.conn.commit()
        return res,cursor

    def query_many(self,sql,dataset,commit=False):
        try:
            cursor = self.conn.cursor()
            res = cursor.executemany(sql,dataset)

        except  InterfaceError: #pymysql.OperationalError:
            print('MySQL connection not found. reconnecting...')
            self.connect()
            cursor = self.conn.cursor()
            res = cursor.executemany(sql,dataset)
        if commit:
            self.conn.commit()
        return   res,cursor

#####################################################
# RESUME CATALOG
#####################################################
    def initialize_catalog_db(self):

        sql = """DROP TABLE IF EXISTS user_data;"""
        res,cursor = self.query(sql )

        sql = """
        CREATE TABLE user_data (
        uid INT,
        rid INT,
        time CHAR(32),
        raw CHAR(128),
        seg CHAR(128),
        loc CHAR(32),
        occ CHAR(32),
        label CHAR(128),
        mseg CHAR(128),
        mlabel CHAR(128),
        batch INT,
        mtimestamp CHAR(32),
        contributor varchar(255) DEFAULT NULL
        ) DEFAULT CHARSET=gbk;
        """
        self.query(sql,commit=True)

        res,cursor =self.query('desc user_data;')
        print(res)

    def read_catalog(self,catalog, append=True):
        """
        load entries from database and store in catalog
        """
        if not append:
            catalog.clear()

        sql = "SELECT DISTINCT uid FROM user_data;"
        res, cursor = self.query(sql)
        uids =  cursor.fetchall()
        catalog.users= [Person(name=i) for i in uids ]
        for i,uid in enumerate(uids):
            sql = "SELECT * FROM user_data WHERE uid = %s" % uid
            res,cursor = self.query(sql)
            data =  cursor.fetchall()
            for j,entry in enumerate(data):
                seg = entry[4] if entry[6]=='' else entry[6]
                labels = entry[5] if entry[7]=='' else entry[7]
                e = WorkExperience(text=entry[3],time=entry[2],seg=seg,
                                   labels=labels  )
                catalog.users[i].work_exp.append(e)


    def write_catalog(self, catalog, clear_table=False):
        """
        insert all resume entries info into database.

        Note: loc (location) and occ (occupation) are not set as the current
            parsing results are not accurate enough

        Parameters
        ----------
        catalog: Catalog
          container for the resume data

        """
        if clear_table:
            # remove all entries in user_data
            sql = '''truncate table user_data'''
            self.query(sql,commit =True)

        # writing content
        dataset=[]
        for uid,u in enumerate(catalog.users):
            for rid,exp in enumerate(u.work_exp):
                if exp:
                    labels = ''
                    seg =''
                    if exp.labels:
                        labels = ','.join(exp.labels)
                    if exp.segmented:
                        seg = exp.segmented

                    row = (uid,rid,exp.time,exp.text,seg,
                            '','',
                              labels ,
                            '','',exp.batch_id,'','')
                    print(row)
                    dataset.append(row)

        sql = '''insert into user_data values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'''
        res ,_= self.query_many(sql,dataset,commit=True)
        print(res)

    def set_user_data_by_id(self,uid,rid,colname,value):

        sql = '''UPDATE user_data SET {}='{}' WHERE uid={} and rid={}'''.format(colname,value,uid,rid)

        self.query(sql,commit = True )

#####################################################
# Manually Defined Label Rules
#####################################################

    def initialize_rules_db(self):
        sql = """DROP TABLE IF EXISTS label_rules;"""

        self.query(sql,commit = True)
        sql = """
        CREATE TABLE label_rules (
        label CHAR(128),
        keywords CHAR(128)
        ) DEFAULT CHARSET=gbk;
        """
        _,cursor = self.query(sql,commit = True)
        res,_ = self.query( 'desc label_rules;')
        print(res)

    def write_rule_dict(self,rule_dict,clear_table=False):

        if clear_table:
            # remove all entries in user_data
            sql = '''truncate table label_rules;'''
            self.query(sql,commit=True)

        dataset=[]
        for w,v in rule_dict.items():
            dataset.append((w,','.join(v)))
        print(dataset[0])
        sql = '''insert into label_rules values(%s,%s);'''
        res,_= self.query_many(sql,dataset,commit=True)
        print(res)


    # =========================================================================
    #add one word into tabel where key=key
    # ex:['留学经历']=['美国','英国','瑞士']
    #db.save_db('留学经历','十佳街道书记')
    #['留学经历']=['美国','英国','瑞士','十佳街道书记']
    # =========================================================================
    def add_rule_to_db(self,key,word):
        #cursor = self.mysql.cursor()
        sql = "SELECT keywords FROM user_data WHERE label = %s;"
        _, cursor = self.query(sql,key)
        data =  cursor.fetchone()
        data_list=data[0].split(',')
        data_list.append(word)
        data_str=','.join(set(data_list))
        sql = "update label_rules set keywords = %s WHERE label=%s;"
        self.query(sql,[data_str,key],commit=True)

    # =========================================================================
    # Get dict{key,word} from db
    # =========================================================================
    def db_2_rule_dict(self):
        new_dict={}
        sql = "SELECT label,keywords FROM label_rules;"
        _,cursor =  self.query(sql)
        data =  cursor.fetchall()
        for thing in data:
            new_dict[thing[0]]=thing[1].split(',')
        return new_dict


###########################################################
# new word dictionary
###########################################################

    def initialize_words_db(self):

        sql = """DROP TABLE IF EXISTS words;"""
        self.query(sql,commit= True)
        sql="""
        CREATE TABLE words (
          wid int DEFAULT NULL,
          word varchar(255) DEFAULT NULL,
          part varchar(32) DEFAULT NULL,
          frequency int DEFAULT NULL,
        UNIQUE KEY word (word)
        ) DEFAULT CHARSET=gbk;
        """
        self.query(sql,commit=True)
        res,_=self.query('desc words;')
        print(res)


        sql="""INSERT INTO words (wid,word,part,frequency) VALUES (0,%s,%s,%s);"""

        self.query(sql,( '1','',0),commit=True)

    def write_word_dict_to_db(self,worddict,clear_table=True):

        if clear_table:
            # remove all entries in user_data
            sql = '''truncate table words'''
            self.query(sql,commit=True)


        sql = '''insert into words values(%s,%s,%s,%s);'''
        res,_ = self.query_many(sql,worddict,commit=True)
        print(res)


    def add_words_to_db(self, word_freq  ):
        """
        insert words to the word table. if word exist, increment the frequency
        otherwise, insert a new word with frequency 1.

        Parameters:
            list_of_words: a list of strings

        Returns:
            new_words: a dictionary of unique words and frequency updated/added

        """
        for (word,freq ) in word_freq.items():
            sql =  "SELECT wid FROM words WHERE word=%s" ;
            _,cursor = self.query(sql,word)
            wid = cursor.fetchone()
            if not wid:
                sql = "INSERT INTO words (wid,word,part,frequency) SELECT \
                        MAX(wid)+1,%s,%s,%s from words"
                self.query(sql, ( word, '',freq) ,commit=True)
            else:
                sql = "UPDATE words SET frequency = frequency+%s WHERE word=%s"
                self.query(sql,[freq,word],commit= True)

    def remove_containing_words_from_db(self, word_list,two_sided=True):
        """
        check if each word in word_list is a proper prefix of an existing word
        in the dictionary;
        if yes, remove the existing word and all words starting/ending with
        the given word from the dictionary.

        Parameters
        ------------
        two_sided: True if remove dictionary words starting or ending with a word in the list;
                    False if only remove dictionary words starting with the given word
        """
        words_to_remove = []
        for word in word_list:
            if two_sided:
                sql =  "SELECT word FROM words WHERE word LIKE %s or word LIKE %s"
                _,cursor = self.query(sql , (word+'_%%', '%%_'+word) )
            else:
                sql =  "SELECT word FROM words WHERE word LIKE %s"
                _,cursor = self.query(sql ,word+'_%%' )
            data =  cursor.fetchall()
            if not data:
                continue
            to_remove = [ x[0] for x in data ]
            words_to_remove +=   to_remove

            if len(to_remove)==1:
                sql = "DELETE FROM words WHERE word=%s"
                self.query(sql , to_remove[0],commit = True)
            else:
                sql = "DELETE FROM words WHERE word in {}".format(tuple(to_remove))

                self.query(sql,commit=True )
        return set(words_to_remove)

    def read_words_from_db(self,list_of_words=None):
        """ get table entries of words in list_of_words
            if list_of_words is not provided, return all entries in the table
        """
        if list_of_words:
            if len(list_of_words)==1:
                sql = "SELECT word,part,frequency FROM words WHERE word=%s;"
                _,cursor = self.query(sql,  list_of_words[0])
            else:
                sql = "SELECT word,part,frequency FROM words WHERE word in {};".format(tuple(list_of_words))
                _,cursor = self.query(sql)
        else:
            sql = "SELECT word,part,frequency FROM words;"
            _,cursor = self.query(sql)

        result= cursor.fetchall()
        return result;
