#!/usr/bin/python
# python file to get headfile function propertype 

import os
import sys
from subprocess import check_output
from collections import OrderedDict

SOURCE_PATH0 = os.environ['HOME']+'/SOURCE/linux-3.5.6/'
SOURCE_PATH1 = os.environ['HOME']+'/SOURCE/linux-3.8.13/'
TARGET_PATH = 'target/'
CURRENT_PATH = os.getcwd()
CTAGSFILE_EXT = '_ctags.txt'
HEADERFILE_EXT = '_headfile.txt'

def printDictMethod(dictname,filename):
  with open(filename,'w') as out:
    for (k,v) in dictname.items():
      print >> out,k,v

def getSrcPath(vers):  
  if (cmp(vers,'0') == 0):
    return SOURCE_PATH0
  else:
    return SOURCE_PATH1

def reviseCtagsFile(vers):
  filename = TARGET_PATH+'v'+vers+CTAGSFILE_EXT
  SOURCE_PATH = getSrcPath(vers)
  print filename,'file is reviseding ...'
  
  ctags_dict = OrderedDict()
  with open(filename) as fp:
    sline = fp.readline()
    while sline:
      if (sline !='\n' ):
        tlist = sline.split()
        name = tlist[0]
        _type = tlist[1]
        rows = tlist[2];rowstart = rows
        _file = tlist[3][len(SOURCE_PATH):]
        state_list = tlist[4:]
        if len(state_list)==0:
          print 'state_list==0',sline
          break
        fileph = tlist[3]
        if _type in ('macro','function','prototype'):
          statement = state_list[0]
          for slt in state_list[1:]:	#handle more space
            if statement.endswith(','):
              statement = statement + slt
            else:
              statement = statement +' '+ slt
          statement = statement.split('/*')[0].strip() #del notes
          while statement.endswith(','):
            rows = int(rows) + 1
            temp=check_output(['sed','-n',str(rows)+'p',fileph]).strip()
            statement = statement + temp
          while(statement.endswith('\\')):
            rows = int(rows) + 1
            temp=check_output(['sed','-n',str(rows)+'p',fileph]).strip()
            statement = statement.rstrip('\\').rstrip()+' '+ temp
          ctags_dict[name] = ' '+ _type+'  '+_file+'  '+rowstart+'  '+statement
        
        elif _type in ('struct','enum','union'):
          statement = ' '.join(state_list).split('/*')[0].strip()
          statement = statement.split('/*')[0].strip() #del notes
          aliasname_list = []
          if not statement.endswith(';'): # not one line decl
		        openbrace_unmatch = 0	# open brace-->{ , close brace-->}
		        openbrace_unmatch += statement.count('{')
		        temp_dict = OrderedDict()
		        rowend = int(rows) + 1
		        temp=check_output(['sed','-n',str(rowend)+'p',fileph]).strip()
		        while True:  # find end rows of struct
		          openbrace_unmatch += temp.count('{')
		          openbrace_unmatch -= temp.count('}')
		          if openbrace_unmatch == 0:
		            break
		          temp = temp.split('/*')[0].strip()
		          temp = temp.split('{')[0].strip()
		          locNo = rowend - 1
		          lastline = check_output(['sed','-n',str(locNo)+'p',fileph]).strip()
		          if cmp(lastline,'')==0:
		            locNo = rowend-2
		          if temp in ('union','struct','enum'): # recored unamed/named struct member start flag
		            if not temp.endswith('{'):
		              temp = temp + ' {'
		            temp_dict[locNo] = temp
		          elif temp.endswith('};'): # recored named struct member end flag
		            temp_dict[locNo] = temp
		          else:
		            pass
		          rowend = int(rowend) + 1 # refresh end rows of struct
		          temp=check_output(['sed','-n',str(rowend)+'p',fileph]).strip()
		        endstmt = temp.split('/*')[0].strip() # end flag of struct
		        
		        if not endstmt.endswith('};') and endstmt.endswith(';'):#get alias name of data struct 
		          i = 0;
		          for cstr in endstmt[::-1]:
		            if cstr == '}':
		              break
		            i += 1
		          aliasname = endstmt[(len(endstmt)-i):-1].strip()
		          if '(' not in aliasname:
		            aliasname_list = aliasname.split(',')
		        
		        if '{' not in statement:
		          statement = statement + ' {'
		        sline2 = fp.readline()
		        while sline2 and (sline2 != '\n'):
		          rows = sline2.split()[2]
		          if int(rows) > int(rowend):
		            break
		          state_list2 = sline2.split()[4:]
		          statement2 = ' '.join(state_list2).split('/*')[0].strip()
		          while statement2.endswith(',') and ('member' in sline2):  #enumerator endswith ',' so exclude it
		          	rows = int(rows) + 1
		          	temp=check_output(['sed','-n',str(rows)+'p',fileph]).split('/*')[0].strip()
		          	statement2 = statement2 + temp
		          if not statement.endswith(statement2):
		            statement = statement +' '+ statement2  # merge statement
		          if int(rows) in temp_dict: #mod struct member struct/union/enum start and end
		            if not statement.endswith(temp_dict[int(rows)]):
		              statement = statement +' '+ temp_dict[int(rows)]
		          
		          sline2 = fp.readline() # read next line
		        if not statement.endswith(endstmt):
		          statement = statement +' '+ endstmt 
		        fp.seek(-len(sline2),1); #back to last line    
          else:
            if not statement.endswith('};') and endstmt.endswith(';'):
              i = 0;
              for cstr in statement[::-1]:
                if cstr == '}':
                  break
                i += 1
              aliasname = statement[(len(statement)-i):-1].strip()
              if '(' not in aliasname:
                aliasname_list = aliasname.split(',')
          
          ctags_dict[name] = ' '+ _type+'  '+_file+'  '+rowstart+'  '+statement
          if len(aliasname_list)>0:
            for vname in aliasname_list:
              if '____' not in vname:
                vname = vname.split()[-1]
                ctags_dict[vname] = ' '+ _type+'  '+_file+'  '+rowstart+'  '+statement
        elif _type in ('member','enumerator'): #typedef struct,typedef enum,struct class
          statement = ' '.join(state_list).split('/*')[0].strip()
          statement = statement.split('/*')[0].strip() #del notes
          temp_dict = OrderedDict()
          namelist = []
          temp = statement
          while True: # find start rows of data type
            if '{' in temp: 
              if ('struct' not in temp) and ('enum' not in temp) and ('union' not in temp):
                rowstart = int(rowstart) - 1
                temp=check_output(['sed','-n',str(rowstart)+'p',fileph]).split('/*')[0].strip() 
              break
            rowstart = int(rowstart) - 1
            temp=check_output(['sed','-n',str(rowstart)+'p',fileph]).split('/*')[0].strip()  
          startstmt = temp.split('/*')[0].strip() # start flag
          
          rowend = rowstart
          if not startstmt.endswith(';'):
            openbrace_unmatch = 0
            openbrace_unmatch += startstmt.count('{')
            rowend = rowend + 1
            temp=check_output(['sed','-n',str(rowend)+'p',fileph]).strip()
            while True:  # find end
              openbrace_unmatch += temp.count('{')
              openbrace_unmatch -= temp.count('}')
              if openbrace_unmatch == 0:
                break
              temp = temp.split('/*')[0].strip()
              temp = temp.split('{')[0].strip()
              locNo = rowend - 1
              lastline = check_output(['sed','-n',str(locNo)+'p',fileph]).strip()
              if cmp(lastline,'')==0:
                locNo = rowend-2
              if temp in ('union','struct','enum'): # recored unamed/named struct member start flag
                if not temp.endswith('{'):
                  temp = temp + ' {'
                temp_dict[locNo] = temp
              elif temp.endswith('};'): # recored named struct member end flag
                temp_dict[locNo] = temp
              else:
                pass
              rowend = rowend + 1
              temp=check_output(['sed','-n',str(rowend)+'p',fileph]).strip()
            endstmt = temp.split('/*')[0].strip() # end flag
            
            if not ('typedef' in startstmt):
              _type = startstmt.split()[0]
            else:
              _type = startstmt.split()[1]
            
            if not endstmt.endswith('};') and endstmt.endswith(';'):
              i = 0;
              for cstr in endstmt[::-1]:
                if cstr == '}':
                  break
                i += 1
              name = endstmt[(len(endstmt)-i):-1].strip()
              if '(' not in name:
                namelist = name.split(',')
            else:
              name = 'unamed-'+_type
            
            if '{' not in startstmt:
              startstmt = startstmt + ' {'
            if int(rows) <= int(rowend):
              statement = startstmt +' '+ statement
            sline2 = fp.readline()
            while sline2 and (sline2 != '\n'):
              rows = sline2.split()[2]
              if int(rows) > int(rowend):
                break
              state_list2 = sline2.split()[4:]
              statement2 = ' '.join(state_list2).split('/*')[0].strip()
              while statement2.endswith(',') and ('member' in sline2):  #enumerator endswith ',' so exclude it
                rows = int(rows) + 1
                temp=check_output(['sed','-n',str(rows)+'p',fileph]).split('/*')[0].strip()
                statement2 = statement2 + temp
              if not statement.endswith(statement2):
                statement = statement +' '+ statement2  # merge statement
              
              if int(rows) in temp_dict: #mod struct member struct/union/enum start and end
                if not statement.endswith(temp_dict[int(rows)]):
                  statement = statement +' '+ temp_dict[int(rows)]
              
              sline2 = fp.readline() # read next line    
            if not statement.endswith(endstmt):
              statement = statement +' '+ endstmt
            fp.seek(-len(sline2),1); #back to last line  
          else:
            if 'struct' in statement:
              _type = 'struct'
            elif 'enum' in statement:
              _type = 'enum'
            elif 'union' in statement:
              _type = 'union'
            else:
              _type = 'typedef'
            
            if statement.endswith('};'):
              name = 'unamed-' +_type
            elif endstmt.endswith(';'):
              i = 0;
              for cstr in statement[::-1]:
                if cstr == '}':
                  break
                i += 1
              name = statement[(len(statement)-i):-1].strip()
              if '(' not in name:
                namelist = name.split(',')
            else:
              pass
          if 'unamed' not in name:
            for vname in namelist:
              if '____' not in vname:
                vname = vname.split()[-1]
                ctags_dict[vname] = ' '+ _type+'  '+_file+'  '+str(rowstart)+'  '+statement
        else: #other typedef
          pass
      sline = fp.readline()# move file pointer
  printDictMethod(ctags_dict,filename)
  print filename,'file is revised successful!'

