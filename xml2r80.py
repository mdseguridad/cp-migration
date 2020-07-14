#!/usr/bin/env python3

# -*- coding: utf-8 -*


import time,argparse,random
import xml.etree.ElementTree as ET

colors = [ 'aquamarine', 'black', 'blue', 'crete blue', 'burlywood', 'cyan', 'dark green', 'khaki', 'orchid', 'dark orange', \
'dark sea green', 'pink', 'turquoise', 'dark blue', 'firebrick', 'brown', 'forest green', 'gold', 'dark gold', \
'gray', 'dark gray', 'light green', 'lemon chiffon', 'coral', 'sea green', 'sky blue', 'magenta', 'purple', 'slate blue',\
 'violet red', 'navy blue', 'olive', 'orange', 'red', 'sienna', 'yellow']

parser = argparse.ArgumentParser(description='exportamos la politicas de Checkpoint')
parser.add_argument('policy',help='fichero xml con las politicas')
parser.add_argument('nat',help='fichero xml con los reglas de NAT')
parser.add_argument('object',help='fichero xml con los objetos')
parser.add_argument('services',help='fichero xml con los servicios')
parser.add_argument('-l','--layer', help='policy layer', default='Network')
parser.add_argument('-p','--package', help='policy package', default='Standard')
parser.add_argument('-t','--tag', help='tag', default='python')
parser.add_argument('-o','--objectsexport', help='export objects', action='store_true')
parser.add_argument('-r','--rulesexport', help='export rules', action='store_true')
parser.add_argument('-s','--servicesexport', help='export services', action='store_true')
parser.add_argument('-n','--natexport', help='export nat rules', action='store_true')

args = parser.parse_args()
ficheroPolicy = args.policy
ficheroNAT = args.nat
ficheroObjects = args.object
ficheroServices = args.services
policyLayer = args.layer
tag = args.tag
package = args.package
commandTail ='ignore-warnings true -s id.txt'


def parseNetworksObjects(netObjects):
    objectList = []
    tmpObjects = netObjects.find('members')
    tmpObjects = tmpObjects.findall('reference')
    for i in tmpObjects:
        j = i.find('Name')
        objectList.append(j.text)
    return objectList

def parseNATObjects(netObjects):
    objectList = []
    tmpObjects = netObjects
    for i in tmpObjects:
        j = i.find('Name')
        objectList.append(j.text)
    return objectList

def parseNATObjectsCompound(netObjects):
    objectList = []
    tmpObjects = netObjects
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
def parseInterfaces(netObjects):
    objectList = []
    tmpObjects = netObjects.find('interfaces')
    tmpObjects = tmpObjects.findall('interfaces')
    for i in tmpObjects:
        j = i.find('ipaddr')
        k = i.find('netmask')
        l = i.find('officialname')
        if (j != ''):
            objectList.append(str(j.text) + ';' + str(k.text) + ';' + str(l.text))
    return objectList

def prettyInterfaces(objects):
    tmpList = list(objects)
    groupString = ''
    counter = 1
    for i in tmpList:
        ipaddr, mask, name = i.split(';')
        groupString = groupString + ' interfaces.'+ str(counter) +'.name "' + name + '" ' +\
                 ' interfaces.'+ str(counter) +'.subnet  "' + ipaddr + '" ' +\
                 ' interfaces.'+ str(counter) +'.subnet-mask  "' + mask+ '" '
        counter = counter + 1        
    return groupString
    
