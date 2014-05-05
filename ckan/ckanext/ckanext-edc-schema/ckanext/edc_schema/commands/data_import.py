import cx_Oracle
import urllib2
import urllib
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


def get_record_name(record_dict, title):
    name = re.sub('[^0-9a-zA-Z]+',' ', title)
    name = ' '.join(name.split())
    name = name.lower().replace(' ', '-')[:100]
    
    count = 0
    if name in record_dict :
        count = record_dict[name]
    count += 1
    record_dict[name] = count
    if count == 1:
        return name
    else:
        index = min(len(name), 96)
        return name[:index] + "-%03d" % count
    

def get_connection(data_source):
    
    if data_source.lower() == 'odc' :
        host = 'sponde.bcgov'
        port = 1521
        SID = 'BCGWDLV'    
        user_name = 'APP_DATABC'
        password = 'i85dg07'
    elif data_source.lower() == 'discovery' :
        user_name = 'metastar'
        host = 'slkux12.env.gov.bc.ca'
        port = 1521
        SID = 'BCGWDLV'
        password = 'blueb1rd'
    else :
        print "No data source is given."
    
#    password = getpass.getpass("Password:")
    
    
    dsn_tns = cx_Oracle.makedsn(host, port, SID)
    
    con = cx_Oracle.connect(user_name, password, dsn_tns)
    
    return con


