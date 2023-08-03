#coding=gb18030
import re, os,fileinput
#parameters
ztouch=xtouch=xoffset=yoffset=Nozzoff=atX=Filalen=FilaCom=zCom=Tem=Forcedz=0
input=output='NULL'
index=0;patndex=0
valid_file=False#为F即无可用文件
flag=flag1=flag2=False
reSignal=False
ZComcum=0
Gflag=False#防止被奇奇怪怪的G92 E0带偏
CustomD="NULL"#自定义放下
CustomR="NULL"#自定义收起
fcon = open("con.txt")
temp=fcon.read()
s = []
path=[]
currHeight=0#存储当前所在的高度
currExtrude=0#存储当前的挤出
item=""
s = re.findall("\d+\.?\d*", temp)
s = list(map(float,s))
ztouch=s[0];xtouch=s[1];xoffset=s[2];yoffset=s[3];atX=s[4];Filalen=s[5];FilaCom=s[6];Nozzoff=s[7];zCom=s[8];Tem=s[9];Forcedz=s[10]
#print(s)
#print(Tem)
s.clear()

for line1 in fileinput.input("con.txt"):
    #print( line1)
    if line1.find("X轴偏移") != -1 and line1.find("-") != -1:
        xoffset=-xoffset
    if line1.find("Y轴偏移") != -1 and line1.find("-") != -1:
        yoffset = -yoffset
    if line1.find("Z轴误差补偿") != -1 and line1.find("-") != -1:
        zCom= -zCom
    if line1.find("回抽补偿") != -1 and line1.find("-") != -1:
        FilaCom= -FilaCom
    if line1.find("自定义收起")!=-1:
        index=line1.find("：")
        CustomD=line1[index+1:]
    if line1.find("自定义放下")!=-1:
        index=line1.find("：")
        CustomR=line1[index+1:]

for item in os.listdir():
    if item.find(".g") !=-1 or item.find(".x3g")!=-1:#识别.G,.GCODE,.X3G,即输入文件
        if item.find("Output")==-1:
            input=item
            valid_file=True
#找到gcode文件，并确定该文件是否已处理过的文件
index=input.find(".")
output=input[0:index]+"_Output.gcode"

for item in os.listdir():
    if item == output:
        os.remove(item)
