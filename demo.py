from labeler.label_classifier import ExpRuleClassifier
import os
import time

#print('hello, here is:',os.getcwd())

text1 = '清华大学深圳研究院电子通信硕士'
text2 = '深圳市罗湖区街道派出所民警'

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