def getCtagsFile(vers):
  hdFileTxt = TARGET_PATH+'v'+vers+HEADERFILE_EXT
  outCtagsPath = TARGET_PATH+'v'+vers+CTAGSFILE_EXT
  SOURCE_PATH = getSrcPath(vers)
  assert os.path.isfile(hdFileTxt),'input file '+hdFileTxt+' not found!\n'
  
  with open(outCtagsPath,'w') as out:
    with open(hdFileTxt) as fp:
      hdFileName = fp.readline();
      while hdFileName:
        filepath1 = SOURCE_PATH+'include/'+hdFileName[:-1]
        filepath2 = SOURCE_PATH+'arch/x86/include/'+hdFileName[:-1]
        filepath3 = SOURCE_PATH+'include/uapi/'+hdFileName[:-1]
        filepath4 = SOURCE_PATH+'arch/x86/include/uapi/'+hdFileName[:-1]
        if os.path.isfile(filepath1):
          filepath = filepath1
        elif os.path.isfile(filepath2):
          filepath = filepath2
        elif os.path.isfile(filepath3):
          filepath = filepath3
        elif os.path.isfile(filepath4):
          filepath = filepath4
        else:
          filepath = ""
          print 'header file '+hdFileName[:-1]+' in',SOURCE_PATH,' not found!'
        if cmp(filepath,"")!= 0:
		      cmd_string = ['ctags','-xu','--c-kinds=+p',filepath] #,'--extra=+q'
		      hdFnd_list = check_output(cmd_string).rstrip('\0').split('\0')
		      for hflist in hdFnd_list:
		        print >> out,hflist
        hdFileName = fp.readline()
  print outCtagsPath,'file is generated successful!'

def reviseHdFile(vers):
  outpath = TARGET_PATH+'v'+vers+'_headfile.txt'
  inpath = TARGET_PATH+'sfile_list.txt'
  str1 = 'arch/x86/include/'
  str2 = 'include/'
  
  hfile_list = [] #
  with open(outpath) as fp:
    for line in fp.readlines():
      line = line.rstrip('\n')
      hfile_list.append(line)
  with open(inpath) as fp:
    for line in fp.readlines():
      line = line.rstrip('\n')
      if line.startswith(str1):
        line = line[len(str1):]
      else:
        line = line[len(str2):] 
      if line not in hfile_list:
        hfile_list.append(line)
  with open(outpath,'w') as out:
    for tlist in hfile_list:
      print >> out,tlist

  print 'revise',outpath,'successful.'

def main():
    print '\npython file:',sys.argv[0],'running...'
    #reviseHdFile('0')
    #reviseHdFile('1')
    getCtagsFile('0')
    getCtagsFile('1')
    reviseCtagsFile('0')
    reviseCtagsFile('1')
    print 'Done\n'
  
if __name__ == '__main__':
    main()
