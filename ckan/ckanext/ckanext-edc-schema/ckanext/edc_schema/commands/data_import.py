import cx_Oracle
import urllib2
import urllib
import os
import sys
import json
import pprint
import re
from pylons import config
import getpass

from ckanext.edc_schema.commands.base import edc_package_create

from ckanext.edc_schema.util.util import (get_organization_id, 
                                          get_edc_tag_id, 
                                          get_user_id)

user_name = 'khalegh'
#user_name = 'admin'


def load_record_dict(dict_file):

    if not os.path.exists(dict_file):
        return {}
    #Read the organizations json file
    with open(dict_file) as json_file:
        record_dict = json.loads(json_file.read())
    
    return record_dict

def save_record_dict(record_dict, dict_file):
    
    with open(dict_file, 'w') as json_file:
        json.dump(record_dict, json_file)

def get_record_name(record_dict, title):
    '''
    Returns a unique record name based on the given record title
    '''
    
    #Replace all characters other that 0-9, a-z, A-Z with space  
    name = re.sub('[^0-9a-zA-Z]+',' ', title)
    name = ' '.join(name.split())
    
    #Remove extra white spaces and replace spaces with '-'
    name = name.lower().strip().replace(' ', '-')
    
    #Truncate the title, it cannot hav emore that 100 characters 
    if len(name) > 100 :
        name = name[:100] 
    
    count = 0
    
    #Check if a record with this exists
    if name in record_dict :
        count = record_dict[name]
    count += 1
    record_dict[name] = count
    if count == 1:
        return name
    else:
        #If there are more than one record with the same name add '_' + 3-digit record count to the name
        index = min(len(name), 96)
        return name[:index] + ("-%03d" % (count,))
    

def get_connection(data_source):
    
    if data_source.lower() == 'odc' :
#         host = 'sponde.bcgov'
#         port = 1521
#         SID = 'idwprod1.bcgov'    
#         user_name = 'proxy_metastar'
#         password = 'h0tsh0t'
        connection_str = "proxy_metastar/h0tsh0t@slkux1.env.gov.bc.ca/idwprod1.bcgov"
        con = cx_Oracle.connect(connection_str)
    elif data_source.lower() == 'discovery' :
         user_name = 'metastar'
         host = 'slkux12.env.gov.bc.ca'
         port = 1521
         SID = 'BCGWDLV'
         password = 'blueb1rd'
         dsn_tns = cx_Oracle.makedsn(host, port, SID)
         con = cx_Oracle.connect(user_name, password, dsn_tns)
#        connection_str = "proxy_metastar/h0tsh0t@slkux1.env.gov.bc.ca/idwprod1.bcgov"
    else :
        print "No data source is given."
    
#    password = getpass.getpass("Password:")
    
    
    
#    con = cx_Oracle.connect(connection_str)
    
    return con

def import_odc_records(con, record_dict):
    
    user_id = get_user_id(user_name)
