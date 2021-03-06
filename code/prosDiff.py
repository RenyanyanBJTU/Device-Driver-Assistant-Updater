#!/usr/bin/python
# python file to get assistant infomation

import os
import sys
import commands
from subprocess import check_output
from collections import OrderedDict

from display import * #show result

EXT0 = '.ind' # AST file
EXT2 = '.int' #interface file
SOURCE_PATH0 = os.environ['HOME']+'/SOURCE/linux-3.5.6/'
SOURCE_PATH1 = os.environ['HOME']+'/SOURCE/linux-3.8.13/'
TARGET_PATH = 'target/' #path to save target file
FILE_TO_PROCESS = sys.argv[1]
CTAGSFILE_EXT = '_ctags.txt'
LOGERR = 'assitLog/'+os.path.basename(FILE_TO_PROCESS)+'_assitLog.txt'

def printDictMethod(dictname,filename):
  with open(filename,'w') as out:
    for (k,v) in dictname.items():
      print >> out,k,v

def printToFile(fnFile_dict,fnCall_dict,fcFile_dict):
  
  fnFilePath = TARGET_PATH + 'fnFile_dictTemp.txt'
  printDictMethod(fnFile_dict,fnFilePath)
  print 'generated file:',fnFilePath
  
  fnCallPath = TARGET_PATH + 'fnCall_dictTemp.txt'
  with open(fnCallPath,'w') as out:
		for fnName,fcName_dict in fnCall_dict.items():
		  print >> out,fnName
		  for fcName,fcLoc_list in fcName_dict.items():
		    print >> out,'  '+fcName
		    for fcLoc in fcLoc_list:
		      print >> out,'    '+fcLoc
  print 'generated file:',fnCallPath
  
  fcFilePath = TARGET_PATH + 'fcFile_dictTemp.txt'
  printDictMethod(fcFile_dict,fcFilePath)
  print 'generated file:',fcFilePath

def printDataStruct(dataStructCall_dict):
  dataStructCallPath = TARGET_PATH + 'dataStructCall_dictTemp.txt'
  count = 0
  with open(dataStructCallPath,'w') as out:
    for dataName,fnName_dict in dataStructCall_dict.items():
      print >> out,dataName
      for fnName,dcLoc_list in fnName_dict.items():
        print >> out,'  '+fnName
        for dcLoc in dcLoc_list:
          print >> out, '    '+dcLoc
          count +=1
  print 'dataStructCall count-->',count
  print 'generated file:',dataStructCallPath
  
def getDataStructCall(filename):
  # get dataStruct-Call-dict as {'dataName':{'fnName':['loc1','loc2',..]}}
  crpath=TARGET_PATH+'dataStruct_list.txt'
  dataStructCall_dict = OrderedDict()
  with open(crpath) as fp:
    sline=fp.readline();
    while sline:
      fnName,dataName,dcLoc,dataType=sline.split()
      if dcLoc.split(':')[0].endswith(os.path.basename(filename)):
        if dataName not in dataStructCall_dict:
          dataStructCall_dict[dataName] = OrderedDict()
          dataStructCall_dict[dataName][fnName] = [dcLoc]
        else:
          if fnName not in dataStructCall_dict[dataName]:
            dataStructCall_dict[dataName][fnName] = [dcLoc]
          else:
            dataStructCall_dict[dataName][fnName].append(dcLoc)
      else:
        pass
      sline=fp.readline();    
  #print 'test--------------'
  printDataStruct(dataStructCall_dict)
  print 'dataStructCall name count-->',len(dataStructCall_dict.keys())
  return dataStructCall_dict

def getFuncAndFile():
  #get function-file like {'fnName':['file:sloc','eloc','.ind--lineNo']}}
  #V0_MANIFEST
  rpath = check_output(['find',TARGET_PATH,'-name','*'+EXT2]).rstrip('\n')
  fnFile_dict = OrderedDict()
  linec = 0
  with open(rpath) as fp:
    sline=fp.readline();linec += 1
    while sline:    
      left,right = sline.split('(')
      fnName = left.strip().split()[-1]
      rright = right.split(')')[-1]
      fnFile = rright.strip().split()[:-1]
      if fnName not in fnFile_dict:
        fnFile_dict[fnName] = fnFile
      sline=fp.readline();linec += 1
  return fnFile_dict
 
