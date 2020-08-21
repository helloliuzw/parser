#!/usr/bin/env python3
#coding=utf-8
from matplotlib import pyplot as plt
from matplotlib.pyplot import MultipleLocator
# from Career_Platform.octree.OCtree import CTree
import os
import json
import datetime
from datetime import date

location = os.path.abspath(os.path.dirname(__file__))

class Experience:
    def __init__(self,text, time=None, loc=None, org=None,seg=None,labels=None):
        self.text=text
        self.time=time
        self.organization=org
        self.location=loc
        self.segmented = seg # segmented string
        self.labels = labels # list of labels
        self.batch_id =None
class WorkExperience(Experience):
    '''The format of `time` and `labels` should be like:
    '2015.08—2019.07' ['双一流大学','理工方向']
    '''
    def __init__(self, text, time=None, loc=None, org=None,seg=None,
                 labels=None, pos=None):
        Experience.__init__(self,text,time,loc,org,seg,labels)
        self.position = pos

class Person:
    '''Description Here'''
    def __init__(self,name,gender='',age=30):
        self.name = name
        self.gender = gender
        self.age = age
        self.tags = []
        self.work_exp = []  #indexed by rid
        self.work_labels = []
        for item in self.work_exp:
            self.work_labels.extend(item.labels)
        self.work_labels = list(set(self.work_labels))
    def __str__(self):
        return '姓名：'+self.name+'，共有'+str(self.__len__())+'条经历；'
    
    def update_resumes(self,L):
        self.work_exp = L
        self.work_labels = []
        for item in self.work_exp:
            self.work_labels.extend(item.labels)
        self.work_labels = list(set(self.work_labels))
        self.survival()
        
    def survival(self,query_condition_path = location+'/config/query_condition.json'):
        '''construct a survival time dictionary(STD)'''
        f = open(query_condition_path,encoding='utf-8')
        condition_dict = json.load(f)
        f.close()
        
        self.STD = {}
        for key in self.work_labels:
            self.STD[key] = [0,(0,0),[],condition_dict[key]['Timelen'],condition_dict[key]['Period'],condition_dict[key]['Now']]
        for exp in self.work_exp:
            strtuple = exp.time.split('—')
            datetuple = [date(int(eval(item)//1),round((eval(item)%1)*100),1) for item in strtuple]
            interval = (datetuple[1]-datetuple[0]).days
            for key in exp.labels:
                self.STD[key][0] += interval
                self.STD[key][2].append(datetuple)
        for key in self.STD.keys():
            self.STD[key][1] = (self.STD[key][2][0][0],self.STD[key][2][-1][1])
            self.STD[key][0] = self.STD[key][0]
        return self.STD
    
    def checkbytime(self,year,month,day):
        checktime = date(year,month,day)
        for exp in self.work_exp:
            strtuple = exp.time.split('—')
            datetuple = [date(int(eval(item)//1),round((eval(item)%1)*100),1) for item in strtuple]
            if checktime>datetuple[0] and checktime<datetuple[1]:
                return [exp.text,exp.labels]
        return None
    
    def reply(self,allquery):
        '''imageine the Query looks like :
        allquery = {
        'personal':{'gender':'W','age':(20,50)},
        'workexp':{
            '基层经历':{'Timelen':730,'Period':(datetime.date(2001, 9, 1), datetime.date(2006, 4, 1)),'Now':False},
            '教育':{'Timelen':730,'Now':False}
        }
        }
        在不勾选任何附加项的情况下，返回的Query应为：
        allquery = {
        'personal':{'gender':None,'age':(0,120)},
        'workexp':{
            '勾选的标签':{'Timelen':1,'Period':(datetime.date(1949, 10, 1), datetime.date(9999, 10, 1)),'Now':False},
        }
        }
        '''
        pquery = allquery['personal']
        if pquery['gender'] != None:
            if pquery['gender'] != self.gender:
                return False
        if (self.age < pquery['age'][0]) or (self.age > pquery['age'][1]):
            return False
        
        query = allquery['workexp']
        querykeys = list(query.keys())
        if set(querykeys).issubset(set(self.work_labels)) == 0:
            return False
        for key in querykeys:
            if self.STD[key][3] == True:
                if query[key]['Timelen'] > self.STD[key][0]:
                    return False
            if self.STD[key][5] == True:
                if query[key]['Now']==True:
                    if key not in self.work_exp[-1].labels:
                        return False
            if self.STD[key][4] == True:
                flag = 0
                for tu in self.STD[key][2]:
                    if flag == 1:
                        break
                    for d in tu:
                        if d>query[key]['Period'][0] and d<query[key]['Period'][1]:
                            flag = 1
                if flag == 0:
                    return False

        return True
        
        
    def labelmap(self):
        plt.grid(True)
        X,Y = [],[]
        Ydict = {}
        for i,key in enumerate(self.work_labels):
            Ydict[key] = i+1
        plt.yticks(fontproperties="STSong") 
        plt.yticks([Ydict[key] for key in self.work_labels],self.work_labels)
        for exp in self.work_exp:
            strtuple = exp.time.split('—')
            numtuple = [self.date2num(zw) for zw in strtuple]
            plt.plot([numtuple[0]]*2,[0.5,len(self.work_labels)+0.5],linestyle=':',color='grey')
            plt.text(numtuple[0],len(self.work_labels)+0.5,strtuple[0],ha='center')
            X.append(numtuple)
            Y.append(exp.labels)
        for i,timelen in enumerate(X):
            for label in Y[i]:
                plt.plot(timelen,[Ydict[label]]*len(timelen),linewidth=5.0)
        plt.show()
                
    def date2num(self,text,reverse=False):
        if reverse==False:
            num = eval(text)
            return (num//1+(num%1)/(0.12))
        return str(text//1+round((text%1)*12)/100)
        
        

class Catalog:
    def __init__(self):
        self.users = [] # indexed by uid
        self.tokenizer = None
        self.classifier = None

    def clear(self):
        self.users = []

    def print_2(self, raw=False,max_n = 2000):
        ct = 0
        for u in self.users:
            print('name:', u.name )
            for i,exp in enumerate(u.work_exp):
                if ct >= max_n:
                    return
                if raw:
                    print(i,exp.text)
                else:
                    print(i,exp.time,'parsed:',exp.segmented,
                          'labels:',exp.labels, 'loc:',exp.location,
                          'pos:',exp.position,'batch:',exp.batch_id)
                ct+=1


    def get_all_parsed(self):
        result = []
        for uid,user in enumerate(self.users):
            for rid,exp in enumerate(user.work_exp):
                result.append(((uid, rid), exp.segmented))
        return result

    def get_all_labels(self):
        result=[]
        for u in self.users:
            for exp in u.work_exp:
                result.append(exp.labels)
        return result

    def add_tokenizer(self, tokenizer):
        self.tokenizer = tokenizer

    def parse_catalog(self,HMM=True):
        if not self.tokenizer:
            print('Error: Please add a tokenizer first!')
            return
        for user in self.users:
            for exp in user.work_exp:
                result = self.tokenizer.parse_strings([exp.text],simple=False,HMM=HMM)[0]
                if len(result)<=3:
                    print('[Error] fail to parse', exp.text)
                    continue
                result = result[3:]
                exp.location=''
                org_pos = []
                exp.segmented=' '.join([word for  word,flag in result ])
                for word,flag in result:
                    if flag == 'ns' or flag == 'LOC':
                        exp.location += word

                    if flag != 'm' and flag != 'x':
                        org_pos.append( (word,flag) )
                if len(org_pos)>1:
                    exp.position =   org_pos[-1][0]
                    exp.organization=''.join( [w for w,f in org_pos[:-1]])

    def add_classifier(self,cla):
        self.classifier = cla

    def classify_all(self):
        if not self.classifier:
            print('Error: Please add a label classifier first!')
        for user in self.users:
            for exp in user.work_exp:
                print(exp.text)
                if exp.organization and exp.position:
                    exp.labels  = self.classifier.classify(exp.organization+exp.position)
                else:
                    exp.labels = ['undefined']


class ResumeFileIO(Catalog):
    def __init__(self):
        Catalog.__init__(self)
        #self.print_2(raw=True)


    # This function is defined to write each entry of the user data to one line,
    # rather than break into several lines as in ori.txt,
    # which is quite helpful for comma-removing later
    def pre_user_data(self,file_path):
        f_ori = open(file_path,'r',encoding='utf-8')
        entry_list = []
        new_entry_list = []
        i = 0

        for line in f_ori:
            line = line.replace(',','，')
            line = re.sub("[；|;|。].*$","",line)
            line = line.strip()
            line = self.remove_parentheses(line)

            # if we use "-今" instead of "-今     ", unexpected error happened.
            # So i replace it with "-今     "
            line = re.sub("—今     ","—9999.99",line)
            entry_list.append(line)

        while i <= len(entry_list)-1:
            # set a convergent condition
            if i == len(entry_list)-1:
                new_entry_list.append(entry_list[i])
                break

            else:
                new_entry = entry_list[i]
                # cond_1 means next line does not start with '---'
                cond_1 = ( re.match('^-.*',entry_list[i+1]) == None )
                # cond_2 means next line does not start with number 1 to 9
                cond_2 = ( re.match('^[1-9].*',entry_list[i+1]) ==None )

                while cond_1 and cond_2 :
                    i = i+1
                    new_entry += entry_list[i]
                    if i < len(entry_list)-1:
                        cond_1 = ( re.match('^-.*',entry_list[i+1]) == None )
                        cond_2 = ( re.match('^[1-9].*',entry_list[i+1]) == None )
                    else:
                        break
                new_entry_list.append(new_entry)
                i += 1
        return new_entry_list

    def remove_comma_round_1(self,pre_data,file_path):
        # remove comma_2, do not create entries, and write into file
        list_with_comma_2 = []

        # 此函数用于替换字符串中特定位置的字符
        def replace_char(string,char,index):
            string = list(string)
            string[index] = char
            return ''.join(string)

        for entry in pre_data:
            #去掉job_experience开头的“兼”或“兼职"字眼
            blank_ind = entry.find(' ')
            job = entry[blank_ind+1:]
            if job[0] == '兼':
                entry = entry[:blank_ind+1] + job[1:]
            if job[:2] == '兼职':
                entry = entry[:blank_ind+1] + job[2:]

            # 找到“兼”的index,计算其到下一个标点（若有）的字符串长度，
            # 和阈值（暂定为8）比较，小于等于阈值替换为“、” ，大于阈值替换为“，”
            threshold = 8
            tmp_entry = ''
            part_time_ind = entry.find('兼')
            while part_time_ind != -1:
                tmp_entry = tmp_entry[part_time_ind+1:]
                tmp_index_1 = tmp_entry.find('，')
                tmp_index_2 = tmp_entry.find('、')
                if (tmp_index_1 != -1) and (tmp_index_2 != -1):
                    tmp_index = min(tmp_index_1,tmp_index_2)
                if (tmp_index_1 == -1) and (tmp_index_2 != -1):
                    tmp_index = tmp_index_2
                if (tmp_index_1 != -1) and (tmp_index_2 == -1):
                    tmp_index = tmp_index_1
                else:
                    # 当后面没有任何标点时,设tmp_index = 1000,取整个entry
                    tmp_index = 1000

                part_time_entry = entry[part_time_ind+1:tmp_index]

                if len(part_time_entry) > threshold:
                    entry = replace_char(entry,'，',part_time_ind)
                else:
                    entry = replace_char(entry,'、',part_time_ind)
                part_time_ind = tmp_entry.find('兼')

            entry = entry.replace('，，','，')
            entry = entry.replace('，、','、')
            entry = entry.replace('、、','、')
            entry = entry.replace('、，','，')

            comma_ind = entry.find('，')
            while comma_ind != -1:
                blank_ind = entry.find(' ')
                list_with_comma_2.append(entry[:comma_ind])
                entry = entry[:blank_ind]+'  '+entry[comma_ind+1:]
                comma_ind = entry.find('，')
            list_with_comma_2.append(entry)

        with open(file_path,'w',encoding='utf-8') as f:
            for entry in list_with_comma_2:
                comma_2_ind = entry.find('、')
                if comma_2_ind != -1:
                    f.write(entry[:comma_2_ind]+'\n')
                else:
                    f.write(entry+'\n')
        f.close

    def remove_comma_round_2(self,pre_data,tree,output_path):
        # remove comma_2, create new entries via prefix, and write into file
        list_with_comma_2 = []

        # 此函数用于替换字符串中特定位置的字符
        def replace_char(string,char,index):
            string = list(string)
            string[index] = char
            return ''.join(string)

        for entry in pre_data:
            #去掉entry开头的“兼”或“兼职"字眼
            blank_ind = entry.find(' ')
            job = entry[blank_ind+1:]
            if job[0] == '兼':
                entry = entry[:blank_ind+1] + job[1:]
            if job[:2] == '兼职':
                entry = entry[:blank_ind+1] + job[2:]

            # 找到“兼”的index,计算其到下一个标点（若有）的字符串长度，
            # 和阈值（暂定为8）比较，小于等于阈值替换为“、” ，大于阈值替换为“，”
            threshold = 8
            tmp_entry = ''
            part_time_ind = entry.find('兼')
            while part_time_ind != -1:
                tmp_entry = tmp_entry[part_time_ind+1:]
                tmp_index_1 = tmp_entry.find('，')
                tmp_index_2 = tmp_entry.find('、')
                if (tmp_index_1 != -1) and (tmp_index_2 != -1):
                    tmp_index = min(tmp_index_1,tmp_index_2)
                if (tmp_index_1 == -1) and (tmp_index_2 != -1):
                    tmp_index = tmp_index_2
                if (tmp_index_1 != -1) and (tmp_index_2 == -1):
                    tmp_index = tmp_index_1
                else:
                    tmp_index = 1000

                part_time_entry = entry[part_time_ind+1:tmp_index]
                if len(part_time_entry) > threshold:
                    entry = replace_char(entry,'，',part_time_ind)
                else:
                    entry = replace_char(entry,'、',part_time_ind)
                part_time_ind = tmp_entry.find('兼')

            entry = entry.replace('，，','，')
            entry = entry.replace('，、','、')
            entry = entry.replace('、、','、')
            entry = entry.replace('、，','，')
            comma_ind = entry.find('，')
            while comma_ind != -1:
                blank_ind = entry.find(' ')
                list_with_comma_2.append(entry[:comma_ind])
                entry = entry[:blank_ind]+'  '+entry[comma_ind+1:]
                comma_ind = entry.find('，')
            list_with_comma_2.append(entry)

        with open(output_path,'w',encoding='utf-8') as f:
            b = []
            for entry in list_with_comma_2:
                comma_2_ind = entry.find('、')
                blank_ind = entry.find(' ')
                time_period = entry[:blank_ind]
                if comma_2_ind == -1:
                    f.write(entry+'\n')

                else:
                    a = entry[blank_ind+2:comma_2_ind]
                    n1,_ = tree.greedy_prefix_match(a)
                    prefix_list= [ n.data.name for n in tree.get_prefix(n1)]
                    prefix = ''

                    for i in range( max( (len(prefix_list)-1), 1 )):
                        prefix += prefix_list[i]

                    flag = True
                    while comma_2_ind != -1:
                        if flag == True:
                            f.write(entry[:comma_2_ind]+'\n')
                            flag = False
                        else:
                            entry = entry[comma_2_ind+1:]
                            comma_2_ind = entry.find('、')
                            if comma_2_ind == -1:
                                f.write(time_period + '  ' + prefix + entry+'\n')
                                break
                            else:
                                f.write(time_period + '  ' + prefix + entry[:comma_2_ind]+'\n')
        f.close()

    def length_filter(self,input_file,output_file):
        tmp = []
        with open(input_file,'r',encoding='utf-8') as f1:
            for line in f1:
                tmp.append(line)

        with open(output_file,'w',encoding='utf-8') as f2:
            for entry in tmp:
                if entry.startswith('-') or entry.endswith('.xls\n'):
                    f2.write(entry)
                elif len(entry)>25:
                    f2.write(entry)

    def read_resume_txt(self,file_path):
        newPerson = None
        newEntry = None
        with open(file_path,'r',encoding='UTF-8' ) as f:
            for line in f:
                line= line.strip()
                m_head = re.match("([0-9]+).xls",line)
                m_entry = re.match("(\d{4}.\d{1,2}?—\d{4}.\d{1,2})\s*(.+)",line)
                # m_entry_cont = re.match("^(?![-|—]).*",line)
                if m_head :
                    if newPerson:
                        if newEntry:
                            newPerson.work_exp.append(newEntry)
                            newEntry=None
                        self.users.append(newPerson)
                    newPerson = Person(m_head.group(1))
                    #print(newPerson.name)
                elif m_entry:
                    if newEntry and len(newEntry.text)>=20 :
                        # only add entries at least 20 characters long
                        newPerson.work_exp.append(newEntry)
                    time = m_entry.group(1)
                    text = m_entry.group(2)
                    newEntry = WorkExperience(line,time=time )
                    # print(newEntry.text)
                # elif m_entry_cont:
                   #  newEntry.text +=line


    def remove_parentheses(self,line):
        p_left_index = line.find('(')
        if p_left_index == -1:
            pass
        else:
            p_right_index = line.find(')')
            content = line[p_left_index+1:p_right_index]
            content = content.strip()
            if content =='':
                line = line[:p_left_index]+line[p_right_index+1:]
            else:
                line = line[:p_left_index]+content+line[p_right_index+1:]

        return line
if __name__ == '__main__':
    print('catalog.py debugging')
    liu = Person('张三')
    liu.gender = 'W'
    liu.age = 30
    #r0 = WorkExperience(time='',labels=[])
    r1 = WorkExperience(text='某某大学学习',time='1997.08—2001.09',labels=['双一流大学'])
    r2= WorkExperience(text='深圳龙华区公务员',time='2001.09—2006.04',labels=['深圳','龙华','基层工作'])
    r3= WorkExperience(text='深圳市党校校长',time='2006.04—2016.10',labels=['深圳','教育'])
    r4= WorkExperience(text='深圳市人大代表',time='2016.10—2020.09',labels=['深圳','市人大直属'])
    liu.update_resumes([r1,r2,r3,r4])
    liu.labelmap()
    
    print(liu.survival())
    
    query = {
            'personal':{'gender':'W','age':(20,50)},
            'workexp':{
                #'基层经历':{'Timelen':730,'Period':(datetime.date(2001, 9, 1), datetime.date(2006, 4, 1)),'Now':False},
                '教育':{'Timelen':730,'Now':False}
            }
            }
    print('\nreply query:',liu.reply(query))
    print('check by time:',liu.checkbytime(2015,2,3))