def import_odc_records(con):
    
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
                "FROM DBC_RESOURCE_SETS DBC_RS " + \
                ",DBC_CREATOR_ORGANIZATIONS DBC_CO " + \
                ",DBC_CREATOR_SECTORS DBC_CS " + \
                ",DBC_LICENSE_TYPES DBC_LT " + \
                ",DBC_MAP_PREVIEWS DBC_MP " + \
                ",DBC_RESOURCE_TYPES DBC_RT " + \
                ",DBC_SUB_ORGANIZATIONS DBC_SO "+ \
                ",DBC_WMS_LAYERS DBC_WL " + \
                ",DBC_DISPLAY_CONTACTS DBC_DC " + \
                ",(select RESOURCE_SET_ID,min(DISPLAY_CONTACT_ID) DISPLAY_CONTACT_ID from DBC_DISPLAY_CONTACTS " + \
                "group by RESOURCE_SET_ID) DBC_Dc_MIN " + \
                "WHERE DBC_RS.SUB_ORGANIZATION_ID=DBC_SO.SUB_ORGANIZATION_ID " + \
                "AND DBC_CO.CREATOR_ORGANIZATION_ID=DBC_SO.CREATOR_ORGANIZATION_ID " + \
                "AND DBC_LT.LICENSE_TYPE_ID=DBC_RS.LICENSE_TYPE_ID " + \
                "AND DBC_WL.RESOURCE_SET_ID(+)=DBC_RS.RESOURCE_SET_ID " + \
                "AND DBC_MP.RESOURCE_SET_ID(+)=DBC_RS.RESOURCE_SET_ID " + \
                "AND DBC_RT.RESOURCE_TYPE_ID=DBC_RS.RESOURCE_TYPE_ID " + \
                "AND DBC_CS.CREATOR_SECTOR_ID=DBC_SO.CREATOR_SECTOR_ID " + \
                "AND DBC_DC_MIN.RESOURCE_SET_ID(+)=DBC_RS.RESOURCE_SET_ID " + \
                "AND DBC_DC.DISPLAY_CONTACT_ID(+)=DBC_DC_MIN.DISPLAY_CONTACT_ID "
    
    
    cur = con.cursor()
    cur.execute(edc_auery)
    data = cur.fetchall()
    
    total_number_of_records = len(data)
    
    
    resource_query = "select * from APP_DATABC.DBC_RESOURCE_ACCESS_ODC_VW "
    resource_cur = con.cursor()
    resource_cur.execute(resource_query)        
    resource_data = resource_cur.fetchall()

    
    number_of_records_created = 0
    
    record_dict = {}

    for result in data:
        
        
        #If this is record exists in discovery ignore it
        #The record exists in discovery if either DISCOVERY_UID or FEATURE_CLASS_NAME is not null.
        if (not result[2]) or result[9] or result[22] :
            continue
        
        edc_record = {}
        
        title = result[2]
        
        edc_record['name'] = get_record_name(record_dict, title);
        edc_record['title'] = title
        
        #Set the state of record
        
        edc_record['edc_state'] = result[21]
        
        edc_record['license_id'] = str(result[10])
        
        #Setting the record type
        record_types = {'001' : 'application', '002': 'nongeospatial','003': 'geospatial',  '004': 'webservice'}
        record_type_id = get_edc_tag_id('dataset_type_vocab', result[8])
        edc_record['type'] = record_types[record_type_id]
        
        edc_record['author'] = user_id        
        org = get_organization_id(result[1])
        edc_record['org'] = org
        edc_record['owner_org'] = org
        edc_record['sub_org'] = get_organization_id(result[6])
        edc_record['notes'] = result[3] or ' '
    
        if result[4]:
        #Extract the keywords(tags) names and add the list of tags to the record.
            keywords = result[4].split(',')
            edc_record['tags'] = [{'name' : keyword} for keyword in keywords]
        
        #Adding dataset dates
        dates = []
        if result[18] :
            dates.append({'type': '001', 'date': result[18], 'delete': '0'})
        if result[16] :
            dates.append({'type': '002', 'date': result[17], 'delete': '0'})
        if result[17] :
            dates.append({'type': '003', 'date': result[16], 'delete': '0'})
        
        edc_record['dates'] = dates
        
        #Adding dataset contacts
        contacts = []        
        contacts.append({'name': result[19], 'email': result[20], 'delete': '0', 'organization': org, 'role' : '002'})
        
        edc_record['contacts'] = contacts
        
        #Set record's resource status to completed
        edc_record['resource_status'] = '001'
        
        #Set record's resource update cycle 
        update_cycle = ''
        update_cyle_str = result[7].lower()
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
            update_cycle = 'unknown'
        edc_record['resource_update_cycle'] = get_edc_tag_id('resource_update_cycle', update_cycle)
        
        
        #Set record's security classification to "Restricted to Named User"
        edc_record['security_class'] = '003'
        edc_record['bc_ocio'] = 'LOW-PUBLIC'
        
        #Set record view audience and download audience to public
        edc_record['view_audience'] = '001'
        edc_record['download_audience'] = '001'
        
        edc_record['privacy_impact_assessment'] = 'N'
        
        edc_record['iso_topic_cat'] = '020'   #Not applicable
                
        edc_record['metadata_visibility'] = '002'
        
        edc_record['odsi_uid'] = result[0]
        
        edc_record['more_info'] = [{'link': result[5], 'delete': '0'}]
        
        #Set geospatial record specific properties
        if edc_record['type'] == 'geospatial':
            edc_record['layer_name'] = result[11]
            edc_record['preview_latitude'] = result[12]
            edc_record['preview_longtude'] = result[13]
            edc_record['zoom_level'] = result[14]
            edc_record['preview_map_service_url'] = result[15]

                
        record_id = result[0]
        
        resource_records = [resource for resource in resource_data if resource[0] == record_id]
        resources = []
        for resource in resource_records:
            
            resource_rec = {}
            #Setting resource url to RESOURCE_ACCESS_URL from ODC 
            resource_rec['url'] = resource[3]
            
            #Setting resource name to PRODUCT_TYPE_NAME frrom ODC 
            if (edc_record['type']  != 'application'):
                resource_rec['name'] = resource[2]
            
            #Setting resource format field value
            format = ""
            
            mimeType = (resource[1] or 'Unknown').lower()
            if mimeType == 'application/zip' :
                format = 'Spreadsheet-ZIP'
            elif mimeType == 'application/json':
                format = "Delimited text-JSON"
            elif mimeType == 'application/xls' :
                format = 'Spreadsheet-XLS'
            elif mimeType == 'application/xml' or mimeType == 'application/rdf+xml':
                format = 'XML'
            elif mimeType == 'text/csv' :
                format = 'Delimited text-CSV'
            elif mimeType == 'text/plain' :
                format = 'Delimited text-TXT'
            elif mimeType == 'application/vnd.google-earth.kmz' or mimeType == 'application/vnd.google-earth.kml+xml' :
                format = 'KMZ'
            else:
                format = 'Unknown'
            
            format_id = get_edc_tag_id('resource_format', format) 
            if (edc_record['type'] != 'application'):    
                resource_rec['format'] = format_id
            
            #Setting Geospatial and Non-geospatial specific resource fields
            if edc_record['type'] == 'geospatial' or edc_record['type'] == 'nongeospatial':
