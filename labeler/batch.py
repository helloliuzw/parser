#!/usr/bin/env python3
#coding=utf-8
import os
import sys

from Career_Platform.octree.OCtree import CTree
from Career_Platform.parser.catalog import ResumeFileIO
from Career_Platform.parser.tokenizer import JiebaTokenizer
from treelib import Node, Tree
import numpy as np

'''
-load raw file, perform processing and extract sequences

-for each experience, run jieba to perform initial parsing

-call oc tree to generate sequences

'''

class BatchGenerator:
    # initilize resume catalog from database
    def __init__(self,catalog):
        self.catalog = catalog

    def set_batch_ids(self):
        pass

class OCTreeBatchGenerator(BatchGenerator):


    def __init__(self,catalog,tree=None):
        BatchGenerator.__init__(self,catalog)

        # generate OC tree from tokenized entries
        if tree:
            self.tree = tree
        else:
            self.tree = CTree()
            self.tree.build_tree(self.catalog.get_all_parsed())
            self.tree.compress_tree()
        self.entry_node_map={}
        self.node_score_map={}

        self.initialize_oc_maps()


    def initialize_oc_maps(self):

        # for each entry  catalog, make uid, rid - nodeid correspondence
        matched = 0
        for uid,user in enumerate(self.catalog.users):
            for rid,exp in enumerate(user.work_exp):
                text =  exp.segmented.replace(" ","")
                n,is_success =self.tree.greedy_prefix_match( text)
                if is_success:
                    matched+=1

                n.data.resume_ids.append((uid,rid))
                self.entry_node_map[(uid,rid)] ={'nid':  n.data.id }

        self.tree.compute_node_scores()

        for n in self.tree.all_nodes():
            self.node_score_map[n.data.id] = {'score':n.data.score,'depth':self.tree.depth(n) }

    def set_batch_ids(self):
        # sort nodes by (score-1)^(depth-1)
        sorted_map = sorted(self.node_score_map.items(),
                            key=lambda x:(x[1]['score']-1)**( x[1]['depth']-1),reverse=True)
        #offset=0
        entries_per_batch = 10
        counter = 0
        for rank, (nid,value) in enumerate( sorted_map  ):
            print(self.tree[nid].data.name,'depth=', value['depth'],'score=',value['score'])
            descendents = self.tree.expand_tree(nid)
            resume_ids = []
            for d  in descendents:
                resume_ids += self.tree.get_node(d).data.resume_ids
            for j,(uid,rid) in  enumerate(resume_ids):
                exp= self.catalog.users[uid].work_exp[rid]
                #rank = sorted_map.index((nid,value))
                #exp.batch_id =
                self.entry_node_map[(  uid,rid)]['rank'] = rank
                #mini_batch = j //entries_per_batch
                if exp.batch_id == None:
                    exp.batch_id = counter//entries_per_batch
                    #exp.batch_id =  offset +mini_batch

                    print('index:',rank,'m_batch', exp.batch_id ,'seg',exp.segmented )
                    counter+=1
            #offset += int(np.ceil(len(resume_ids)/entries_per_batch))
