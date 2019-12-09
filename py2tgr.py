#!/usr/bin/env python3
import sys,os,time,dis
global args,pre,jmps,vars
args,pre,jmps,vars=[],[],[],[]
RAMPOS = 0x00000000
#  RAM POS  WORK_ARGS 
#      /^\ /^-------^\
#regs=[0,0,0,0,0,0,0,0
#      A B C D E F G H
def regs(x):
 if regs == 0: return "C"
 if regs == 1: return "D"
 if regs == 2: return "E"
 if regs == 3: return "F"
 if regs == 4: return "G"
 if regs == 5: return "H"
 return "H"
def findvar(x,end):
 print(" \\Checking for var. \""+x+"\"")
 for j in range(len(vars)):
  if vars[j][0] == x:
   print("  \\Found var. \""+x+"\"")
   return j
 print("  \\Could not find var. \""+x+"\" "+end,end=(len(end)<1)*"\n")
 return -1
if len(sys.argv) > 2:
 inF,out = open(sys.argv[1],"r").read(),[]
 i,m,d,n=0,0,[i for i in dis.Bytecode(inF)],inF.split("\n")
 while i<len(d):
  if d[i].starts_line!=None and args != []: print("line: "+str(m)+" | "+n[m]+"\n"+str(pre)+"\n"); args=[]; m+=1
  print(d[i])
  
  if d[i].opname == "LOAD_CONST":
   if not("SUBSCR" in d[i+1].opname):
    print("\\Found LOAD_CONST")
    if d[i].argval == None:
     print(" \\Can't set argument to \"None\".");
     if d[i].is_jump_target == True:
      args.append(["jmp",d[i].argval])
     else: print(" \\Skipped"); i=i+1; continue
    else: args.append(d[i].argval); print(" \\"+str(args))
  
  if d[i].opname == "BUILD_LIST":
   print("\\Found BUILD_LIST")
   for j in range(len(args)):
    print("index["+str(j)+"]:",args[j])
   args.insert(0,"BUILD_LIST")
   
  if d[i].opname == "STORE_NAME":
   print("\\Found STORE_NAME")
   if d[i].argval == None: print("Token Error: Cannot set a None Var."); sys.exit()
   print(args,len(args))
   if len(args) > 1:
    if args[0] == "BUILD_LIST": args.pop(0)
    foundvar = findvar(d[i].argval+"["+str(j)+"]","generating a ")
    if foundvar != -1: vars.append([d[i].argval,RAMPOS,len(args)-1])
    for j in range(len(args)-2):
     foundvar = findvar(d[i].argval+"["+str(j)+"]","generating a ")
     if foundvar != -1:
      pre.append(["setvar",vars[foundvar][1],args[0]])
     else:
      if type(args[j]) == type(True):
       vars.append([d[i].argval+"["+str(j)+"]",RAMPOS,1])
       pre.append(["setvar",RAMPOS,args[j],1])
       print("Boolean (1-bits -> 1 byte)...")
       RAMPOS=RAMPOS+1
      elif type(args[j]) == type(0):
       if args[j] > 0xFFFF:
        vars.append([d[i].argval+"["+str(j)+"]",RAMPOS,4])
        pre.append(["setvar",RAMPOS,args[j],4])
        print("Integer (32-bits -> 4 bytes)...")
        RAMPOS=RAMPOS+4
       else:
        vars.append([d[i].argval+"["+str(j)+"]",RAMPOS,2])
        pre.append(["setvar",RAMPOS,args[j],2])
        print("Integer (16-bits -> 2 bytes)...")
        RAMPOS=RAMPOS+2
      elif type(args[j]) == type(0.0):
       vars.append([d[i].argval+"["+str(j)+"]",RAMPOS,4])
       pre.append(["setvar",RAMPOS,args[j],4])
       print("Float (32-bits -> 4 bytes)...")
       RAMPOS=RAMPOS+8
      elif type(args[j]) == type(""):
       vars.append([d[i].argval+"["+str(j)+"]",RAMPOS,len(args[j])])
       pre.append(["setvar",RAMPOS,args[j],len(args[j])])
       print("String ("+str(len(args[j])*8)+"-bits -> "+str(len(args[j]))+" Bytes/Characters)...")
       RAMPOS=RAMPOS+len(args[j])
     print("   \\"+str(d[i].argval)+"["+str(j)+"] = "+str(args[j]))
   elif len(args) == 1:
    foundvar = findvar(d[i].argval,"generating a ")
    if foundvar != -1:
     if type(args[0]) == type(""): pre.append(["setvar",vars[args[1]][1],(args[0]+"\x00"*((vars[args[1]+1][1]-vars[args[1]][1])-len(args[0])))[:(vars[args[1]+1][1]-vars[args[1]][1])],-1])
     pre.append(["setvar",vars[foundvar][1],args[0],-1])
    else:
     if type(args[0]) == type(True):
      vars.append([d[i].argval,RAMPOS,1])
      pre.append(["setvar",RAMPOS,args[0],1])
      print("Boolean (1-bits -> 1 byte)...")
      RAMPOS=RAMPOS+1
     elif type(args[0]) == type(0):
      vars.append([d[i].argval,RAMPOS,4])
      pre.append(["setvar",RAMPOS,args[0],4])
      print("Integer (32-bits -> 4 bytes)...")
      RAMPOS=RAMPOS+4
     elif type(args[0]) == type(0.0):
      vars.append([d[i].argval,RAMPOS,4])
      pre.append(["setvar",RAMPOS,args[0],4])
      print("Float (32-bits -> 4 bytes)...")
      RAMPOS=RAMPOS+8
     elif type(args[0]) == type(""):
      vars.append([d[i].argval,RAMPOS,len(args[0])])
      pre.append(["setvar",RAMPOS,args[0],len(args[0])])
      print("String ("+str(len(args[0])*8)+"-bits -> "+str(len(args[0]))+" Bytes/Characters)...")
      RAMPOS+=len(args[0])
    print("   \\"+str(d[i].argval)+" = "+str(args[0]))
  if d[i].opname == "STORE_SUBSCR":
   print("\\Found STORE_SUBSCR")
   if len(args) > 1:
    if type(args[0]) == type(""): pre.append(["setvar",vars[args[1]][1],(args[0]+"\x00"*((vars[args[1]+1][1]-vars[args[1]][1])-len(args[0])))[:(vars[args[1]+1][1]-vars[args[1]][1])],-1])
    else: pre.append(["setvar",vars[args[1]][1],args[0],-1])
   
  if d[i].opname == "LOAD_NAME":
   print("\\Found LOAD_NAME")
   print("SUBSCR" in d[i+2].opname,d[i+2].opname)
   if "SUBSCR" in d[i+2].opname:
    print(" \\Found SUBSCR instuction")
    foundvar=findvar(d[i].argval+"["+str(d[i+1].argval)+"]","... Unavailable to set list var.\n")
    if foundvar != -1: args.append(foundvar)
   else:
    foundvar=findvar(d[i].argval,"\n")
    if foundvar != -1: args.append(foundvar)
   print(args)
  if d[i].opname == "BINARY_ADD":
   print("\\Found BINARY_ADD")
   pre.append(["add",vars[args[0]][1],vars[args[1]][1]])
   args=args[:-1]
  #
  
  i+=1
 print("vars:"+str(vars)+"\npre:"+str(pre))
# for i in pre:
#    out = "mov "+regs(d[i].arg)+","+str(d[i+1]) #mov A,0
elif len(sys.argv) == 2:
 print("Error: Requesting output \".tgr\" file...")
else:
 print("Error: Requesting input \".py\" file...")
