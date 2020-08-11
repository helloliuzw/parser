#!/usr/bin/env python3
#coding=utf-8
import numpy as np
import json
import sklearn
from sklearn.linear_model import SGDClassifier
from sklearn.multiclass  import OneVsRestClassifier
from gensim.models import FastText
#from Career_Platform.parser.database import backend_database_connection
#from Career_Platform.parser.exceptions import TrainDataException
import re,os,pickle

class LabelClassifier:
    """
    base class for label classifier

    --------
    Parameter:
        label_dict: a map from integer to string label
    """
    def __init__(self,label_dict_path=os.path.abspath(os.path.dirname(__file__))+'/../data/labels.txt'):
        self.labeldict = {}  # dictionary that maps int to label text
        self.labeldictR = {} # maps label text to int
        self.load_label_dict(label_dict_path)
        #print(self.labeldictR)

    def load_label_dict(self,filename):
        with open(filename,encoding='UTF-8') as f:
            data = f.read().splitlines()
        self.labeldict = { i:a.split('\t')[0] for (i,a) in enumerate(data)}
        self.labeldictR = { a:i  for (i,a) in self.labeldict.items()}

    '''
    def update_classifier_db(self,list_rid,list_uid,list_mseg,list_mlabel):
        for index,thing in  enumerate(list_mseg):
            list_mseg[index]=list_mseg[index].replace('，','').replace('|','').replace(' ','').replace(',','')

        print(list_mlabel)
        self.train_update(list_mseg, list_mlabel)

        # update the database with new prediction
        labels = [ ','.join(self.classify(sen) ) for sen in list_mseg ]
        j = backend_database_connection()
        j.save_db(labels,list_uid,list_rid)
    '''


    # abstract function to be reimplemented in subclasses.
    def classify(self,string):
        pass

    # abstract function to be reimplemented in subclasses.
    def train_update(self, list_mseg, list_mlabel):
        pass


class ManualLabelClassifier(LabelClassifier):

    """ a rule-based  classifier using keywords
        can be accelerated using a reversed dictionary or
        suffix tree string matching """

    def __init__(self, rules={}):
        LabelClassifier.__init__(self)
        self.rule_dict = rules

    def classify(self,string):
        labels=[]
        for (label,keywords) in  self.rule_dict.items():
            for word in keywords:
                if(word in string):
                    labels.append(label)
                    break
        if(len(labels)==0):
            labels.append('undefined')
        return labels


    def import_label_rules(self,filename):
        with open(filename,encoding='UTF-8') as f:
            data = f.read().splitlines()
            f.close()

        self.rule_dict = {}
        for line in data:
            words =line.split('\t')
            if len(words)>1 and words[1]!='':
                self.rule_dict[words[0]] = words[1].split(',')
            else:
                self.rule_dict[words[0]] = []