#                resource_rec['storage_format_description'] = resource[1] or 'Not given'
                #resource_type = resource[2] or 'Unknown'
                resource_type = 'Data'
                resource_rec['edc_resource_type'] = get_edc_tag_id('resource_type', resource_type.strip())
                access_method = resource[5] or 'Unknown'
                resource_rec['resource_storage_access_method'] = get_edc_tag_id('resource_storage_access_method', access_method.strip())
                resource_rec['resource_storage_location'] = '002'
                
                if edc_record['type'] == 'geospatial':
                    resource_rec['projection_name'] = ' '
            
            #Add the current resource record to the list of dataset resources     
            resources.append(resource_rec)
        
        #Add the list of dataset resources to the dataset
        edc_record['resources'] = resources    
#        media_cur.close()
        
#        pprint.pprint(edc_record)   
        
        record_info = edc_package_create(edc_record)
        
        if record_info:
            number_of_records_created = number_of_records_created + 1
        else :
            print 'Error in creating record.'
        
        
    
    print "Total number of records : ", total_number_of_records
    print "Number of records created : ", number_of_records_created   
    con.close()


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

def import_discovery_records(con):
    
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
                "SUBSTR(dat.xml_data.extract('//E9682/text()').getStringVal(),1,450) UNIQUE_METADATA_URL, " \
                "usr.description OWNER_DESC, " \
                "usr.email OWNER_EMAIL, " \
                "dat.sv_5 RECORD_TYPE " \
                "FROM metastar.bat_records_104 dat, " \
                "metastar.bat_users usr, " \
                "metastar.bat_states st " \
                "WHERE dat.state_uid IN (164,166,168,172) " \
                "AND usr.user_uid = dat.user_uid " \
                "AND st.state_uid = dat.state_uid " \
                "AND SUBSTR(dat.xml_data.extract('//E9292/text()').getStringVal(),1,105) = 'historicalArchive'"   
#                /* state is Draft, Approve, Published or ZPublished */

    cur = con.cursor()
    data = cur.execute(edc_query)
    total_number_of_records = 0   
            
    number_of_records_created = 0
    index = 0
    record_dict = {}
    
    for result in data:
        edc_record = {}
        
        #Record title is required
        if not result[0]:
            continue
        
        title = result[0]
        edc_record['name'] = get_record_name(record_dict, title);
        edc_record['title'] = title
        
        edc_record['notes'] = result[1] or ' '
        #Set the state of record
        
        state_convert_dict = {'Draft': 'DRAFT', 'Approve': 'PENDING PUBLISH', 'Published': 'PUBLISHED', 'ZPublished': 'ARCHIVED'}
        edc_record['edc_state'] = state_convert_dict[result[3]]
        
        edc_record['purpose'] = result[4]
        
        if result[32] and result[32].lower == 'yes':
            edc_record['license_id'] = "2"
        else:
            edc_record['license_id'] = "22"
        
        edc_record['type'] = 'geospatial'
        
        edc_record['author'] = user_id
                
        (org_title, sub_org_title) = get_organization(result[2])
        edc_record['org'] = get_organization_id(org_title)
        edc_record['owner_org'] = edc_record['org']
        edc_record['sub_org'] = get_organization_id(sub_org_title)
    
        #Extract the keywords(tags) names and add the list of tags to the record.
        if result[5] and len(result[5] >= 2) :
            keywords = result[5].split(',')
            
            edc_record['tags'] = [{'name' : re.sub('[^ A-Za-z0-9_-]+','', keyword)} for keyword in keywords]
        
        resource_status = result[6] or 'onGoing'
        #Set record's resource status to completed
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
        
        #Adding dataset contacts
        contacts = []
        
        contact_len = min(len(contact_names), len(contact_emails), len(contact_orgs))
        
        for i in range(contact_len): 
