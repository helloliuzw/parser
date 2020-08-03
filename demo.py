from labeler.label_classifier import ExpRuleClassifier
import os
import time

#print('hello:',os.getcwd())
'''
'''
text1 = '清华大学深圳研究院硕士'
text2 = '深圳市罗湖区街道派出所民警'

label = ExpRuleClassifier()
liu1 = label.groupclassify('school',text1)
print('\nSample Text:',text1)
#print(liu1)
t0 = time.time()
print(label.classify(text1))
print('Time Consuming:',time.time()-t0,'s')
print('\nSample Text:',text2)
t1 = time.time()
print(label.classify(text2))
print('Time Consuming:',time.time()-t1,'s')

# debug