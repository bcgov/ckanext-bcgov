# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 

# FIXME: these redefined converters for extra fields are not compatible with
# the way CKAN normally stores extras. They were created to support adding
# nested values to datasets, so we need to find a new way to support nested
# values without breaking compatibility
def convert_to_extras(key, data, errors, context):
    extras = data.get(('extras',), [])
    if not extras:
        data[('extras',)] = extras

    keyStr = ':'.join([str(x) for x in key])
    extras.append({'key': keyStr, 'value': data[key]})


def convert_from_extras(key, data, errors, context):

    def remove_from_extras(data, keyList):
        to_remove = []
        for data_key, data_value in data.items():
            if (data_key[0] == 'extras' and data_key[1] in keyList) :
                to_remove.append(data_key)
        for item in to_remove:
            del data[item]

    indexList = [] # A list containing the index of items in extras to be removed.
    new_data = {}  #A new dictionary for data stored in extras with the given key
    for data_key, data_value in data.items():
        if (data_key[0] == 'extras'
            and data_key[-1] == 'key'):
            #Extract the key components eparated by ':'
            keyList = data_value.split(':')
            #Check for multiple value inputs and convert the list item index to integer
            if (len(keyList) > 1):
                keyList[1] = int(keyList[1])
            #Construct the key for the stored value(s)
            newKey = tuple(keyList)
            if (key[-1] == newKey[0] or key == newKey):
                #Retrieve data from extras and add it to new_data so it can be added to the data dictionary. 
                new_data[newKey] = data[('extras', data_key[1], 'value')]
                #Add the data index in extras to the list of items to be removed. 
                indexList.append(data_key[1])
    
    #Remove all data from extras with the given index
    remove_from_extras(data, indexList)

    #Remove previous data stored under the given key
    del data[key]
    
    deleteIndex = []
    for data_key, data_value in new_data.items():
        #If this is a deleted record then add it to the deleted list to be removed from data later.  
        if ('delete' in data_key and data_value == '1'):
            deleteIndex.append(data_key[1])
    deleted = []        
    for data_key, data_value in new_data.items():
            if (len(data_key) > 1 
                and data_key[1] in deleteIndex):
                deleted.append(data_key)
                
    if not errors:            
        for item in deleted :
            del new_data[item]

    #Add data extracted from extras to the data dictionary
    for data_key, data_value in new_data.items():
        data[data_key] = data_value
        

def convert_dates_form(data):
    return data

def remove_whitespace(value, context):
    if isinstance(value, str):
        return value.strip()
    return value


def convert_iso_topic(key, data, errors, context):    
    iso_topic_cat = data[key]
    if iso_topic_cat :
        if isinstance(iso_topic_cat, str):  
            iso_topic_cat = [iso_topic_cat]  
        data[key] = ','.join(iso_topic_cat)          
        