#    print user_id
    
    edc_auery = "SELECT DBC_RS.RESOURCE_SET_ID RESOURCE_SET_ID " + \
                ",DBC_CO.CREATOR_ORGANIZATION CREATOR_ORGANIZATION " + \
                ",DBC_RS.TITLE TITLE " + \
                ",DBC_RS.DESCRIPTION DESCRIPTION " + \
                ",DBC_RS.KEYWORDS KEYWORDS " + \
                ",DBC_RS.SOURCE_CITATION SOURCE_CITATION " + \
                ",DBC_SO.SUB_ORGANIZATION SUB_ORGANIZATION " + \
                ",DBC_RS.TEMPORAL_COVERAGE TEMPORAL_COVERAGE " + \
                ",DBC_RT.RESOURCE_TYPE_NAME RESOURCE_TYPE_NAME " + \
                ",DBC_RS.FEATURE_CLASS_NAME FEATURE_CLASS_NAME " + \
                ",DBC_LT.LICENSE_TYPE_ID LICENSE_ID " + \
                ",DBC_MP.LAYER_NAME MAP_PREVIEW_LAYER_NAME " + \
                ",DBC_MP.LATITUDE MAP_PREVIEW_LATITUDE " + \
                ",DBC_MP.LONGITUDE MAP_PREVIEW_LONGITUDE " + \
                ",DBC_MP.ZOOM_LEVEL MAP_PREVIEW_ZOOM_LEVEL " + \
                ",DBC_MP.SERVICE_URL MAP_PREVIEW_SERVICE_URL " + \
                ",TO_CHAR(DBC_RS.DATE_MODIFIED, 'YYYY-MM-DD')  AS DATE_MODIFIED" \
                ",TO_CHAR(DBC_RS.DATE_PUBLISHED, 'YYYY-MM-DD')  AS DATE_PUBLISHED" \
                ",TO_CHAR(DBC_RS.DATE_ADDED, 'YYYY-MM-DD')  AS DATE_ADDED" \
                ",DBC_DC.DISPLAY_NAME " + \
                ",DBC_DC.DISPLAY_EMAIL " + \
                ",DBC_RS.RESOURCE_STATE " + \
                ",DBC_RS.DISCOVERY_UID DISCOVERY_ID " \
                "FROM APP_DATABC.DBC_RESOURCE_SETS DBC_RS " + \
                ",APP_DATABC.DBC_CREATOR_ORGANIZATIONS DBC_CO " + \
                ",APP_DATABC.DBC_CREATOR_SECTORS DBC_CS " + \
                ",APP_DATABC.DBC_LICENSE_TYPES DBC_LT " + \
                ",APP_DATABC.DBC_MAP_PREVIEWS DBC_MP " + \
                ",APP_DATABC.DBC_RESOURCE_TYPES DBC_RT " + \
                ",APP_DATABC.DBC_SUB_ORGANIZATIONS DBC_SO "+ \
                ",APP_DATABC.DBC_DISPLAY_CONTACTS DBC_DC " + \
                ",(select RESOURCE_SET_ID,min(DISPLAY_CONTACT_ID) DISPLAY_CONTACT_ID from APP_DATABC.DBC_DISPLAY_CONTACTS " + \
                "group by RESOURCE_SET_ID) DBC_Dc_MIN " + \
                "WHERE DBC_RS.SUB_ORGANIZATION_ID=DBC_SO.SUB_ORGANIZATION_ID " + \
                "AND DBC_CO.CREATOR_ORGANIZATION_ID=DBC_SO.CREATOR_ORGANIZATION_ID " + \
                "AND DBC_LT.LICENSE_TYPE_ID=DBC_RS.LICENSE_TYPE_ID " + \
                "AND DBC_MP.RESOURCE_SET_ID(+)=DBC_RS.RESOURCE_SET_ID " + \
                "AND DBC_RT.RESOURCE_TYPE_ID=DBC_RS.RESOURCE_TYPE_ID " + \
                "AND DBC_CS.CREATOR_SECTOR_ID=DBC_SO.CREATOR_SECTOR_ID " + \
                "AND DBC_DC_MIN.RESOURCE_SET_ID(+)=DBC_RS.RESOURCE_SET_ID " + \
                "AND DBC_DC.DISPLAY_CONTACT_ID(+)=DBC_DC_MIN.DISPLAY_CONTACT_ID "
#                "AND DBC_RT.RESOURCE_TYPE_NAME='Geospatial Dataset'"
    
    
    cur = con.cursor()
    cur.execute(edc_auery)
    data = cur.fetchall()
    
    total_number_of_records = len(data)
    
    
    index = 0
    records_created = 0
    
    previous_count = 0;
    for name in record_dict.keys():
        previous_count = previous_count + record_dict[name]
    
    print previous_count
    
    #Create ODSI error file
    error_file = open('ODSI_errors.txt', 'a') 
    
#    for result in data:
    for result in data:
        try:        
            if index < previous_count :
                index += 1
                continue
        
            edc_record = {}
            edc_record['edc_state'] = result[21]
            
            # If this is record exists in discovery ignore it
            # The record exists in discovery if either DISCOVERY_UID or FEATURE_CLASS_NAME is not null.
            #Also ignore DRAFT records
            if (not result[2]) or result[9] or result[22] or edc_record['edc_state'] == 'DRAFT':
