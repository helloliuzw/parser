#!/usr/bin/env python3
#coding=utf-8

from __future__ import print_function, unicode_literals

import jieba
import jieba.posseg as pseg
import re
from Career_Platform.parser.db_interface import DBInterface
from pdb import set_trace as bp
class Tokenizer:
    def __init__(self,db_options):

        self.db = DBInterface(db_options)

    def parse_strings(self,list_of_txt):
        pass


    def update_dict_db(self, list_mseg,multiplier=1,
                        remove_containing_words=False,ignore_singleton=True):
        """ add words in list_mseg to tokenizer and the word database
        -------------
        Parameters:
            list_mseg: list of user segmented texts
        """
        # convert list of sentence to a list of list
        list_mseg = [re.split(',| ',r) if (not isinstance(r,list)) \
                            else r for  r in  list_mseg ]
        # flatten to a single list
        words = [ w for  sentence in list_mseg for w in sentence]
        if ignore_singleton:
            # do not add words of single character
            words = [ w for  sentence in list_mseg for w in sentence if len(w)>1]
        # remove from tokenizer prefix words
        new_words = {w:words.count(w) for w in  words }
        if remove_containing_words:
            to_remove= self.db.remove_containing_words_from_db(new_words.keys())
            for w in to_remove:
                self.remove_user_word(w)

        # add to database
        print(new_words)
        self.db.add_words_to_db(new_words )
        #update tokenizer with new words
        for w,freq  in new_words.items():
            self.add_user_word(w,freq = freq*multiplier)
        return list_mseg


    def update_tokenizer_db(self,list_uid,list_rid,list_mseg):
        """ add words in list_mseg to tokenizer and the word database
        -------------
        Parameters:
            list_uid: list of user ids
            list_rid: list of resume ids
            list_mseg: list of user segmented texts
        """
        # convert list of sentence to a list of list
        list_mseg = self.update_dict_db(list_mseg)
        # put manual seg result in database
        for i in range(len(list_uid)):
            self.db.set_user_data_by_id(list_uid[i],list_rid[i],'mseg',
                                        ' '.join(list_mseg[i]))

    def save_userdict(self,filename,mode='w'):
        """ save words in db into a text file """
        print('saving user dict words to',filename)
        word_entries= self.db.read_words_from_db( )
        with open(filename,mode,encoding='UTF-8') as f:
            lines = ['%s %d %s\n' % (word,freq,part) for word,part,freq in word_entries]
            f.writelines(lines)
            f.close()


    def load_userdict_from_txt(self,filename,sync_db=True):
        """ load userdict from text file """
        print('load user dict',filename,'... sync database...')
        # sync database table with what's in txt files
        #self.db.initialize_words_db()

        # load txt file to the tokenizer
        self.load_userdict(filename)
        if sync_db:

            with open(filename,'r' ) as f:
                lines = f.read().splitlines()
            data =[]
            for i, str in enumerate(lines):
                entry = str.split(' ')
                part = entry[2] if len(entry)==3 else ''

                data.append((i, entry[0], part, int(entry[1])))

            self.db.write_word_dict_to_db(data)



    def load_userdict_from_db(self):
        """ load userdict from word table in the database """
        word_entries = self.db.read_words_from_db( )
        for (word, part ,freq) in word_entries:
            self.add_user_word(word,freq)
        print('loaded',len(word_entries),
              'words from userword database')





class JiebaTokenizer(Tokenizer):
    """
    This class is used for Parsing
    Currently Using Jieba
    """
    def __init__(self,db_options):
        Tokenizer.__init__(self,db_options)
        #jieba.enable_paddle()


    def parse_strings(self,list_of_txt, simple=True,HMM=True):

        results = []

        for txt in list_of_txt:

            words = pseg.cut(txt,use_paddle=False, HMM=HMM)
            if simple:
                words = [ w for w ,flag in words if w != ' ']
            else:
                words = [(w ,flag) for w ,flag in words if w != ' ']

            results.append(words)
        return results

    def add_user_word(self,word,freq=50):
        print('adding',word,'freq=',freq, '..\n')
        jieba.add_word(word ,freq)

    def add_user_segs(self,list_of_words,multiplier=2):
        word_freq = {x:list_of_words.count(x) for x in  list_of_words }
        for (word,freq ) in word_freq.items():
            print('word=%s,freq=%d' % (word,freq))
            jieba.add_word(word,freq*multiplier)

    def remove_user_word(self,word):
        print('removing',word,'..\n')
        jieba.del_word(word)

    def suggest_seg(self,seg):
        """ suggest a particular segmentation """
        print('adding',seg,'..\n')
        jieba.suggest_freq(seg,True)

    def load_userdict(self,filename):
        """ load user dict from a file """
        jieba.load_userdict(filename)


    def _word_freq(self,w):
        """ a debug function to check the internal dictionary
        frequency of word w """

        f=jieba.get_FREQ
        return f(w)
'''
class HybridTokenizer(Tokenizer):
    """
    This class is used for Parsing
    Currently Using Jieba
    """
    def __init__(self):
        Tokenizer.__init__(self)

    def parse_strings(self,list_of_txt):
        pass

'''