def getFuncCallDict(filename):
  #get function-call-dict like {'fdA':{'fcB':['loc1','loc2',..]}}
  #filename = os.path.basename(path)[:-len(EXT2)]
  crpath=TARGET_PATH+'cm_list.txt'
  fnCall_dict = OrderedDict()
  with open(crpath) as fp:
    sline=fp.readline();
    while sline:
      fnName,fcName,fcLoc=sline.split()
      if fcLoc.split(':')[0].endswith(os.path.basename(filename)):
		    if fcName not in fnCall_dict:
		      fnCall_dict[fcName]=OrderedDict()
		      fnCall_dict[fcName][fnName]=[fcLoc]
		    else:
		      if fnName not in fnCall_dict[fcName]:
		        fnCall_dict[fcName][fnName]=[fcLoc]
		      else:
		        fnCall_dict[fcName][fnName].append(fcLoc)
      sline=fp.readline();
  print 'functionCall name count-->',len(fnCall_dict.keys())
  return fnCall_dict

def getHeadFileList():
  headFilePath = TARGET_PATH + 'headfile.txt'
  headfile_list = []
  with open(headFilePath) as fp:
    sline = fp.readline()
    while sline:
      sline = sline.strip('\n')
      headfile_list.append(sline)
      sline = fp.readline()
  
  return headfile_list

def getCtagsFileDict(vers):
  filename = TARGET_PATH+'v'+vers+CTAGSFILE_EXT
  ctags_dict = OrderedDict()
  with open(filename) as fp:
    sline = fp.readline()
    while sline:
      if (sline !='\n' ):
        tlist = sline.split()
        name = tlist[0]
        _type = tlist[1]
        _file = tlist[2]
        rows = tlist[3]
        statement = ' '.join(tlist[4:])
        #if _type in ('macro','function','prototype'):
        ctags_dict[name] = [_type,_file,rows,statement]
      sline = fp.readline()
  return ctags_dict

def code_Diff():
  v0ctags_dict = getCtagsFileDict('0')
  v1ctags_dict = getCtagsFileDict('1') 
  diffLog_dict = OrderedDict()
  for k,vlist in v0ctags_dict.items():
    v0_type,v0_file,v0_rows,v0_state = vlist[0:]
    if v0_type not in ('typedef'): #('macro','function','prototype'):
      if k in v1ctags_dict:# if exist
        v1_type,v1_file,v1_rows,v1_state = v1ctags_dict[k]
        if cmp(v0_file,v1_file)==0:       
          if (cmp(v0_type,v1_type)==0) and (cmp(v0_state,v1_state)==0): 
            #nothing changed
            diffLog_dict[k] = ['Not']
            del v1ctags_dict[k]
          else:  #decl changed
            _type = v0_type
            if cmp(v0_type,v1_type)!=0: #type
              _type = _type+'-->'+v1_type
            diffLog_dict[k] = ['Mod',_type,v0_file,v0_state,v1_state]
            del v1ctags_dict[k]
        else:
          if (cmp(v0_type,v1_type)==0) and (cmp(v0_state,v1_state)==0):
            #just file changed
            diffLog_dict[k] = ['Mov',v0_type,v0_file,v1_file,v1_state]
            del v1ctags_dict[k]
          else: #all changed(file,decl)
            _file = v0_file+'-->'+v1_file #file
            _type = v0_type
            if cmp(v0_type,v1_type)!=0:   #type
              _type = _type+'-->'+v1_type
            diffLog_dict[k] = ['All',_type,_file,v0_state,v1_state]
            del v1ctags_dict[k]
      else:  # not exist-->deleted
        diffLog_dict[k] = ['Del',v0_type,v0_file,v0_state]  
    else:# typedef others
      pass
    
  if len(v1ctags_dict)>0:  # add changed
    for k,vlist in v1ctags_dict.items():
      diffLog_dict[k] = ['Add'] + vlist 
  #print test start--------------------------------
  filename = 'diffLog.txt'
  with open(filename,'w') as out:
		for k,vlist in diffLog_dict.items():  
			if vlist[0] not in ('Not'):
				diff_type,_type,_file = vlist[0:3]
				print >> out,'\n',k,'\t( diff_type: '+diff_type,'type: '+_type,'file: '+_file,')'
				print >> out,'\t--',vlist[3]
				if cmp(diff_type,'Del')!=0:
					print >> out,'\t++',vlist[4]
				print >> out,""
  print '\nprint test start--------------------------'
  print filename,'file generated successful!'
  print 'print test end--------------------------\n'
  #print test end--------------------------------
  return diffLog_dict

