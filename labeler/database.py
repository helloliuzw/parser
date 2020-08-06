#!/usr/bin/env python3
#coding=utf-8
import pymysql

class backend_database_connection():

    def __init__(self,host='localhost',user='root',password='',
                database='CAREER', port=3306):
        # 1.我们先建立数据库的连接信息
        self.mysql = pymysql.connect(host=host, user=user, password=password, port=port,database=database)

    def read_db(self,list_uid,list_rid):

        #read value from data base
        cursor = self.mysql.cursor()

        sql = "SELECT label FROM user_data WHERE uid = %s AND rid = %s;"

        for i in range(len(list_uid)):
            uid_rid = [list_uid[i], list_rid[i]]
            cursor.execute(sql,uid_rid)
            data = cursor.fetchone()
            print(data)

        #return data
        self.mysql.close()

    def read_db_all(self):

        #read value from data base
        cursor = self.mysql.cursor()

        sql = "SELECT rid,uid,label,mlabel,seg FROM user_data;"

        cursor.execute(sql)
        data = cursor.fetchall()

        #print(data)
        return data
        self.mysql.close()


    def save_db(self,list_text,list_uid,list_rid):

        cursor = self.mysql.cursor()
        sql = "update user_data set mlabel = %s where uid=%s and rid = %s;"


        for i in range(len(list_uid)):
            mesg_uid_rid = [str(list_text[i]),list_uid[i],list_rid[i]]
            cursor.execute(sql,mesg_uid_rid)
            self.mysql.commit()

        self.mysql.close()

    def save_db_t(self,list_text,list_uid,list_rid):

        print('write to mlabel',list_text)
        cursor = self.mysql.cursor()
        sql = "update user_data set mseg = %s where uid=%s and rid = %s;"

        for i in range(len(list_uid)):
            #print(len(list_uid))
            mesg_uid_rid = [str(list_text[i]),list_uid[i],list_rid[i]]
            #print(mesg_uid_rid[i])
            cursor.execute(sql,mesg_uid_rid)
            self.mysql.commit()
        #data = cursor.fetchone()
        #print(data)
        self.mysql.close()


    def read_db_t(self,list_uid,list_rid):

        cursor = self.mysql.cursor()
        sql = "SELECT seg FROM user_data WHERE uid = %s AND rid = %s;"

        for i in range(len(list_uid)):
            uid_rid = [list_uid[i], list_rid[i]]
            cursor.execute(sql,uid_rid)
            data = cursor.fetchone()
            print(data)
        self.mysql.close()


    def read_db_dict(self,list_mseg):
        #read value from data base
        cursor = self.mysql.cursor()
        sql = "SELECT word,part,Frequency FROM word WHERE word = %s;"
        for i in range(len(list_mseg)):
            cursor.execute(sql,list_mseg[i])
            data = cursor.fetchone()
            print(data)
        #return data
        self.mysql.close()

    def save_db_withoutur(self,list_uid,list_rid,list_label):
        cursor = self.mysql.cursor()
        sql = 'INSERT INTO user_data VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

        for i in range(len(list_uid)):
            whole_list = [list_uid[i],list_rid[i],'','','','','',list_label[i],'','',0,'']
            #print(str(list_word[i]))
            #print(str(list_part[i]))
            #print(list_freqeucny[i])
            #print(list_wid[i])
            cursor.execute(sql,whole_list)
            self.mysql.commit()
            #data = cursor.fetchone()
            #print(data)
        self.mysql.close()
    def write_db_dict(self,list_wid,list_word,list_part,list_freqeucny):

        cursor = self.mysql.cursor()
        #sql = "update word set word = 'aaa', part = 'k', Frequency=9 where wid = 3;"
        sql = 'INSERT INTO word VALUES (%s, %s, %s, %s)'
        print(len(list_wid))
        for i in range(len(list_wid)):
            whole_list = [list_wid[i],list_word[i],list_part[i],list_freqeucny[i]]
            #print(str(list_word[i]))
            #print(str(list_part[i]))
            #print(list_freqeucny[i])
            #print(list_wid[i])
            cursor.execute(sql,whole_list)
            self.mysql.commit()
            #data = cursor.fetchone()
            #print(data)
        self.mysql.close()

    def get_lastid_dict(self):
        cursor = self.mysql.cursor()
        sql = "SELECT wid FROM word ORDER BY wid DESC LIMIT 1;"
        cursor.execute(sql)
        data = cursor.fetchone()
        return data
        self.mysql.close()
###############################################################################################

if __name__ == '__main__':
    p = backend_database_connection()
    #p.__init__()
    list_uid = [1000,1001]
    list_rid = [1000,1001]
    list_text = ['jjaaaaaaaaaaa','123']
    #p.save_db(list_text,list_uid,list_rid)
    #p.read_db(list_uid,list_rid)
    #p.save_db_t(list_text,list_uid,list_rid)
    #p.read_db_t(list_uid,list_rid)
    list_t = ['纪检监察,党的建设,政法,公安,法律,外事和港澳工作,经济,金融,产业,科技,企业管理,财务,工程建设,国土规划,交通运输,生态环境,水务,教育,卫生,信息技术,紧急处突,群团工作,基层,政策研究,单位一把手经历,街道书记经历,经历,部队经历,援派和扶贫工作经历,留学经历,新担当作为先进典型,十佳街道书记','']

    list_wid = [12,13,14,15]
    list_word = ['市长','aa']
    list_part = ['n','n','n','n']
    list_freqeucny = [100,100,100,100]
    list_mseg = ['aa','bb']
    #p.write_db_dict(list_wid,list_word,list_part,list_freqeucny)
    #p.read_db_dict(list_mseg)
    p.save_db_withoutur(list_uid,list_rid,list_t)
