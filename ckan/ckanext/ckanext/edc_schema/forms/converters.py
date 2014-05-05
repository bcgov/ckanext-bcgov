def convert_to_extras(key, data, errors, context):
#    print "key :====> ", key, "data : ====>", data[key] 
    extras = data.get(('extras',), [])
    if not extras:
        data[('extras',)] = extras
    
    keyStr = ':'.join([str(x) for x in key])
    extras.append({'key': keyStr, 'value': data[key]})


def convert_from_extras(key, data, errors, context):

#    print "key : <====", key, "\n"
    def remove_from_extras(data, keyList):
        to_remove = []
        for data_key, data_value in data.iteritems():
            if (data_key[0] == 'extras' and data_key[1] in keyList) :
                to_remove.append(data_key)
        for item in to_remove:
            del data[item]
        
    
    indexList = [] # A list containing the index of items in extras to be removed.
    new_data = {}  #A new dictionary for data stored in extras with the given key
    for data_key, data_value in data.iteritems():
        if (data_key[0] == 'extras'
            and data_key[-1] == 'key'):
            #Extract the key components eparated by ':'
            keyList = data_value.split(':')
            #Check for multiple value inputs and convert the list item index to integer
            if (len(keyList) > 1):
                keyList[1] = int(keyList[1])
            #Construct the key for the stored value(s)
            newKey = tuple(keyList)
            if (key[-1] == newKey[0]):
                #Retrieve data from extras and add it to new_data so it can be added to the data dictionary. 
                new_data[newKey] = data[('extras', data_key[1], 'value')]
                #Add the data index in extras to the list of items to be removed. 
                indexList.append(data_key[1])
    
    #print new_data
    #Remove all data from extras with the given index
    remove_from_extras(data, indexList)

    #Remove previous data stored under the given key
    del data[key]
    
    deleteIndex = []
    for data_key, data_value in new_data.iteritems():
        #If this is a deleted record then add it to the deleted list to be removed from data later.  
        if ('delete' in data_key
            and data_value == '1'):
            deleteIndex.append(data_key[1])
    deleted = []        
    for data_key, data_value in new_data.iteritems():
            if (len(data_key) > 1 
                and data_key[1] in deleteIndex):
                deleted.append(data_key)
    for item in deleted :
        del new_data[item]

    #Add data extracted from extras to the data dictionary
    for data_key, data_value in new_data.iteritems():
        data[data_key] = data_value
        

def convert_dates_form(data):
#    print data;
    return data
