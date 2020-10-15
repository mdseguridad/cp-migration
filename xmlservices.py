#!/usr/bin/env python3

# -*- coding: utf-8 -*


import time,argparse,random
import xml.etree.ElementTree as ET

colors = [ 'aquamarine', 'black', 'blue', 'crete blue', 'burlywood', 'cyan', 'dark green', 'khaki', 'orchid', 'dark orange', \
'dark sea green', 'pink', 'turquoise', 'dark blue', 'firebrick', 'brown', 'forest green', 'gold', 'dark gold', \
'gray', 'dark gray', 'light green', 'lemon chiffon', 'coral', 'sea green', 'sky blue', 'magenta', 'purple', 'slate blue',\
 'violet red', 'navy blue', 'olive', 'orange', 'red', 'sienna', 'yellow']

parser = argparse.ArgumentParser(description='exportamos un servicio de las politicas de Checkpoint')
parser.add_argument('servicesfiles',help='fichero xml con los servicios')
parser.add_argument('service2find',help='objeto a exportar')
parser.add_argument('-t','--tag', help='tag', default='python')


args = parser.parse_args()
ficheroServices = args.servicesfiles
serviceFind = args.service2find
tag = args.tag
commandTail ='ignore-warnings true -s id.txt'

def parseNetworksObjects(netObjects):
    objectList = []
    tmpObjects = netObjects.find('members')
    tmpObjects = tmpObjects.findall('reference')
    for i in tmpObjects:
        j = i.find('Name')
        objectList.append(j.text)
    return objectList

def prettyGroup(objects):
    tmpList = list(objects)
    if (len(tmpList) > 1):
        groupString = "'["
        for i in tmpList[0:-1]:
            groupString = groupString + '"'+ i + '", '
        groupString = groupString + '"'+ tmpList[-1] + '"'
        groupString = groupString + "]'"
    elif (len(tmpList) == 1):
        groupString = '"' + tmpList[0] + '"'
    else:
        groupString = '"ErrorRaro"'
    return groupString

def expandGroup (recordList, allRecordGroups):
    backList = []
    for i in recordList:
         if (i in allRecordGroups):
             backList.extend(expandGroup(allRecordGroups[i].split(','),allRecordGroups))
             backList.append(i)
         else:
             backList.append(i)
    backList = set(backList)
    return backList
    
  
def getServices(servicesXML):
    allServicesObject = dict()
    allServicesGroup = dict()
    for child in servicesXML:
       type = child.find('type').text
       color = child.find('color').text
       if ((color == 'black') or (color not in colors)):
           color = random.choice(colors)
       comments = child.find('comments').text
       if (comments != None):
           comments =  comments + ' importado: ' + fecha
       else:
           comments = 'Importado el : ' + fecha
       if ((type == 'Tcp') or (type == 'tcp')):
           timeout =  child.find('timeout').text
           if (timeout == '0'):
               line = 'mgmt_cli add service-tcp name "' + child.find('Name').text + '"  port "' + \
               child.find('port').text + '" tags "' + tag + '" color "' + color + '" comments "' + comments + '" ' + commandTail
           else:
                line = 'mgmt_cli add service-tcp name "' + child.find('Name').text + '"  port "' + \
                child.find('port').text + '" tags "' + tag + '" color "' + color + \
                '" use-default-session-timeout false session-timeout '+ timeout  + \
                '  comments "' + comments + '" ' + commandTail
           allServicesObject[child.find('Name').text] = line
       elif ((type == 'Udp') or (type == 'udp')):
           timeout =  child.find('timeout').text
           if (timeout == '0'):
               line = 'mgmt_cli add service-udp name "' + child.find('Name').text + '"  port "' + \
               child.find('port').text  + '" tags "' + tag + '" color "' + color + '" comments "' + comments + '" ' + commandTail
           else:
                line = 'mgmt_cli add service-udp name "' + child.find('Name').text + '"  port "' + \
                child.find('port').text  + '" tags "' + tag + '" color "' + color + \
                '" use-default-session-timeout false session-timeout '+ timeout  + \
                ' comments "' + comments + '" ' + commandTail
           allServicesObject[child.find('Name').text] = line
       elif ((type == 'Icmp') or (type == 'icmp')):
           line = 'mgmt_cli add service-icmp name "' + child.find('Name').text + '"  icmp-type ' + \
           child.find('icmp_type').text  + ' tags "' + tag +  '" color "' + color + '" comments "' + comments + '" ' + commandTail
           allServicesObject[child.find('Name').text] = line
       elif ((type == 'Other') or (type == 'other')):
           line = 'mgmt_cli add service-other name "' + child.find('Name').text + '"  ip-protocol ' + \
           child.find('protocol').text  + ' tags "' + tag + '" color "' + color + '" comments "' + comments + '" ' + commandTail
           allServicesObject[child.find('Name').text] = line
       elif (type == 'group'):
           groupMembers = parseNetworksObjects(child)
           line = 'mgmt_cli add service-group name "' + child.find('Name').text + '" members ' + prettyGroup(groupMembers) +\
           ' tags "' + tag +'" color "' + color + '" comments "' + comments + '" ' + commandTail
           allServicesObject[child.find('Name').text] = line
           allServicesGroup[child.find('Name').text] = ','.join(groupMembers)
    return allServicesObject, allServicesGroup


fecha = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) 
print ('# fichero de servicios:', ficheroServices)
print ('# fecha: ', fecha)
print ()


try:
    treeServices = ET.parse(ficheroServices)
except:
    print ('Error leyendo el fichero: ', ficheroServices)
    exit()

rootServices = treeServices.getroot()
allServicesList,allServicesGroup = getServices(rootServices)

print ('# Info')
print ('')
print ('')

print ('# Total services:',len(allServicesList))
print ('# Total services group:',len(allServicesGroup))

if serviceFind in allServicesList:
    if serviceFind in allServicesGroup:
        netList = []
        netList.extend(expandGroup([serviceFind], allServicesGroup))
        for j in netList:
            print (allServicesList[j])
    else:
        print (allServicesList[serviceFind])
else:
    print ('Service ',serviceFind,'not in network object db')