#            if (not result[2]) :
                index += 1
                continue
        
        
            title = result[2]
        
            edc_record['name'] = get_record_name(record_dict, title);
            edc_record['title'] = title
        
        # Set the state of record
        
        
            license_id = str(result[10])
        
            if license_id == '1' :
                edc_record['license_id'] = '2'
            elif license_id == '2' :
                edc_record['license_id'] = '21'
            elif  license_id == '3' or license_id == '4' :
                edc_record['license_id'] = '22'
            elif  license_id == '5':
                edc_record['license_id'] = '24'
            else :
                edc_record['license_id'] = '41'
            
            
            
            #edc_record['license_id'] = str(result[10])
        
            # Setting the record type
            type_dict = {'Application' : 'Application', 'Geospatial Dataset' : 'Geographic', 'Non-Geospatial Dataset' : 'Dataset', 'Web Service' : 'WebService'}
#            record_types = {'001' : 'Dataset', '002': 'Geographic Dataset', '003': 'Application', '004': 'Webservice / API'}
#            record_type_id = get_edc_tag_id('dataset_type_vocab', result[8])
            edc_record['type'] = type_dict[result[8]]
        
            edc_record['author'] = user_id        
            org = get_organization_id(result[1])
            edc_record['org'] = org
            edc_record['owner_org'] = org
            edc_record['sub_org'] = get_organization_id(result[6])
            edc_record['notes'] = result[3] or ' '
    
            if result[4]:
                # Extract the keywords(tags) names and add the list of tags to the record.
                keywords = result[4].split(',')
                edc_record['tags'] = [{'name' : keyword.strip()} for keyword in keywords]
        
                # Adding dataset dates
            dates = []
            if result[18] :
                dates.append({'type': '001', 'date': result[18], 'delete': '0'})
            if result[16] :
                dates.append({'type': '002', 'date': result[16], 'delete': '0'})
            if result[17] :
                dates.append({'type': '003', 'date': result[17], 'delete': '0'})
        
            edc_record['dates'] = dates
        
            # Adding dataset contacts
            contacts = []        
            contacts.append({'name': result[19], 'email': result[20], 'delete': '0', 'organization': org, 'role' : '002', 'private' : 'Display'})
        
            edc_record['contacts'] = contacts
        
            # Set record's resource status to completed
            edc_record['resource_status'] = '001'
        
            edc_record['security_class'] = '006'
        
            # Set record view audience and download audience to public
            edc_record['view_audience'] = '001'
            edc_record['download_audience'] = '001'
        
            edc_record['privacy_impact_assessment'] = 'N'
        
            edc_record['iso_topic_cat'] = '020'  # Not applicable
                
            edc_record['metadata_visibility'] = '002'
        
            edc_record['odsi_uid'] = result[0]
        
            edc_record['more_info'] = [{'link': result[5], 'delete': '0'}]
        
            # Set geospatial record specific properties
            if edc_record['type'] == 'Geographic':
                edc_record['layer_name'] = result[11]
                edc_record['preview_latitude'] = result[12]
                edc_record['preview_longitude'] = result[13]
                edc_record['preview_zoom_level'] = result[14]
                edc_record['preview_map_service_url'] = result[15]


            #Extract resource object name
            if (edc_record['type'] == 'Geographic') :
                object_name = result[9]
                if object_name and (object_name.startswith('WHSE_') or object_name.startswith('REG_')) :
                    edc_record['object_name'] = object_name
        
   
                
            record_id = result[0]
            
            resource_query = "SELECT * FROM APP_DATABC.DBC_RESOURCE_ACCESS_ODC_VW WHERE RESOURCE_SET_ID = '" + str(record_id) + "'"
            resource_cur = con.cursor()
            resource_cur.execute(resource_query)        
            resource_data = resource_cur.fetchall()
            
#            print 'Resource data : '
#            pprint.pprint(resource_data)
            