def getRules(rulesList):
    newRules = []
    newNetObject = []
    newServices = []
    for rule in rulesList:
        # Procces sections
        if (rule.find('header_text') != None):
            newRules.append('mgmt_cli add access-section name "'+ rule.find('header_text').text + \
            '" position bottom layer "' + policyLayer + '" ' + commandTail)
        else:
            # Process Rule_Number
            ruleNumber = rule.find('Rule_Number').text
            # Process rule name
            if rule.find('name').text:
                ruleName = rule.find('name').text  + ' old rule: ' + ruleNumber
            else:
                ruleName = 'old rule: ' + ruleNumber
            # Clean rule name
            rulenName = ruleName.strip()
            # Process disabled
            ruleDisabled = rule.find('disabled').text
            if (ruleDisabled == 'true'):
                ruleEnabled = 'false'
            else:
                ruleEnabled = 'true'
            # Process comments
            comments = rule.find('comments').text
            if (comments != None):
                comments =  comments + ' importado: ' + fecha
            else:
                comments = 'Regla importada el  ' + fecha
            # Process sources
            sourceList = parseNetworksObjects(rule.find('src'))
            newNetObject.extend(sourceList)
            # Process destinations
            destinationList = parseNetworksObjects(rule.find('dst'))
            newNetObject.extend(destinationList)
            # Process Services
            serviceList = parseNetworksObjects(rule.find('services'))
            newServices.extend(serviceList)
            # Process Actions
            actionObject = rule.find('action').find('action').find('Name')
            action = actionObject.text
            newRules.append('mgmt_cli add access-rule layer "' + policyLayer +'" name "' + \
            ruleName + '" action ' + action + ' source ' + prettyGroup(sourceList) + ' destination ' + \
            prettyGroup(destinationList) + ' service ' + prettyGroup(serviceList) + ' enabled ' +\
            ruleEnabled + ' position bottom track.type "Log" comments "' + comments + '" ' + commandTail)
            
    return  newRules, newNetObject, newServices

def getNAT(rulesList):
    newRules = []
    newNetObject = []
    newServices = []
    for rule in rulesList:
        # Procces sections
        #print ('Rule name:', rule.find('Rule_Number').text)
        if (rule.find('header_text') != None):
            newRules.append('###')
            newRules.append('mgmt_cli add nat-section name "'+ str(rule.find('header_text').text) + \
            '" position bottom package "' + package + '" ' + commandTail)
            newRules.append('###')
        else:
            # Process Rule_Number
            ruleNumber = rule.find('Rule_Number').text
            # Process disabled
            ruleDisabled = rule.find('disabled').text
            if (ruleDisabled == 'true'):
                ruleEnabled = 'false'
            else:
                ruleEnabled = 'true'
            # Process comments
            comments = rule.find('comments').text
            if (comments != None):
                comments =  comments + ' importado: ' + fecha
            else:
                comments = 'Importado el : ' + fecha
            # Process nat flawor
            if (rule.find('src_adtr_translated').find('adtr_method').text == 'adtr_method_static'):
                natType = 'static'
            else:
                natType = 'hide'
            # Process Sources
            sourceList = parseNATObjects(rule.find('src_adtr'))
            newNetObject.extend(sourceList)
            # Process Destination
            destinationList = parseNATObjects(rule.find('dst_adtr'))
            newNetObject.extend(destinationList)
            # Process traslated Sources
            sourceListTraslated = parseNATObjectsCompound(rule.find('src_adtr_translated'))
            newNetObject.extend(sourceListTraslated)
            # Process traslated Destination
            destinationListTraslated = parseNATObjectsCompound(rule.find('dst_adtr_translated'))
            newNetObject.extend(destinationListTraslated)
            # Process services
            serviceLists = parseNATObjects(rule.find('services_adtr'))
            newServices.extend(serviceLists)
            serviceListsTraslated = parseNATObjectsCompound(rule.find('services_adtr_translated'))
            newServices.extend(serviceListsTraslated)
            # Mount the enchilada
            item = 'mgmt_cli add nat-rule package "' + package + '" position bottom ' +\
            ' enabled ' + ruleEnabled + ' method "' + natType +'"'
            if (sourceList[0] != 'Any'):
                item = item + ' original-source ' + prettyGroup(sourceList)
            if (destinationList[0] != 'Any'):
                item = item + ' original-destination ' + prettyGroup(destinationList)
            if (serviceLists[0] != 'Any'):
                item = item + ' original-service ' + prettyGroup(serviceLists)
            if (sourceListTraslated[0] != 'Any'):
                item = item + ' translated-source ' + prettyGroup(sourceListTraslated)
            if (destinationListTraslated[0] != 'Any'):
                item = item + ' translated-destination ' + prettyGroup(destinationListTraslated)
            if (serviceListsTraslated[0] != 'Any'):
                item = item + ' translated-service ' + prettyGroup(serviceListsTraslated)
            item = item + ' comments "' + comments + '" ' + commandTail
            newRules.append(item)
    return  newRules, newNetObject, newServices

