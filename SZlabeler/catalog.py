#!/usr/bin/env python3
#coding=utf-8
import re
from Career_Platform.octree.OCtree import CTree

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
    def __init__(self, text, time=None, loc=None, org=None,seg=None,
                 labels=None, pos=None):
        Experience.__init__(self,text,time,loc,org,seg,labels)
        self.position = pos

class Person:
    def __init__(self,name):
        self.name = name
        self.work_exp = []  #indexed by rid


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
        result=[]
        for u in self.users:
            for exp in u.work_exp:
                result.append(exp.segmented)
        return result

    def get_all_labels(self):
        result=[]
        for u in self.users:
            for exp in u.work_exp:
                result.append(exp.labels)
        return result

# This function is defined to classify the entries into some general catafories
    # To use this function, you must clarify which parameter you use. 'write_file' or 'read_file'
    # If you use write_file parameter, remember to add parameter 'result'. 
    # The 'result' usually comes from self.parse_catalog() function
    # Otherwise, unexpected error may rise
    def get_classified_parsed(self,result=None,write_file = None,read_file = None,):
        if (read_file == None) and (write_file != None):
            flag = [0]*len(result)
            
            for i in range(len(result)):
                if flag[i] == 1:
                    print('skip %d'%i)
                    continue

                print(result[i])

                while True:
                    if len(result[i]) <= 6 or result[i].find(' ') == -1:
                        key_word = result[i]
                        label = 7
                        break
                    else:
                        key_word = input('input a keyword:\t')
                        try:
                            label = int(input('input the classification:\t'))
                        except:
                            continue

                    if self.key_word_in_entry(result[i],key_word) and (label<=7 and label>=1) :
                        break
                
                flag[i] = 1
                index = result[i].index(key_word)
                
                
                for j in range(i+1,len(result)):
                    if self.key_word_match(result[j][:index+len(key_word)],result[i][:index+len(key_word)]):
                        result[j] = self.manual_classifier(result[j],label)
                        flag[j] = 1
                    else:
                        continue
                
                result[i] = self.manual_classifier(result[i],label)

            with open(write_file,'w',encoding='utf-8') as f:
                for entry in result:
                    f.write(entry+'\n')
            return result

        elif (read_file != None) and (write_file == None):
            result = []
            with open(read_file,'r',encoding = 'utf-8') as f:
                for line in f:
                    result.append(line[:-1])
            print(result)
            return result

        else:
            print('Error! You must specify only one parameter! You will choose either read_file or write_file.')
            print('If you choose read_file, you use the data txt that has been classified manually before.')
            print('If you choose write_file, you will be classifying the entries on site manually. It might be time-consuming!')
            print('If this is your first time to use this function, you need to use write_file parameter. Otherwise,\
                I suggest you use \'read_file\' parameter to save your time')
    
    def key_word_match(self,result,match):
        return result == match

    def key_word_in_entry(self,result,key_word):
        return str(key_word+' ') in result or str(' '+key_word+' ') in result or str(' '+key_word) in result
    
    def manual_classifier(self,result,label):
        if label == 1:
            result = '市政协直属 '+result
        elif label == 2:
            result = '市人大直属 '+result
        elif label == 3:
            result = '市委直属 '+result
        elif label == 4:
            result = '市政府直属 '+result
        elif label == 5:
            result = '事业单位/国企 '+result
        elif label == 6:
            result = '军检法机构 '+result
        elif label == 7:
            result = '其他 '+result
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

    def time_filter(self,
                year,  # only support for one year filter.
                       # e.g, input "2012", it will show all the entries incluing 2012.
                input_file_path):
        with open(input_file_path,'r',encoding='utf-8') as in_file:
            list1 = in_file.readlines()

        output_file_path = 'data/%s_period.txt'%str(year)

        with open(output_file_path,'w',encoding='utf-8') as out_file:
            for line in list1:
                if line.startswith('-') or line.endswith('xls\n'):
                    out_file.write(line)
                else:
                    dash_ind = line.find('—')
                    blank_ind = (' ')
                    t_period_start = line[:4]
                    t_period_end = line[dash_ind+1:dash_ind+5]
                    if year >= int(t_period_start) and year <= int(t_period_end) :
                        out_file.write(line)


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

        # return re.sub("\(.*\)","",line)

   # def remove_text_after_comma(self,line):
        #return re.sub("[、|，|；|,|;].*$","",line)