#            resource_records = [resource for resource in resource_data if resource[0] == record_id]
            resources = []
            for resource in resource_data:
            
                resource_rec = {}
                # Setting resource url to RESOURCE_ACCESS_URL from ODC 
                resource_rec['url'] = resource[3]
            
                # Setting resource name to PRODUCT_TYPE_NAME frrom ODC 
                if (edc_record['type'] != 'application'):
                    resource_rec['name'] = resource[2]
            
                # Setting resource format field value
                res_format = ""
            
                mimeType = (resource[1] or 'Unknown').lower()
                if mimeType == 'application/zip' :
                    res_format = 'ZIP'
                elif mimeType == 'application/json':
                    res_format = "JSON"
                elif mimeType == 'application/xls' :
                    res_format = 'XLS'
                elif mimeType == 'application/xml' or mimeType == 'application/rdf+xml':
                    res_format = 'XML'
                elif mimeType == 'text/csv' :
                    res_format = 'CSV'
                elif mimeType == 'text/plain' :
                    res_format = 'TXT'
                elif mimeType == 'application/vnd.google-earth.kmz' or mimeType == 'application/vnd.google-earth.kml+xml' :
                    res_format = 'KMZ'
                else:
                    res_format = 'Other'
            
                format_id = get_edc_tag_id('resource_format', res_format) 
                if (edc_record['type'] != 'application'):    
                    resource_rec['format'] = format_id
            
                # Setting Geospatial and Non-geospatial specific resource fields
                if edc_record['type'] == 'Geographic' or edc_record['type'] == 'Dataset':
                    #resource_rec['storage_format_description'] = resource[1] or 'Not given'
                    # resource_type = resource[2] or 'Unknown'
                    resource_type = 'Data'
                    resource_rec['edc_resource_type'] = get_edc_tag_id('resource_type', resource_type.strip())
                    access_method = resource[5] or 'Direct Access'
                    resource_rec['resource_storage_access_method'] = get_edc_tag_id('resource_storage_access_method', access_method.strip())
                    resource_rec['resource_storage_location'] = '002'
                
                    if edc_record['type'] == 'Geographic':
                        resource_rec['projection_name'] = ' '
            
                # Set record's resource update cycle 
                update_cycle = ''
                if result[7] :
                    update_cyle_str = result[7].lower()
                else:
                    update_cyle_str = 'monthly'
                    
                if 'day' in update_cyle_str or 'daily' in update_cyle_str:
                    update_cycle = 'daily'
                elif 'week' in update_cyle_str:
                    update_cycle = 'weekly'
                elif 'month' in update_cyle_str:
                    update_cycle = 'montly'
                elif 'quarterly' in update_cyle_str:
                    update_cycle = 'quarterly'
                elif 'biannually' in update_cyle_str or 'semi-annually' in update_cyle_str or 'biannual' in update_cyle_str:
                    update_cycle = 'biannually'
                elif 'annual' in update_cyle_str or 'year' in update_cyle_str:
                    update_cycle = 'annually'
                elif 'needed' in update_cyle_str or 'as required' in update_cyle_str or 'as necessary' in update_cyle_str :
                    update_cycle = 'asNeeded'
                elif 'occasional' in update_cyle_str or 'irregular' in update_cyle_str:
                    update_cycle = 'irregular'
                elif 'notplanned' in update_cyle_str :
                    update_cycle = 'notPlanned'
                elif 'periodic' in update_cyle_str or 'continual' in update_cyle_str:
                    update_cycle = 'continual'
                else:
                    update_cycle = 'monthly'
                    
                resource_rec['resource_update_cycle'] = get_edc_tag_id('resource_update_cycle', update_cycle)
        
        
                # Add the current resource record to the list of dataset resources     
                resources.append(resource_rec)
        
            # Add the list of dataset resources to the dataset
            edc_record['resources'] = resources    
        
#            pprint.pprint(edc_record)
            
            (record_info, errors) = edc_package_create(edc_record)
        
            if  record_info :
                records_created += 1
            else :
                pprint.pprint(errors)
                
                error_file.write('Error in importing record with UID : ' + str(result[0]) + '\n')
                error_file.write('Record info :\n')
                json.dump(edc_record, error_file)
                error_file.write('\nError details :')
                json.dump(errors, error_file)
                error_file.write('\n\n------------------------------------------------------------------------------------------------------------------------------------\n\n')
            index = index + 1
        
        except Exception, e:
            print str(e)
            error_file.write('Exception in importing record with UID ' + str(result[0])) + '\n'
            pass
    
    con.close()
    
    print "Total number of records : ", total_number_of_records
    print "Records created : ", records_created

    
#    save_record_dict(record_dict, "odsi_dict.json")