class ExpRuleClassifier(LabelClassifier):
    def __init__(self,rule_label_path = os.path.abspath(os.path.dirname(__file__))+'/config/rule_label.json',hybrid_label_path = os.path.abspath(os.path.dirname(__file__))+'/config/hybrid_rule_label.json'):
        LabelClassifier.__init__(self)
        f = open(rule_label_path,encoding='utf-8')
        self.label_dic = json.load(f)
        f.close()
        self.groupkeys = list(self.label_dic.keys())
        f = open(hybrid_label_path,encoding='utf-8')
        self.hylabel_dic = json.load(f)
        f.close()
        self.hybridkeys = list(self.hylabel_dic.keys())
        
    def classify(self,text,Hybrid = True):
        final = {}
        for groupname in self.groupkeys:
            res = self.groupclassify(groupname,text)
            final = {**final,**res}
        if Hybrid:
            final = self.addhybridlabel(final)
        return final
    
    def groupclassify(self,groupname,text,f=1):
        jsondict = self.label_dic
        group = jsondict[groupname]
        innerkeys = list(group.keys())
        addition = innerkeys[3:]
        
        result = {group['default']:False}
        for label in addition:
            result[label] = False
        
        if f==1:
            f = self.method1
        elif f==2:
            f = self.method2
        flag = f(text,group['isexist'])
        if f(text,group['remove']):
            flag = False
        if flag:
            for label in addition:
                temp = group[label]
                if f(text,temp):
                    result[label] = True
                    if result.get('')!=None:
                        del result['']
                    return result
            result[group['default']] = True
        if result.get('')!=None:
            del result['']
        return result
    
    def hybridclassify(self,labelname,D):
        jsondict = self.hylabel_dic
        f = eval(jsondict[labelname])        
        result = {labelname:False}        
        result[labelname] = f(D)
        return result
    
    def addhybridlabel(self,result_dict):
        for labelname in self.hybridkeys:
            res = self.hybridclassify(labelname,result_dict)
            result_dict = {**result_dict, **res}
        return result_dict
    '''存在性判断'''
    def method1(self,text,D):
        for item in D['keyword']:
            if item in text:
                return True
        for reg in D['regular']:
            if re.search(reg,text) != None:
                return True
        return False
    '''任意性判断'''
    def method2(self,text,D):
        for item in D['keyword']:
            if item not in text:
                return False
        return True
    '''简单的Hybrid Label生成法'''
    def method3(self,text,L,n=2):
        count = 0
        for item in L:
            if item in text:
                count += 1
                if count>=n:
                    return True
        return False
        
    
class ExpKnowClassifier(LabelClassifier):
    def __init__(self,excelpath = None):
        LabelClassifier.__init__(self)
        
