# Copyright  2015, Province of British Columbia 
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license 
 

import cx_Oracle
import urllib2
import urllib
import os
import sys
import json
import getpass

from base import import_properties

def get_connection(repo_name):
    
    SID = service_name = None

    if repo_name.lower() == 'odsi' :
        host = import_properties['odsi_host']
        port = import_properties['odsi_port']
    
        if 'odsi_sid' in import_properties :
            SID = import_properties['odsi_sid']
        else :
            service_name = import_properties['odsi_service_name']
        user_name = import_properties['odsi_username']
        password = import_properties['odsi_password']
    else :
        host = import_properties['discovery_host']
        port = import_properties['discovery_port']
    
        if 'discovery_sid' in import_properties :
            SID = import_properties['discovery_sid']
        else :
            service_name = import_properties['discovery_service_name']
        user_name = import_properties['discovery_username']
        password = import_properties['discovery_password']
        
    
    if service_name :
        connection_str = user_name + '/' + password + '@' + host + '/' + service_name
        
        con = cx_Oracle.connect(connection_str)
    else :
        dsn_tns = cx_Oracle.makedsn(host, port, SID)    
        con = cx_Oracle.connect(user_name, password, dsn_tns)
                
    return con


def get_discovery_record(con, record_uid):

    '''
    Fetches the discovery record from database
    '''
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
                "to_number(dat.RECORD_UID) RECORD_UID, " \
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
                "SUBSTR(dat.xml_data.extract('//E11282/text()').getStringVal(),1,3) License_data, " \
                "dat.xml_data.extract('//E9350/text()').getStringVal() Resource_Storage_Description, " \
                "dat.xml_data.extract('//E10050/text()').getStringVal() object_name, " \
                "SUBSTR(dat.xml_data.extract('//E9682/text()').getStringVal(),1,450) UNIQUE_METADATA_URL, " \
                "to_number(dat.xml_data.extract('//E9438/text()').getStringVal()) Extent_North, " \
                "to_number(dat.xml_data.extract('//E9436/text()').getStringVal()) Extent_South, " \
                "to_number(dat.xml_data.extract('//E9434/text()').getStringVal()) Extent_East, " \
                "to_number(dat.xml_data.extract('//E9432/text()').getStringVal()) Extent_West, " \
                "dat.xml_data.extract('//E10424/text()').getStringVal() product_type, " \
                "dat.xml_data.extract('//E9856/text()').getStringVal() product_id, " \
                "dat.xml_data.extract('//E9244/text()').getStringVal() record_language, " \
                "dat.xml_data.extract('//E9246/text()').getStringVal() record_characterSet, " \
                "dat.xml_data.extract('//E9262/text()').getStringVal() standard_name, " \
                "dat.xml_data.extract('//E9264/text()').getStringVal() standard_ersion, " \
                "usr.description OWNER_DESC, " \
                "usr.email OWNER_EMAIL, " \
                "dat.sv_5 RECORD_TYPE, " \
                "to_char(dat.record_modifydate, 'YYYY-MM-DD') record_modified, " \
                "metastar.getResourceDates(dat.record_uid) resource_dates " \
                "FROM metastar.bat_records_104 dat, " \
                "metastar.bat_users usr, " \
                "metastar.bat_states st " \
                "WHERE dat.state_uid IN (164,166,168,172) " \
                "AND usr.user_uid = dat.user_uid " \
                "AND st.state_uid = dat.state_uid " \
                "AND dat.RECORD_UID = " + record_uid
#                /* state is Draft, Approve, Published or ZPublished */

    cur = con.cursor()

    cur.execute(edc_query)
    

    return cur.fetchone()