def get_organization(org_str):
    
    #Get the organization type code (BCGOV, BCAGENCY, NONGOV, MUNIC, ...)
    prefix = org_str.split(' ', 1)[0]
    prefix_len = len(prefix)
    
    org_code = ''
    org_titles = {
                    'AL' : 'Ministry of Agriculture',
                    'ARR': 'Ministry of Aboriginal Relations and Reconciliation',   
                    'CSCD': 'Ministry of Community, Sport and Cultural Development',
                    'ED': 'Ministry of Education',
                    'EMPR': 'Ministry of Energy and Mines',
                    'ENV': 'Ministry of Environment',
                    'FLNRO': 'Ministry of Forests, Lands and Natural Resource Operations',
                    'FOR' : 'Ministry of Forests, Lands and Natural Resource Operations',
                    'HLS' : 'Ministry of Health',
                    'HLTH': 'Ministry of Health',
                    'ILMB': 'Integrated Land Management Bureau', 
                    'JAG': 'Ministry of Justice',
                    'LCS': "Ministry of Technology, Innovation and Citizens Services",
                    'MEM': 'Ministry of Energy and Mines',
                    'MCFD': 'Ministry of Children and Family Development',
                    'MOT': 'Ministry of Transportation and Infrastructure',
                    'MSDSI': 'Ministry of Social Development and Social Innovation',
                    'NGD' : 'Ministry of Natural Gas Development',
                    'PSSG': 'Public Safety and Solicitor General',
                    'TCA': 'Ministry of Jobs, Tourism and Skills Training'                 
                }
    
    org_title = None
    sub_org_title = None
    
    if prefix == 'BCGOV':
        org_code = org_str.split(' ', 2)[1]
        org_title = org_titles[org_code]
        sub_org_index = len(org_code) + 7
        sub_org_title = org_str[sub_org_index:]
    elif prefix == 'CDNGOV':
        org_title = 'Government of Canada'
        sub_org_title =  org_str[7:]
    elif prefix == 'BCAGENCY':
        org_title = org_str[9:]
        if org_title.startswith('Agricultural Land Commission'):
            sub_org_title = org_title
            org_title = 'Ministry of Agriculture'
        elif org_title.startswith('Environmental Assessment Office'):
            sub_org_title = 'Environmental Assessment Office'
            org_title = 'Ministry of Environment'
        elif org_title.startswith('Elections British Columbia'):
            sub_org_title = 'Elections British Columbia'
            org_title = 'Ministry of Technology, Innovation and Citizens Services'
        elif org_title.startswith('Oil and Gas Commission') :
            sub_org_title = 'Oil and Gas Commission'
            org_title = 'Ministry of Natural Gas Development'
        else:
            sub_org_title = ''        
    elif prefix == 'NONGOV' or prefix == 'MUNIC':
        org_title = org_str[prefix_len+1:]
        sub_org_title = ''
    elif prefix == 'OTHER':
        org_title = 'BC Government'
        sub_org_title = ''
    else :
        pass
    
    return (org_title, sub_org_title)


def load_common_records() :
    
    with open('common_records.txt', 'r') as common_records_file :
        common_records = [line.rstrip('\n') for line in common_records_file]
        
    return common_records