def getObjetcs(objectsXML):
    allNetObject = dict()
    allNetGroup = dict()
    for child in objectsXML:
       type = child.find('type').text
       color = child.find('color').text
       if ((color == 'black') or (color not in colors)):
           color = random.choice(colors)
       comments = child.find('comments').text
       if (comments != None):
           comments =  comments + ' importado: ' + fecha
       else:
           comments = 'Importado el : ' + fecha   
       # Datos para redes
       if (type == 'network'):
           if (child.find('addr_type_indication').text == 'IPv6'):
               line = 'mgmt_cli add-network name "' + child.find('Name').text +'" subnet6 ' + \
               child.find('ipaddr6').text + ' subnet-mask 56 tags "' + tag +\
               '" color "' + color + '" comments "Dummy6 ' + comments + '" ' + commandTail
           else:
               line = 'mgmt_cli add-network name "' + child.find('Name').text +'" subnet ' + \
               child.find('ipaddr').text + ' subnet-mask '+ child.find('netmask').text + ' tags "' + tag +\
               '" color "' + color + '" comments "' + comments + '" ' + commandTail
           allNetObject[child.find('Name').text] = line
       # Datos para hosts
       elif (type == 'host'):
           line = 'mgmt_cli add-host name "' + child.find('Name').text + '" ip-address ' + \
           child.find('ipaddr').text + ' tags "' + tag + '" color "' + color + '" comments "' +  comments +'" '
           # Extra Topology
           interfacesExtra = parseInterfaces(child)
           if (len(interfacesExtra) > 0):
               #print ('ExtraTopology',child.find('Name').text, child.find('ipaddr').text,interfacesExtra, prettyInterfaces(interfacesExtra))
               line = line + prettyInterfaces(interfacesExtra)
           line = line  + commandTail
           allNetObject[child.find('Name').text] = line
       # Datos para rangos
       elif (type == 'machines_range'):
           line = 'mgmt_cli add address-range name "' + child.find('Name').text + '" ip-address-first ' + \
           child.find('ipaddr_first').text + ' ip-address-last '+ child.find('ipaddr_last').text + \
           ' tags "' + tag +'" color "' + color + '" comments "' + comments + '" ' + commandTail
           allNetObject[child.find('Name').text] = line
       # Datos para gonjetos que se pasan como dummies
       elif ((type == 'cluster_member') or (type == 'gateway') or (type == 'gateway_cluster') or  \
            (type == 'vsx_cluster_member') or (type == 'vs_cluster_member') or (type == 'vs_gateway') or \
            (type == 'gateway_plain')):
           line = 'mgmt_cli add-host name "' + child.find('Name').text + '" ip-address 127.0.0.1' + \
           ' tags "Dummy" color "pink" comments "Dummy:' + type + ' -- ' + comments + '" '
           # Extra Topology
           interfacesExtra = parseInterfaces(child)
           if (len(interfacesExtra) > 0):
               #print ('ExtraTopology',child.find('Name').text, child.find('ipaddr').text,interfacesExtra, prettyInterfaces(interfacesExtra))
               line = line + prettyInterfaces(interfacesExtra)
           line = line  + commandTail
           allNetObject[child.find('Name').text] = line
       # Datos para grupos
       elif (type == 'group'):
           groupMembers = parseNetworksObjects(child)
           if groupMembers:
               line = 'mgmt_cli add group name "' + child.find('Name').text + '" members ' + prettyGroup(groupMembers) +\
               ' tags "' + tag +'" color "' + color + '" comments "'+ '" ' + commandTail
           else:
               line = 'mgmt_cli add group name "' + child.find('Name').text  +\
               '" tags "' + tag +'" color "' + color + '" comments "'+ '" ' + commandTail
           allNetObject[child.find('Name').text] = line
           allNetGroup[child.find('Name').text] = ','.join(groupMembers)
    return allNetObject, allNetGroup
  
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
           line = 'mgmt_cli add service-tcp name "' + child.find('Name').text + '"  port "' + \
           child.find('port').text + '" tags "' + tag + '" color "' + color + '" comments "' + comments + '" ' + commandTail
           allServicesObject[child.find('Name').text] = line
       elif ((type == 'Udp') or (type == 'udp')):
           line = 'mgmt_cli add service-udp name "' + child.find('Name').text + '"  port "' + \
           child.find('port').text  + '" tags "' + tag + '" color "' + color + '" comments "' + comments + '" ' + commandTail
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
print ('# fichero de politica:' , ficheroPolicy)
print ('# fichero de objetos:' , ficheroObjects)
print ('# fichero de servicios:', ficheroServices)
print ('# fichero de NAT:', ficheroNAT)
print ('# fecha: ', fecha)
print ()

