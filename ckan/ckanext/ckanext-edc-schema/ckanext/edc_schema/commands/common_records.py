
import cx_Oracle
import urllib2
import urllib
import os
import sys




def get_connection():
    
    connection_str = "proxy_metastar/h0tsh0t@slkux1.env.gov.bc.ca/idwprod1.bcgov"
    con = cx_Oracle.connect(connection_str)
    return con


def get_common_records():
    
    con = get_connection()
    
    print 'Connection established. Getting data from database... '
    
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
    common_records_file = open('common_records.txt', 'w') 

    common_records = []
    
    for result in data:
        
        # If this is record exists in discovery add it to the list            
        if result[22]:
            common_records.append(result[22])
            print result[22]
        
    for record_uid in common_records :
        common_records_file.write('%s\n' % record_uid)
    
    common_records_file.close()
    
get_common_records()