def import_discovery_records(con, record_dict):
    
    #Required for email validation
    from lepl.apps.rfc3696 import Email
    is_valid_email = Email()
    
    common_uids = load_common_records()
    
    user_id = get_user_id(user_name)
    
    edc_query = "SELECT dat.sv_2 Title, " \
                "dat.xml_data.extract('//E9286/text()').getStringVal() Description, " \
                "SUBSTR(dat.xml_data.extract('//E9254/text()').getStringVal(),1,300) Data_Custodian_organization, " \
                "st.state_name, " \
                "dat.xml_data.extract('//E9288/text()').getStringVal() Purpose, " \
                "metastar.getKeywords(dat.record_uid) Keywords, " \
                "SUBSTR(dat.xml_data.extract('//E9292/text()').getStringVal(),1,105) Resource_Status, " \
                "metastar.getContactNames(dat.record_uid) Contact_Name, " \
                "metastar.getContactEmails(dat.record_uid) Contact_Email, " \
                "metastar.getContactOrganization(dat.record_uid) Contact_Organization, " \
                "dat.xml_data.extract('//E9342/text()').getStringVal() MAINT_FREQ_CODE, " \
                "SUBSTR(dat.xml_data.extract('//E11266/text()').getStringVal(),1,4) DataViewPubl, " \
                "SUBSTR(dat.xml_data.extract('//E11404/text()').getStringVal(),1,4) DataDistPubl, " \
                "SUBSTR(dat.xml_data.extract('//E11436/text()').getStringVal(),1,6) PIAComplete, " \
                "to_number(dat.RECORD_UID) RECORD_UID , " \
                "dat.xml_data.extract('//E9742/text()').getStringVal() Projection_Name, " \
                "to_char(to_date(dat.xml_data.extract('//E10000/text()').getStringVal(),'YYYY-MM-DD'), 'YYYY-MM-DD') Beginning_Date, " \
                "to_char(to_date(dat.xml_data.extract('//E10002/text()').getStringVal(),'YYYY-MM-DD'), 'YYYY-MM-DD') End_Date, " \
                "dat.xml_data.extract('//E9514/text()').getStringVal() Lineage_Statement, " \
                "SUBSTR(dat.xml_data.extract('//E10330/text()').getStringVal(),1,3) IS_PUBLIC, " \
                "dat.xml_data.extract('//E10338/text()').getStringVal() Archive_Retention_Schedule, " \
                "to_char(to_date(dat.xml_data.extract('//E10340/text()').getStringVal(),'YYYY-MM-DD'), 'YYYY-MM-DD') Retention_Expiry_Date, " \
                "dat.xml_data.extract('//E10348/text()').getStringVal() Source_Data_Path, " \
                "SUBSTR(dat.xml_data.extract('//E9866/text()').getStringVal(),1,105) Resource_Type, " \
                "SUBSTR(dat.xml_data.extract('//E10284/text()').getStringVal(),1,750) Resource_Storage_Location, " \
                "metastar.getFeatureClassNames(dat.record_uid) Feature_Class_Names, " \
                "metastar.getFeatureClassDescriptions(dat.record_uid) Feature_Class_Descriptions, " \
                "metastar.getOnlineReferences(dat.record_uid) Online_References, " \
                "SUBSTR(dat.xml_data.extract('//E9388/text()').getStringVal(),1,300) Classification_Category, " \
                "metastar.getIsoCategory(dat.record_uid) ISO_Topic_Category, " \
                "to_char(dat.record_createdate, 'YYYY-MM-DD')  CREATEDATE, " \
                "to_char(to_date(dat.xml_data.extract('//E9260/text()').getStringVal(),'YYYY-MM-DD'), 'YYYY-MM-DD') DATE_MODIFIED, " \
                "substr(dat.xml_data.extract('//E11282/text()').getStringVal(),1,3) License_data, " \
                "dat.xml_data.extract('//E9350/text()').getStringVal() Resource_Storage_Description, " \
                "dat.xml_data.extract('//E10050/text()').getStringVal() object_name, " \
                "SUBSTR(dat.xml_data.extract('//E9682/text()').getStringVal(),1,450) UNIQUE_METADATA_URL, " \
                "usr.description OWNER_DESC, " \
                "usr.email OWNER_EMAIL, " \
                "dat.sv_5 RECORD_TYPE " \
                "FROM metastar.bat_records_104 dat, " \
                "metastar.bat_users usr, " \
                "metastar.bat_states st " \
                "WHERE dat.state_uid IN (164,166,168,172) " \
                "AND usr.user_uid = dat.user_uid " \
                "AND st.state_uid = dat.state_uid "  
#                /* state is Draft, Approve, Published or ZPublished */

    cur = con.cursor()
    data = cur.execute(edc_query)
#    total_number_of_records = 0   
            
