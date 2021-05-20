#!/usr/bin/env python3
#coding=utf-8
import numpy as np
import json
import re,os,pickle
from graphviz import Digraph

location = os.path.abspath(os.path.dirname(__file__))

class logictree():
    def __init__(self,ltree={},result_dict={}):
        self.tree = ltree
        self.result_dict = result_dict
    def __call__(self,ltree):
        self.tree = ltree
    def update_basicdict(self,resD):
        self.result_dict = resD
        
    def getvalue(self,nodeid='0'):
        # print(nodeid)
        node = self.tree[nodeid]
        if node[2] == False:
            f = lambda x:x
        else:
            f = lambda x:(not x)
        if node[3]==None:
            return f(self.result_dict[node[1]])
        if node[3]=='and':
            for id in node[1]:
                if self.getvalue(str(id))==False:
                    return f(False)
            return f(True)
        if node[3]=='or':
            for id in node[1]:
                if self.getvalue(str(id))==True:
                    return f(True)
            return f(False)
        return None
    def show(self):
        g = Digraph(name='logic tree',format="png")
        #g.attr('node',shape='doublecircle')
        for id in self.tree.keys():
            node = self.tree[str(id)]
            if node[3]==None:
                g.node(name=str(id),label=node[1],fontname="Microsoft YaHei")
            else:
                g.node(name=str(id),label=node[3],fontname="Microsoft YaHei")
        #g.attr('node', shape='circle')
        for outid in self.tree.keys():
            if self.tree[outid][3] == None:
                continue
            for inid in self.tree[outid][1]:
                cl = 'green' if self.tree[str(inid)][2]==False else 'red'
                g.edge(str(inid),str(outid),color=cl)
        g.node(name='output',fontname="Microsoft YaHei")
        cl = 'green' if self.tree['0'][2]==False else 'red'
        g.edge('0','output',color=cl)
        # g.view()
        return g
    
    def tree2exp(self,dictname='result_dict',nodeid='0'):
        node = self.tree[nodeid]
        if node[2] == False:
            f = lambda x:x
        else:
            f = lambda x:('(not '+x+')')
        if node[3]==None:
            exp = dictname+'["'+node[1]+'"]'
            return f(exp)
        unit = [self.tree2exp(dictname,str(id)) for id in node[1]]
        exp = (' '+node[3]+' ').join(unit)
        exp = '('+exp+')'
        return f(exp)
    
    def exp2tree(self,expression):
        print('Warning:请合理使用小括号，同一小括号内，and、or、not三类关键字仅出现其中一类；not运算符请贴近底层条件')
        print('正确实例 ：("教育" and (not "科技") and ("经济" or "行政"))')
        print('错误示例1：("教育" and not "科技" and ("经济" or "行政"))')
        print('错误示例2：("教育" and (not "科技") and (("经济" or "行政")))')
        if not expression.startswith('('):
            expression = '('+expression+')'
        Llist = []
        grade,maxgrade = 0,0
        allnode = []
        for i,ch in enumerate(expression):
            if ch=='(':
                Llist.append(i)
                grade += 1
            elif ch==')':
                maxgrade = max(grade,maxgrade)
                allnode.append([grade,expression[Llist.pop():i+1]])
                grade -= 1
        allnode.reverse()
        # allnode get, now depth tree
        depthtree = {}
        for i in range(1,maxgrade+1):
            depthtree[str(i)] = []
        for i,node in enumerate(allnode):
            depthtree[str(node[0])].append([i,[],node[1]])
        # depthtree
        for dep in range(1,maxgrade):
            for par in depthtree[str(dep)]:
                for chi in depthtree[str(dep+1)]:
                    if chi[2] in par[2]:
                        par[1].append(chi[0])
                        par[2] = par[2].replace(chi[2],'',1)             
        # Real tree
        nodelist = []
        for L in depthtree.values():
            nodelist.extend(L)
        nodenum = len(nodelist)
        tree = {}
        for node in nodelist:
            node[2] = node[2][1:-1]
            parsed = node[2].split()
            notflag = False
            for operator in ['and','or']:
                if operator in parsed:
                    logic = operator
                    childL = node[2].split(' '+operator+' ')
            if 'not' in parsed:
                logic = 'None'
                notflag = True
                childL = node[2].split('not ')
            childL = [item.strip() for item in childL]
            childL = list(set(childL))
            if '' in childL:
                childL.remove('')
            if notflag == True:
                tree[str(node[0])] = [True,childL[0],notflag,None]
                continue
            tree[str(node[0])] = [True,node[1],notflag,logic]
            for source in childL:
                tree[str(node[0])][1].append(nodenum)
                tree[str(nodenum)] = [True,source,notflag,None]
                nodenum += 1
        return tree
    
if __name__ == '__main__':
    import time
    tree = {'0':[True,[1,2],False,'and'],
        '1':[True,[3,4,5],False,'or'],
        '2':[True,'科技技术',False,None],
        '3':[True,'一般院校',False,None],
        '4':[True,'双一流大学',False,None],
        '5':[True,'海外名校',False,None]}
    result_d = {'一般院校':False,'双一流大学':False,'海外名校':True,'科技技术':True,'深圳':True}
    ltree = logictree(tree,result_d)
    print('Final:',ltree.getvalue())
    print('Python Expression:',ltree.tree2exp())
    ltree.show()