def classDiffLog(diffLog_dict):
  Alevel_dict = OrderedDict() # impact
  Blevel_dict = OrderedDict() # impact value
  Clevel_dict = OrderedDict() # little impact
  for k,vlist in diffLog_dict.items():
    diff_type = vlist[0]
    if diff_type in ('Not','Mov'):
      pass
    elif cmp(diff_type,'Del')==0:
      Alevel_dict[k] = diffLog_dict[k]
    elif diff_type in ('Mod','All'):  
      _type,_file,v0_state,v1_state = vlist[1:]
      if '-->' not in _type: #type not changed
        if cmp(_type,'macro')==0:
          macor_name_list = v0_state.split()
          if('(' in macor_name_list[1]): # macro with parameter
            state0 = v0_state.split(k)[1].split(')')[0]+')'
            state1 = v1_state.split(k)[1].split(')')[0]+')'
            if(cmp(state0,state1)==0):
              Blevel_dict[k] = diffLog_dict[k]
            else:
              Alevel_dict[k] = diffLog_dict[k]
          else: # macro without parameter
            Blevel_dict[k] = diffLog_dict[k]
        elif _type in ('struct','union','enum'): # data struct
          Blevel_dict[k] = diffLog_dict[k]
        else:
          Alevel_dict[k] = diffLog_dict[k]
      else: #type changed,but defination may not changed
        state0 = v0_state.split(k)[1].rstrip(';')
        state1 = v1_state.split(k)[1].rstrip(';')
        if cmp(state0,state1)==0:
          Clevel_dict[k] = diffLog_dict[k]
        else:
          Alevel_dict[k] = diffLog_dict[k]
    else: # cmp(diff_type,'Add')==0
      pass 
  return Alevel_dict,Blevel_dict,Clevel_dict

def prosFuncTargetFile():
  #handle function-call-relation
  fnFile_dict = getFuncAndFile()
  fnCall_dict = getFuncCallDict(FILE_TO_PROCESS)
  v0ctags_dict = getCtagsFileDict('0')
  
  fcFile_dict = OrderedDict()
  for fnName in fnCall_dict.keys():
    if fnName in v0ctags_dict:
      fcFile_dict[fnName] = v0ctags_dict[fnName]
    elif fnName in fnFile_dict:  
      # macro define function
      tlist = fnFile_dict[fnName][0].split(':')
      fileph = SOURCE_PATH0+tlist[0]
      rows =  tlist[1]
      Sno = tlist[1]+':'+tlist[2]
      Eno = fnFile_dict[fnName][1]
      tstr=check_output(['sed','-n',rows+'p',fileph]).strip()
      if cmp(Sno,Eno)==0:
        fcFile_dict[fnName] =['macfun'] + tlist[:-1] + [tstr]
      else:
        fcFile_dict[fnName] =['function'] + tlist[:-1] + [tstr]
    else: # if not found,may self-decl-macro or kenerl-decl macro of func
      pass #  fcFile_dict[fnName] = []
  #print To File
  printToFile(fnFile_dict,fnCall_dict,fcFile_dict)
  return fcFile_dict,fnCall_dict

def getfcDiffInfoDict(diffLog_dict):
  fcFile_dict,fnCall_dict = prosFuncTargetFile() # get call info
  
  fcDiffInfo_dict = OrderedDict()
  for k,vlist in fcFile_dict.items(): # handle function ..
    _type,_file,_rows,state = vlist[0:]
    if k in diffLog_dict:
      fcDiffInfo_dict[k] = diffLog_dict[k]
    elif cmp(_type,'macfun')==0: # macro define function condition
      fileph = SOURCE_PATH1 + _file
      cmd_string = "grep -w '"+state+"' "+fileph
      tstr=commands.getstatusoutput(cmd_string)
      if tstr[0] == 0 and cmp(state,tstr[1]) ==0 :
        fcDiffInfo_dict[k] = ['Not']
      else:
      	cname = state.split('(')[0]
      	if cname in diffLog_dict:
      	  fcDiffInfo_dict[k] = diffLog_dict[cname]
      	else:
          fcDiffInfo_dict[k] = ['Del']+[_type,_file,state]
    else:
      pass
  return fcDiffInfo_dict,fnCall_dict

def printAssitInfo(out,assitInfo_dict,level,assitLoc_dict):
  filename = os.path.basename(FILE_TO_PROCESS)
  
  print >> out,'\n\n=====',level,' level ====='  
  print >> out,'total count:',len(assitInfo_dict)
  for k,vlist in assitInfo_dict.items():  
    diff_type,_type,_file = vlist[0:3]
    print >> out,'\n',k,'  ( diff_type: '+diff_type,'type: '+_type,'file: '+_file,')'
    print >> out,'  --',vlist[3]
    if cmp(diff_type,'Del')!=0:
      print >> out,'  ++',vlist[4]
    print >> out,""
    # print call loction
    if isinstance(assitLoc_dict[k],list) == True:
      for loc in assitLoc_dict[k]:
        print >> out,'  ',filename+':',loc
    else:
      for fcName,fcLoc_list in assitLoc_dict[k].items():
		    print >> out,'  '+fcName
		    for fcLoc in fcLoc_list:
		      print >> out,'    '+fcLoc
		      