#    record_dict = load_record_dict("discovery_dict.json") or {}
    previous_count = 0;
    for name in record_dict.keys():
        previous_count = previous_count + record_dict[name]
    
    index = 0
    records_created = 0
    
    
    
    #Create error file
    error_file = open('Discovery_errors.txt', 'a') 
    
    for result in data:
        try :
            if index < previous_count :
                index += 1
                continue
            
            #Ignore records available in ODSI
            if str(result[14]) in common_uids :
                index += 1
                continue
        
            edc_record = {}

            state_convert_dict = {'Draft': 'DRAFT', 'Approve': 'PENDING PUBLISH', 'Published': 'PUBLISHED', 'ZPublished': 'ARCHIVED'}
            edc_record['edc_state'] = state_convert_dict[result[3]]

            # Ignore records with null title, DRAFT records or Theme records (Records with Theme in title).
            if not result[0] or edc_record['edc_state'] == 'DRAFT' or '(Theme)' in result[0]:
                index += 1
                continue
        
            title = result[0].strip()
            
            #Remove (DEPRECATED) from the record title
            if title.startswith('(DEPRECATED) ') :
                title = title.replace('(DEPRECATED) ', '').strip()
                edc_record['notes'] = 'DEPRECATED - The resource(s) that this record refers is obsolete and may be scheduled for retirement. Please see the Replacement Record reference in the Data Currency / Update section.'
            else :
                edc_record['notes'] = result[1] or ' '
                
            edc_record['name'] = get_record_name(record_dict, title);
            edc_record['title'] = title
        
        
            edc_record['purpose'] = result[4]
        
            if result[32] and result[32].lower == 'yes':
                edc_record['license_id'] = "2"
            else:
                edc_record['license_id'] = "22"
        
            edc_record['type'] = 'Geographic'
        
            edc_record['author'] = user_id
                
            (org_title, sub_org_title) = get_organization(result[2])
            edc_record['org'] = get_organization_id(org_title)
            edc_record['owner_org'] = edc_record['org']
            edc_record['sub_org'] = get_organization_id(sub_org_title)
    
            # Extract the keywords(tags) names and add the list of tags to the record.
            if result[5] :
                keywords = result[5].split(',')
            
                edc_record['tags'] = [{'name' : re.sub('[^ A-Za-z0-9_-]+', '', keyword)} for keyword in keywords]
        
            resource_status = result[6] or 'onGoing'
            # Set record's resource status to completed
            edc_record['resource_status'] = get_edc_tag_id('resource_status', resource_status)
        
            contact_names = []
            contact_emails = []
            contact_orgs = []
            if result[7]:
                contact_names = result[7].split(',')
            if result[8]:
                contact_emails = result[8].split(',')
            if result[9]:
                contact_orgs = result[9].split(',')
        
            #Validate emails
            contact_emails = [contact_email if is_valid_email(contact_email) else 'databc@gov.bc.ca' for contact_email in contact_emails]
            
            # Adding dataset contacts
            contacts = []
        
            contact_len = min(len(contact_names), len(contact_emails), len(contact_orgs))
        
            for i in range(contact_len): 
#                (contact_org, contact_sub_org) = get_organization(contact_orgs[i])       
                contacts.append({'name': contact_names[i], 'email': contact_emails[i], 'delete': '0', 'organization': edc_record['org'], 'role' : '002', 'private' : 'Display'})
        
            edc_record['contacts'] = contacts
        
            # Set record view audience and download audience to public
            if (result[11] and result[11].lower() == 'yes'):
                edc_record['view_audience'] = '001'
            else :
                edc_record['view_audience'] = '002'
        
            if (result[12] and result[12].lower() == 'yes'):
                edc_record['download_audience'] = '001' 
            else:
                edc_record['download_audience'] = '002'  
        
            if (result[13] and result[13] and result[12] == 'TRUE'):
                edc_record['privacy_impact_assessment'] = 'Y'
            else :
                edc_record['privacy_impact_assessment'] = 'N'
        
            edc_record['iso_topic_cat'] = '020'  # Not applicable
        
            edc_record['metastar_uid'] = str(result[14])
        
            edc_record['lineage_statement'] = result[18]
        
            if result[19].lower().startswith('tru'):       
                edc_record['metadata_visibility'] = '002'
            else:
                edc_record['metadata_visibility'] = '001'
        
            edc_record['archive_retention_schedule'] = result[20]
            edc_record['retention_expiry_date'] = result[21]
            edc_record['source_data_path'] = result[22]
        
            # Adding dataset dates
            dates = []
            if result[30] :
                dates.append({'type': '001', 'date': result[30], 'delete': '0'})
            if result[31] :
                dates.append({'type': '002', 'date': result[31], 'delete': '0'})
        
            edc_record['dates'] = dates

            #security_class = result[28]
            security_class = 'HIGH-CONFEDENTIAL'
        
            security_dict = {'topSecret': '001', 'secret': '002', 'restricted' : '003', 'confidential': '004', 'unclassified' : '006'}
            
            if security_class in security_dict :
                edc_record['security_class'] = security_dict[security_class]
            else :
                edc_record['security_class'] = '007'
        
            iso_topic_cat = (result[29] or 'unknown').split(',')[0]    
            edc_record['iso_topic_category'] = get_edc_tag_id('iso_topic_category', iso_topic_cat)

        
        
            resources = []
            
            resource_rec = {}
            
            resource_rec['name'] = result[0]
            resource_rec['url'] = ' '
            
            resource_rec['format'] = 'SHP'
        
            if result[15] :
                resource_rec['projection_name'] = result[15]
            else :
                resource_rec['projection_name'] = ' '
        
            resource_type = result[23] or 'Data'
            resource_rec['edc_resource_type'] = get_edc_tag_id('resource_type', resource_type.strip())
        

            # Set record's resource update cycle
            update_cycle = result[10] or 'unknown'
            resource_rec['resource_update_cycle'] = get_edc_tag_id('resource_update_cycle', update_cycle)
        
            
            access_method = 'Service'
            resource_rec['resource_storage_access_method'] = get_edc_tag_id('resource_storage_access_method', access_method.strip())
            resource_rec['resource_storage_location'] = '001'  # Get the tag ID for resource storage location
            
            resource_rec['data_collection_start_date'] = result[16]
            resource_rec['data_collection_end_date'] = result[17]
            
            # Add the current resource record to the list of dataset resources     
            resources.append(resource_rec)
        
            # Add the list of dataset resources to the dataset
            edc_record['resources'] = resources    
            #media_cur.close()
        