#            (contact_org, contact_sub_org) = get_organization(contact_orgs[i])       
            contacts.append({'name': contact_names[i], 'email': contact_emails[i], 'delete': '0', 'organization': edc_record['org'], 'role' : '002'})
        
        edc_record['contacts'] = contacts
        
        #Set record view audience and download audience to public
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
        
        edc_record['iso_topic_cat'] = '020'   #Not applicable
        
        edc_record['metastar_uid'] = str(result[14])
        
        edc_record['lineage_statement'] = result[18]
        
        if result[19].lower().startswith('tru'):       
            edc_record['metadata_visibility'] = '002'
        else:
            edc_record['metadata_visibility'] = '001'
        
        edc_record['archive_retention_schedule'] = result[20]
        edc_record['retention_expiry_date'] = result[21]
        edc_record['source_data_path'] = result[22]
        
        #Set record's resource update cycle
        update_cycle =  result[10] or 'unknown'
        edc_record['resource_update_cycle'] = get_edc_tag_id('resource_update_cycle', update_cycle)
        
        #Adding dataset dates
        dates = []
        if result[30] :
            dates.append({'type': '001', 'date': result[30], 'delete': '0'})
        if result[31] :
            dates.append({'type': '002', 'date': result[31], 'delete': '0'})
        
        edc_record['dates'] = dates

        security_class = result[28]
        
        if security_class == 'secret' or security_class == 'topSecret' or 'restricted':
            edc_record['security_class'] = '001'
            if security_class == 'topSecret' :
                edc_record['bc_ocio'] = 'HIGH-CABINET'
            elif security_class == 'secret':
                edc_record['bc_ocio'] = 'HIGH-CONFEDENTIAL'
            else :
                edc_record['bc_ocio'] = 'HIGH-SENSITIVITY'                
        elif security_class == 'confidential':
            edc_record['security_class'] = '002'
            edc_record['bc_ocio'] = 'MEDIUM-SENSITIVITY'
        elif security_class == 'unclassified' :
            edc_record['security_class'] = '003'
            edc_record['bc_ocio'] = 'LOW-SENSITIVITY'
        else :
            edc_record['security_class'] = '003'
            edc_record['bc_ocio'] = 'LOW-PUBLIC'
        
        iso_topic_cat = (result[29] or 'unknown').split(',')[0]    
        edc_record['iso_topic_category'] = get_edc_tag_id('iso_topic_category', iso_topic_cat)

        
        
        resources = []
            
        resource_rec = {}
            
        resource_rec['name'] = result[0]
        resource_rec['url'] = ' '
            
        resource_rec['format'] = '015'
        
        if result[15] :
            resource_rec['projection_name'] = result[15]
        else :
            resource_rec['projection_name'] = ' '
        
        resource_type = result[23] or 'Data'
        resource_rec['edc_resource_type'] = get_edc_tag_id('resource_type', resource_type.strip())
        
        access_method = 'Service'
        resource_rec['resource_storage_access_method'] = get_edc_tag_id('resource_storage_access_method', access_method.strip())
        resource_rec['resource_storage_location'] = '001' #Get the tag ID for resource storage location
            
        resource_rec['data_collection_start_date'] = result[16]
        resource_rec['data_collection_end_date'] = result[17]
        
            #Add the current resource record to the list of dataset resources     
        resources.append(resource_rec)
        
        #Add the list of dataset resources to the dataset
        edc_record['resources'] = resources    
#        media_cur.close()
        
#        pprint.pprint(edc_record) 

        #Adding dataset features        
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
        
#        pprint.pprint(edc_record)
        record_info = edc_package_create(edc_record)
         
        if record_info:
            number_of_records_created = number_of_records_created + 1
        else :
            print 'Error in creating record.'
        
        index = index + 1
        
    
    print "Total number of records : ", index
    print "Number of records created : ", number_of_records_created   
    con.close()
    
def import_data():
    
    data_source = raw_input("Data source (ODC/Discovery): ") 
    con =  get_connection(data_source) 
     
    if data_source.lower() == 'odc' :
        import_odc_records(con)
    elif data_source.lower() == 'discovery' :
        import_discovery_records(con)
    else :
        print "No data source is given."
            
import_data()