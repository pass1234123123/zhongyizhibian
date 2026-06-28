import os
c = open('ai_processor.py','r',encoding='utf-8').read()
c = c.replace(chr(92)+chr(96), chr(96))
open('ai_processor.py','w',encoding='utf-8').write(c)
print('fixed')