#            pprint.pprint(edc_record) 

            #Extract resource object name
            object_name = result[34]
            
            if object_name and (object_name.startswith('WHSE_') or object_name.startswith('REG_')) :
                edc_record['object_name'] = object_name
        
   

            # Adding dataset features        
            features = []
            if (result[25]):
                feature_class_names = result[25].split('|')
                feature_class_desciptions = []
                description_len = 0
                if (result[26]) :
                    feature_class_description_str = ''
                    if isinstance(result[26], str):
                        feature_class_description_str = result[26]
                    else :
                        feature_class_description_str = result[26].read()                
                    feature_class_desciptions = feature_class_description_str.split('|')
                    
                    description_len = len(feature_class_desciptions)
                
                for i in range(len(feature_class_names)):
                    features.append({'name' : feature_class_names[i]})
                    if description_len > i :
                        features[i]['description'] = feature_class_desciptions[i]
            edc_record['feature_types'] = features
        
            more_info = []
            if (result[27]) :
                more_info_links_str = ''
                if isinstance(result[27], str):
                    more_info_links_str = result[27]
                else :
                    more_info_links_str = result[27].read()                
                more_info_links = more_info_links_str.split('|')
        
                for i in range(len(more_info_links)):
                    more_info.append({'link': more_info_links[i], 'delete': '0'})
        
            edc_record['more_info'] = more_info
        
#            pprint.pprint(edc_record)
            (record_info, errors) = edc_package_create(edc_record)
            
            if  record_info :
                records_created += 1
            else :
                pprint.pprint(errors)
                
                error_file.write('Error in importing record with UID : ' + str(result[14]) + '\n')
                error_file.write('Record info :\n')
                json.dump(edc_record, error_file)
                error_file.write('\nError details :')
                json.dump(errors, error_file)
                error_file.write('\n\n------------------------------------------------------------------------------------------------------------------------------------\n\n')
            index = index + 1
        except:
            error_file.write('Exception in importing record with UID ' + str(result[14])) + '\n'
            pass
    
    print "Total number of records : ", index
    print "Records created : ", records_created
    con.close()
    error_file.close()
#    save_record_dict(record_dict, "discovery_dict.json")
    
def import_data():
    
    data_source = raw_input("Data source (ODC/Discovery): ") 
    con =  get_connection(data_source) 
     
    if data_source.lower() == 'odc' :
        dict_file = 'odsi_dict.json'
    elif data_source.lower() == 'discovery' :
        dict_file = 'discovery_dict.json'

    record_dict = load_record_dict(dict_file) or {}
    
    try:
        if data_source.lower() == 'odc' :
            import_odc_records(con, record_dict)
        elif data_source.lower() == 'discovery' :
            import_discovery_records(con, record_dict)
        else :
            print "No data source is given."
    except:
        pass
    finally:
        save_record_dict(record_dict, dict_file)        
            
import_data()