# Leemos los ficheros
try:
    tree = ET.parse(ficheroPolicy)
except:
    print ('Error leyendo el fichero: ', ficheroPolicy)
    exit()
try:
    treeObjects = ET.parse(ficheroObjects)
except:
    print ('Error leyendo el fichero: ', ficheroObjects)
    exit()
try:
    treeServices = ET.parse(ficheroServices)
except:
    print ('Error leyendo el fichero: ', ficheroServices)
    exit()
try:
    treeNAT = ET.parse(ficheroNAT)
except:
    print ('Error leyendo el fichero: ', ficheroNAT)
    exit()

root = tree.getroot()
rootObjects = treeObjects.getroot()
rootServices = treeServices.getroot()
rootNAT = treeNAT.getroot()

# Proceso de reglas
# Fijamos la politica, porque es unica
root = root[0]
netList = []
allServicesList = []
print ('# Policy name:', root.find('Name').text)
processedRules, netList, servicesList = getRules(root.find('rule'))

# Proceso los NATS
rootNAT = rootNAT[0]
print ('# NAT policy name:', rootNAT.find('Name').text)
print ('')
processedNAT, netNAT, servicesNAT = getNAT(rootNAT.find('rule_adtr'))
# Proceso de objetos
allNetObject,allNetGroup = getObjetcs(rootObjects)

# Sumo objetos y servicios
netList = netList + netNAT
servicesList = servicesList + servicesNAT

# proceso los grupos objetos de  que aparezan
netList = set(netList)
netList.remove('Any')

print ('# Info')
print ('')
print ('# Total policy rules:',len(processedRules))
print ('# Total NAT rules:',len(processedNAT))
print ('')
print ('# Unique networks objets in policy & NAT:',len(netList))
netList = expandGroup(netList, allNetGroup)
print ('# Expanded networks objets in policy & NAT:',len(netList))
# Proceso de  Servicios
allServicesList,allServicesGroup = getServices(rootServices)
servicesList = set(servicesList)
servicesList.remove('Any')
print ('# Unique services in policy:',len(servicesList))
servicesList = expandGroup(servicesList, allServicesGroup)
print ('# Expanded services in policy:',len(servicesList))
# More numbers
print ('# Total network objects:',len(allNetObject))
print ('# Total network groups:',len(allNetGroup))
print ('# Total services:',len(allServicesList))
print ('# Total services group:',len(allServicesGroup))

if args.objectsexport:
    print ('')
    print ('## Network Object')
    for i in netList:
        if i in allNetObject:
            print (allNetObject[i])
        else:
            print ('#ERROR: objeto nulo:', i)

if args.servicesexport:
    print ('')
    print ('## Services')
    for i in servicesList:
         if i in allServicesList:
             print (allServicesList[i])
         else:
             print ('#ERROR: servicio nulo:', i)
             
if args.rulesexport:
    print ('')
    print ('## Rules')
    for i in processedRules:
          print (i)

if args.natexport:
    print ('')
    print ('## Nat Rules')
    for i in processedNAT:
        print (i)