class OneVsRestSGDClassifier(LabelClassifier):

    def __init__(self,f_dim=100,ft_iters=20,update_iters=100,
                 label_dict_path='data/labels.txt'):

        LabelClassifier.__init__(self,label_dict_path)
        self.f_dim = f_dim # dimension of word feature vector
        self.ft_iters = ft_iters
        self.update_iters =update_iters

        self.ft_model = FastText(min_count=1, size=self.f_dim)
        self.clf = OneVsRestClassifier( SGDClassifier(loss='modified_huber' ,
                                      class_weight={0:0.4,1:0.6},
                                      penalty='l2' ,warm_start=False,
                                      random_state=1))

    def init_fasttext(self,model_path=None,train_data=None ):
        """
        if train_data is provided, train a new fasttext model;
        otherwise, load it from the given path

        --------
        Parameter:

            model_path: fasttext model prefix

            train_data: a list of tokenized sentences. if not provided,
                will try to load existing model from model_path

        """

        if not train_data and model_path and os.path.isfile(model_path):
            #=== load exisitng model ====
            print('loading fasttext model from',model_path)
            self.ft_model = FastText.load(model_path)

        elif train_data:
            #=== train fast text model ====
            # if train_data is not a list of list, split each sentence
            # into list of words
            print('training fasttext model from scratch...' )
            train_data = [re.split(',| ',r) if (not isinstance(r,list)) else r\
                          for  r in  train_data ]

            self.ft_model.build_vocab(train_data)
            self.ft_model.train(train_data, total_examples=len(train_data) ,
                               epochs = self.ft_iters)
            if model_path:
                self.ft_model.save(model_path,separately=[])
        else:
            #=== no train data and no model path provided
            raise TrainDataException('Error building fasttext model. No data/model provided.')


    def div_norm(self,x):
        norm_value = np.sqrt(np.sum(x**2)) #l2norm
        if norm_value > 0:
            return x * ( 1.0 / norm_value)
        else:
            return x

    def sentence_to_vec(self, words):
        """ generating embedding by summing up normalized
        word embeddings

        --------
        Parameter:
            words: a list of words or a string representation of a sentence
            (seperated by space or ',' )

        Return:
            sentence embedding matrix of size len(words) x f_dim

        """
        if  not isinstance( words ,list):
            words =  re.split(',| ', words  )

        vecs = np.zeros( (len(words),self.f_dim) )
        for i,word in enumerate(words):
            v = self.ft_model.wv.get_vector(word)
            vecs[i] = self.div_norm(v)
        return np.mean(vecs,axis=0)

    def to_vec(self,data):
        """ batch computation of sentence embeddings """
        vec = np.zeros( (len(data),self.f_dim))
        for i,sentence in enumerate(data):
            vec[i] = self.sentence_to_vec(sentence)

        return vec


    def train(self, train_data, train_label):
        """
        offline training of the SGD classifier

        --------
        Parameters:

            train_data: a list of tokenized sentences. Each sentence is either
                a string deliminated by comma or space, or a list of words.

            train_label: a list of labels. Each label is a string deliminated
                by comma or space.
        Return:

            X: sentence embedding matrix of size len(train_data) x f_dim
            Y: binary label matrix of size len(train_data) x #_classes
        """
        print('training multilabel classifier on %d samples...' % len(train_data))
        Y = np.zeros((len(train_label), len(self.labeldict) ) )
        for i, labels in enumerate(train_label):
            label_list = re.split(',| ',labels)

            for l in label_list:
                if l:
	                Y[i,self.labeldictR[l]]=1

        # add dummy sample to classes that do not have samples
        indices = np.where(np.sum(Y,axis=0)==0)[0]
        Y_new = np.zeros( (len(indices),Y.shape[1] ))
        for i,id in enumerate(indices):
            train_data.append([self.labeldict[id]] )
            Y_new[i,id]=1
        Y=np.vstack((Y, Y_new ) )



        X = self.to_vec(train_data)
        self.clf.fit(X,Y)
        return X,Y



    def train_update(self, train_data, train_label ):
        """
        online training of the SGD classifier

        --------
        Parameters: see train()

        """
        Y = np.zeros((len(train_label), len(self.labeldict) ) )
        X = self.to_vec(train_data)
        for i, labels in enumerate(train_label):
            label_list = re.split(',| ',labels)
            for l in label_list:
                if l :
                    Y[i,self.labeldictR[l]]=1
        for i in range(self.update_iters):
            self.clf.partial_fit(X, Y )
        return X,Y

    def classify(self,string):
        """
        predict the labels of a tokenized sentence

        --------
        Parameters:
            string: string delimited by comma or space, or a list of words

        Return:
            labels: a list of predicted labels

        """
        X = self.to_vec( [string ] )
        Y = self.clf.predict( X)
        #print('class probability',self.clf.predict_proba(X) )
        labels = [ self.labeldict[id] for id in np.nonzero(Y[0])[0] ]


        return labels

    def save_clf(self,filename):
        print('writing classification model to',filename,'...')
        with open(filename,'wb') as f:
            pickle.dump(self.clf ,f)

    def load_clf(self,filename):
        print('loading classification model from',filename,'...')
        with open(filename,'rb') as f:
            self.clf = pickle.load(f)

class WordMoverKNNClassifier(LabelClassifier):
    """
    a knn classifier based on word mover distance between sentences

    """
    pass

if __name__ == '__main__':
    import time
    text1 = '清华大学深圳研究院电子通信硕士'
    text2 = '深圳市罗湖区街道派出所民警'
    text3 = '深圳市交通运输委员会福田交通运输局副局长'

    t0 = time.time()
    label = ExpRuleClassifier()
    print('Obj building Consuming:',time.time()-t0,'s')

    print('\nSample Text:',text1)
    t0 = time.time()
    print(label.classify(text1,True))
    print('Time Consuming:',time.time()-t0,'s')

    print('\nSample Text:',text2)
    t1 = time.time()
    print(label.classify(text2,True))
    print('Time Consuming:',time.time()-t1,'s')

    print('\nSample Text:',text3)
    t1 = time.time()
    print(label.classify(text3,True))
    print('Time Consuming:',time.time()-t1,'s')