def getAssitInfo():
  diffLog_dict = code_Diff() # get diff info
  headfile_list =getHeadFileList() #get head file list
  Alevel_dict,Blevel_dict,Clevel_dict = classDiffLog(diffLog_dict) # get class diff info
  fcDiffInfo_dict,fnCall_dict = getfcDiffInfoDict(diffLog_dict)# get call diff info
  dataStructCall_dict = getDataStructCall(FILE_TO_PROCESS) # get dataStruct call info
  
  assitInfoA_dict = OrderedDict()
  assitInfoB_dict = OrderedDict()
  assitInfoC_dict = OrderedDict()
  assitLoc_dict = OrderedDict() # restore call location
  
  for k,vlist in fcDiffInfo_dict.items():
    if k in Alevel_dict:
      assitInfoA_dict[k] = fcDiffInfo_dict[k]
      assitLoc_dict[k] = fnCall_dict[k]
    elif k in Blevel_dict:
      assitInfoB_dict[k] = fcDiffInfo_dict[k]
      assitLoc_dict[k] = fnCall_dict[k]
    elif k in Clevel_dict:
      assitInfoC_dict[k] = fcDiffInfo_dict[k]
      assitLoc_dict[k] = fnCall_dict[k]
    else: # 'Not',Mov'
      pass
  for k,vdict in dataStructCall_dict.items():
    if k in Blevel_dict:
      assitInfoB_dict[k] = Blevel_dict[k]
      assitLoc_dict[k] = dataStructCall_dict[k]
    else:
      pass
      
  fileTopros = 'source/' + FILE_TO_PROCESS
  for k,vlist in Alevel_dict.items():  #A level
    diff_type,_type,_file = vlist[0:3]
    if cmp(diff_type,'Del')==0 and _type in ('macro'):
      if k not in fcDiffInfo_dict:#
        _file = _file.split('include/')[1]
        if _file in headfile_list:
          cmd_string = "grep -nw '"+k+"' "+fileTopros
          status,tstr=commands.getstatusoutput(cmd_string)
          if status == 0:
            loc_list = tstr.split('\n')
            assitLoc_dict[k] = loc_list
            assitInfoA_dict[k] = Alevel_dict[k]
    elif diff_type in ('Mod','All') and ('macro' in _type):
      if k not in fcDiffInfo_dict:
        _file = _file.split('-->')[0]
        _file = _file.split('include/')[1]
        if _file in headfile_list:
          cmd_string = "grep -nw '"+k+"' "+fileTopros
          status,tstr=commands.getstatusoutput(cmd_string)
          if status == 0:
            loc_list = tstr.split('\n')
            assitLoc_dict[k] = loc_list
            assitInfoA_dict[k] = Alevel_dict[k]
    else: # 'Add'
      pass
    
  for k,vlist in Blevel_dict.items(): #B level
    if k not in fcDiffInfo_dict and (k not in dataStructCall_dict):
      _type = vlist[1]
      _file = vlist[2].split('-->')[0]
      _file = _file.split('include/')[1]
      key = k
      if _type in ('struct','union','enum'):
        key = _type +' '+ key
      if _file in headfile_list:
        cmd_string = "grep -nw '"+key+"' "+fileTopros
        status,tstr=commands.getstatusoutput(cmd_string)
        if status == 0:
          loc_list = tstr.split('\n')
          assitLoc_dict[k] = loc_list
          assitInfoB_dict[k] = Blevel_dict[k]  
  for k,vlist in Clevel_dict.items(): #C level
    if k not in fcDiffInfo_dict:
      _file = vlist[2].split('-->')[0]
      _file = _file.split('include/')[1]
      if _file in headfile_list:
        cmd_string = "grep -nw '"+k+"' "+fileTopros
        status,tstr=commands.getstatusoutput(cmd_string)
        if status == 0:
          loc_list = tstr.split('\n')
          assitLoc_dict[k] = loc_list
          assitInfoB_dict[k] = Clevel_dict[k]      
      
  with open(LOGERR,'w') as out:
    filename = os.path.basename(FILE_TO_PROCESS)
    print >> out,'filename to process:',filename
    print >> out,'more info about this log description to read assitlog_description.txt'
  
    printAssitInfo(out,assitInfoA_dict,'A',assitLoc_dict)
    printAssitInfo(out,assitInfoB_dict,'B',assitLoc_dict)
    printAssitInfo(out,assitInfoC_dict,'C',assitLoc_dict)  
    
	
def main():
    print '\npython file:',sys.argv[0],'running...'
    print 'input file:',sys.argv[1]
    getAssitInfo()
    print 'Done\n'
  
if __name__ == '__main__':
    main()