def add_discovery_data():
    import pprint

    con = get_connection('discovery')

    #Get discovery connection

    discovery_data = {}

    '''
        For each common record with metastar uid
        Get the record data from discovery
    '''
    with open('./data/common_records_uids.txt', 'r') as common_records_file :
        common_records_uids = [line.rstrip('\n') for line in common_records_file]

    for record_uid in common_records_uids :
        record_data = get_discovery_record(con, record_uid)
        if not record_data :
            continue

        #---------------------------------------------------- Access Constraints ------------------------------------------------
        metadata_visibility = 'IDIR'
        if record_data[19] and record_data[19].lower().startswith('tru'):
            metadata_visibility = 'Public'

        view_audience = 'Government'
        download_audience = 'Government'
        privacy_impact_assessment = 'No'

        if (record_data[11] and record_data[11].lower() == 'yes'):
            view_audience = 'Public'
        if (record_data[12] and record_data[12].lower() == 'yes'):
            download_audience = 'Public'

        if (record_data[13] and record_data[13] == 'TRUE'):
            privacy_impact_assessment = 'Yes'

        #---------------------------------------------------- Iso topic Category ------------------------------------------------
        iso_topic_cat = (record_data[29] or 'unknown').split(',')
        lineage_statement =  record_data[18]
        source_data_path = record_data[22]

        archive_retention_schedule = record_data[20]
        retention_expiry_date = record_data[21]

        #---------------------------------------------------- Security Classification ------------------------------------------------
        security_class = record_data[28]

        security_dict = {'topSecret': 'MEDIUM-SENSITIVITY', 'secret': 'MEDIUM-SENSITIVITY', 'restricted' : 'MEDIUM-SENSITIVITY', 'confidential': 'MEDIUM-SENSITIVITY', 'unclassified' : 'LOW-PUBLIC'}

        if security_class in security_dict :
            security_class = security_dict[security_class]
        else :
            security_class = 'LOW-PUBLIC'

        resource_status = record_data[6] or 'completed'
        #------------------------------------------------------ Dataset Extent --------------------------------------------------
        #Get dataset map extent coordinates
        if (record_data[36] and record_data[37] and record_data[38] and record_data[39]) :
            north = record_data[36]
            south = record_data[37]
            east = record_data[38]
            west = record_data[39]

            spatial_extent = {"type":"Polygon",
                              "coordinates":[[[west, south], [west, north], [east, north], [east, south],[west, south]]]
                             }
            spatial = json.dumps(spatial_extent)

            west_bound_longitude = west
            east_bound_longitude = east
            south_bound_latitude = south
            north_bound_latitude = north

        resource_type = record_data[23] or 'Data'
        edc_resource_type = resource_type.strip()


        # Set record's resource update cycle
        resource_update_cycle = record_data[10] or 'unknown'

        data_collection_start_date = record_data[16]
        data_collection_end_date = record_data[17]

        purpose = record_data[4]

        #------------------------------------------------------------------<< Metadata Information >>-----------------------------------------------------------------
        metadata_language = record_data[42] or 'eng'
        metadata_character_set = record_data[43] or 'utf8'
        metadata_standard_name = record_data[44]    or 'North American Profile of ISO 19115-1:2014 - Geographic information - Metadata (NAP-Metadata)' #Add default value here if there is any
        metadata_standard_version = record_data[45]  or 'n/a' #Add default value here if there is any

        #-----------------------------------------------------------------------<< Record Dates >>---------------------------------------------------------------------
        date_modified = record_data[49]
        date_created = record_data[30]


        # Adding dataset dates
        dates_of_data = []
            
        if record_data[50] :
            dates_of_data = record_data[50].split(',')
            
        date_type_dict = {'creation' : 'Created', 'revision' : 'Modified', 'publication': 'Published', 'archival' : 'Archived', 'destruction': 'Destroyed'}
        dates = []
            
        for date_of_data in dates_of_data :
            rec_date = date_of_data[:4] + '-' + date_of_data[4:6] + '-' + date_of_data[6:8]
            date_type = date_of_data[8:]
            date_type = date_type_dict[date_type]
            dates.append({'type': date_type, 'date': rec_date, 'delete': '0'})
                
        #---------------------------------------------------------------------<< Record Contacts >>----------------------------------------------------------------------
        from validate_email import validate_email
        
        contact_names = []
        contact_emails = []
        if record_data[7]:
            contact_names = record_data[7].split(',')
        if record_data[8]:
            contact_emails = record_data[8].split(',')
        #Validate emails
        contact_emails = [contact_email if (contact_email and validate_email(contact_email)) else 'data@gov.bc.ca' for contact_email in contact_emails]

        contact_names = [contact_name if contact_name else 'DataBC'  for contact_name in contact_names]
        # Adding dataset contacts
        contacts = []

        contact_len = min(len(contact_names), len(contact_emails))

        for i in range(contact_len):
            contacts.append({'name': contact_names[i], 'email': contact_emails[i], 'delete': '0', 'role' : 'pointOfContact', 'private' : 'Display'})



        data_dict = {
                     'purpose' : purpose,
                     'resource_status' : resource_status,
                     'metadata_visibility' : metadata_visibility,
                     'view_audience' : view_audience,
                     'download_audience' : download_audience,
                     'privacy_impact_assessment' : privacy_impact_assessment,
                     'iso_topic_cat' : iso_topic_cat,
                     'lineage_statement': lineage_statement,
                     'source_data_path' : source_data_path,
                     'archive_retention_schedule': archive_retention_schedule,
                     'retention_expiry_date' : retention_expiry_date,
                     'spatial': spatial,
                     'west_bound_longitude': west_bound_longitude,
                     'east_bound_longitude': east_bound_longitude,
                     'south_bound_latitude': south_bound_latitude,
                     'north_bound_latitude': north_bound_latitude,
                     'edc_resource_type': edc_resource_type,
                     'resource_update_cycle': resource_update_cycle,
                     'data_collection_start_date' : data_collection_start_date,
                     'data_collection_end_date' : data_collection_end_date,
                     'security_class' : security_class,
                     'metadata_language' : metadata_language,
                     'metadata_character_set' : metadata_character_set,
                     'metadata_standard_name' : metadata_standard_name,
                     'metadata_standard_version' : metadata_standard_version,
                     'date_modified' : date_modified,
                     'date_created' : date_created,
                     'dates' : dates,
                     'contacts' : contacts
                     }
        discovery_data[str(record_uid)] = data_dict

    con.close()

    #Write the data dictionary to a file
    with open('./data/discovery_ODSI.json', 'w') as data_file:
        data_file.write(json.dumps(discovery_data))