#清除上一次生成的文件
if valid_file:
    with open(input, "r") as f:#读取输入文件
        with open(output, "w") as f1:#输出文件
            with open("log.txt", "w") as f2:  # 输出日志
                print("Find your Gcode Successfully", file=f2)  #日志说明此时无误
                print("CustomD: " + CustomD, file=f2)
                print("CustomR: " + CustomR, file=f2)
                for line in f.readlines():
                    line = line.strip('\n')#去掉换行符
                    if line.find("M104 S")!=-1:
                        index=line.find("S")
                        s = re.findall("\d+\.?\d*", line[index:])
                        Currtem=float(s[0])
                    if line.find(";LAYER_CHANGE")==-1:
                        print(line, file=f1)  # 将命令原样写入
                        #各个模块
                        if line.find("G1 Z") != -1:  # 如果含有Z抬升的命令
                            if line.find(".")==4:
                                linetemp="G1 Z0"+line[4:]#如果是.47这种
                                s = re.findall("\d+\.?\d*", linetemp)
                                s = list(map(float, s))
                            else:
                                s = re.findall("\d+\.?\d*", line)
                                s = list(map(float, s))
                            currHeight = s[1]
                            print("Height Change: " + str(currHeight), file=f2)  # 日志记录此时的命令
                            #print(line, file=f2)  # 日志记录此时的命令
                            if reSignal==True:
                                print("G1 E" + str(format(float(currExtrude), '.3f')), file=f1)  # 回抽
                                reSignal=False
                        if currHeight >= 0.47:  #此模块在前几层不允许使用

                            # 如果含有接触面注释

                            if line.find(";TYPE:Support material interface") != -1:  # 如果含有支撑接触面的注释
                                print("Support interface, Height: " + str(currHeight), file=f2)
                                #print("Check:"+line,file=f2)
                                flag = True  # 挂上提示应当开始记录参考路径
                                flag1=True#接下来要使用马克笔
                                path.clear()   
                            if flag == True:

                                if line.find("Perimeter") == -1 and line.find(";TYPE:Support material")==-1:
                                    path.append(line)  # 将这命令记录下来，作为马克笔运行的路径参考
                                    #print("OriginPath: " + line, file=f2)  # 说明是原有路径
                                #if line.find("G92 E0")!=-1
                                #    count
                                if line.find("Perimeter") != -1 or (line.find(";TYPE:Support material")!=-1 and line.find("interface")==-1):
                                    path.append(line)#记录这个切换
                                    flag = False  # 把提示取下
                                    #print(path,file=f2)
                                    print("Perimeter detected,stop copying", file=f2)  # 计入日志
                                    #print(";Perimeter detected,stop copying", file=f1)  # 计入日志

                        if line.find("G1")!=-1 and line.find("E")!=-1:
                            index=line.find("E")
                            s = re.findall("\d+\.?\d*",line[index:])
                            currExtrude=s[0]#当前挤出
                    else:
                        if flag1 == True:
                            if Filalen!=0:  # 如果要求了回抽耗材
                               print(";Filament retracting:", file=f1)
                               print("G1 E" + str(format(float(currExtrude) - Filalen,'.3f')), file=f1)  # 回抽
                               print("Filament retracted!", file=f2)  # 日志说明此时回抽
                               print("G1 Z"+str(format(currHeight+0.5,'.3f')),file=f1)
                               reSignal = True  # 提示下次就需要装载耗材了

                            print(";TYPE:Markpen path", file=f1)  # 写入注释说明这些是马克笔的路径


                            if CustomR.find("undefined")!=-1:
                                if ztouch!=0:
                                    if atX == 1:
                                        print("G1 X0", file=f1)
                                    print("G1 Z" + str(ztouch), file=f1)  # lift nozzle
                                    # 把Z轴上升到能触发的高度，Zspx表示最大速度。此时是按下
                                    print("G1 Z" + str(format(currHeight+Nozzoff+5,'.3f')), file=f1)  # lower nozzle
                                    # 降回刚刚记载的高度，也就是currHeight这个变量记录的高度,加5防止笔头污染其他地方
                                elif xtouch!=0:
                                    print("G1 Z"+format(currHeight+Nozzoff,".3f"),file=f1)
                                    #升高喷嘴以防剐蹭
                                    print("G1 X"+str(xtouch),file=f1)
                                    #撞击触发
                                    print("G1 X"+str(xtouch-35),file=f1)
                                    #松开
                                if Tem != 0:
                                    print("M104 S" + str(Currtem - Tem), file=f1)
                                print("Default Deploy",file=f2)


                            else:
                                print(CustomD,file=f1)
                                print("Customized Deploy",file=f2)
                                if Tem != 0:
                                    print("M104 S" + str(Currtem - Tem), file=f1)
                            # 日志记录

                            print("Markpen path starting", file=f2)  # 写入日志说明这些是马克笔的路径
                            #print(path,file=f2)
                            for pathindex,item in enumerate(path):
                                if item.find(";") != -1 or item.find("G1") == -1:
                                    print("Not valid Path: " + item, file=f2)
                                    if item.find("G92 E0")!=-1:
                                        print("G1 Z"+str(format(currHeight+Nozzoff+0.5,'.3f')),file=f1)#稍微升高0.5，以免剐蹭
                                        if path[pathindex+3].find("TYPE")==-1:  #并未切换类型
                                            Gflag=True#提示接下来要减低高度
                                        else:
                                            break#剩下的也不必看了


                                else:
                                    #以下为马克笔输出路径
                                    s = re.findall("\d+\.?\d*", item)
                                    if item.find("X") != -1 and item.find("Y") != -1:  # X,Y都存在
                                        #print("Original: " + item, file=f2)  # 写入日志
                                        print("G1 X" + str(format(float(s[1]) + xoffset,'.3f')) + " Y" +
                                              str(format(float(s[2]) +yoffset,'.3f')), file=f1)
                                        #print("Modified:" + "G1 X" + str(format(float(s[1]) + xoffset, '.3f')) + " Y" + str(format(float(s[2]) + yoffset, '.3f')), file=f2)#写入日志
                                        if flag2 == False:
                                            print("G1 Z" + str(format(currHeight+Nozzoff,'.3f')), file=f1)
                                            #print(";Path 1",file=f1)
                                            flag2=True
                                    if item.find("Y") == -1 and item.find("X") != -1:  # 只有X
                                        #print("Original: " + item, file=f2)  # 写入日志
                                        print("G1 X" + str(format(float(s[1]) + xoffset,'.3f')), file=f1)
                                        #print("Modified:" + "G1 X" + str(format(float(s[1]) + xoffset,'.3f')),file=f2)  # 写入日志
                                        if flag2 == False:
                                            print("G1 Z" + str(format(currHeight+Nozzoff,'.3f')), file=f1)
                                            #print(";Path 1", file=f1)
                                            flag2 = True
                                    if item.find("Y") != -1 and item.find("X") == -1:  # 只有Y
                                        #print("Original: " + item, file=f2)  # 写入日志
                                        print("G1 Y" + str(format(float(s[1]) + yoffset,'.3f')), file=f1)
                                        #print("Modified:" + "G1 Y" + str(format(float(s[1]) + yoffset,'.3f')),file=f1)
                                        if flag2 == False:
                                            print("G1 Z" + str(format(currHeight+Nozzoff,'.3f')), file=f1)

                                            flag2 = True
                                    if Gflag==True:
                                        print("G1 Z"+str(format(currHeight+Nozzoff,'.3f')),file=f1)
                                        Gflag=False

                            #path.clear()

                            print("G1 Z"+str(format(currHeight+Nozzoff+5,'.3f')),file=f1)#稍微升起一下打印机喷嘴

                            #print(atX)

                            if Tem!=0:
                                print("M104 S"+str(Currtem),file=f1)
                            if CustomR.find("undefined")!=-1:
                                if ztouch!=0:
                                    if atX == 1:
                                        print("G1 X0", file=f1)
                                    if zCom!=0:
                                        print("G1 Z" + str(ztouch + ZComcum), file=f1)  # lift nozzle
                                        ZComcum+=zCom
                                    else:
                                        print("G1 Z" + str(ztouch), file=f1)  # lift nozzle
                                    # 把Z轴上升到能触发的高度，Zspx表示最大速度。此时是按下
                                    print("G1 Z" + str(format(currHeight+Nozzoff+5,'.3f')), file=f1)  # lower nozzle
                                    # 降回刚刚记载的高度，也就是currHeight这个变量记录的高度,加5防止笔头污染其他地方
                                    if zCom != 0:
                                        print("G1 Z" + str(currHeight + 1), file=f1)
                                        print("G92 Z" + str(currHeight + 1 - zCom), file=f1)
                                        print("ZCompensation:G92",file=f2)
                                    print(Forcedz)
                                    if Forcedz!=0:
                                        print("G28 Y",file=f1)
                                        print("G28 Z",file=f1)
                                        print("ZCompensation:G28",file=f2)
                                elif xtouch!=0:
                                    print("G1 Z"+format(currHeight+Nozzoff,".3f"),file=f1)
                                    #升高喷嘴以防剐蹭
                                    print("G1 X"+str(xtouch),file=f1)
                                    #撞击触发
                                    print("G1 X"+str(xtouch-35),file=f1)
                                    #松开
                                print("Default Retract",file=f2)

                            else:
                                print(CustomR,file=f1)
                                print("Customized Retract",file=f2)
                            # 日志记录
                            flag1=False
                            flag2=False
    os.startfile(output)
    os.startfile("log.txt")
else:
    with open("log.txt", "w") as f2:  # 输出日志
        print("Error: No available GCODE",file=f2)#说明出现了没文件的错误