def get_common_records():

    con = get_connection('ODSI')

    print 'Updating records from discovery ... '

    auery = "SELECT DBC_RS.RESOURCE_SET_ID RESOURCE_SET_ID " + \
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
                "AND DBC_DC.DISPLAY_CONTACT_ID(+)=DBC_DC_MIN.DISPLAY_CONTACT_ID " + \
                "AND DBC_RT.RESOURCE_TYPE_NAME='Geospatial Dataset'"


    cur = con.cursor()
    cur.execute(auery)
    data = cur.fetchall()


    #Create ODSI error file
    common_records_title_file = open('./data/common_records_titles.txt', 'w')
    common_records_uid_file = open('./data/common_records_uids.txt', 'w')

    common_records_title = []
    common_records_uid = []

    for result in data:
        
        #Check if the status of the record is draft :
        edc_state = result[21] or 'DRAFT'
        
        if edc_state == 'DRAFT' : continue

        # If this is record exists in discovery add it to the list
        if result[9] or result[22]:
            common_records_title.append(result[2])
            if result[22]:
                common_records_uid.append(result[22])

    for record_title in common_records_title :
        common_records_title_file.write('%s\n' % record_title)

    for record_uid in common_records_uid :
        common_records_uid_file.write('%s\n' % record_uid)


    common_records_title_file.close()
    common_records_uid_file.close()

def get_discovery_data():
    get_common_records()
    add_discovery_data()

    