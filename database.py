#import MySQLdb
import pymysql.cursors

class Fea_process():
    def label_(self,record):
        #return 1:same,0:not same,进出口车牌，如四位相同即判定是同一张车牌 ,None:这个label不需要

        drop_license = ['浙A00000','浙A11111','浙A12345','赣555555','沪222222','浙A000DD','浙A000DD']

        if record['C_CARD_LICENSE'][0:7] in drop_license:
            return None
        if record['C_EX_LICENSE'][0:7] in drop_license:
            return None
        en_licnese = record['C_CARD_LICENSE'][2:7]
        ex_license = record['C_EX_LICENSE'][2:7]

        positions = ((0,1,2,3),(1,2,3,4),(0,2,3,4),(0,1,3,4),(0,1,2,4))
        if en_licnese != ex_license:
            for pos in positions:
                same_pos = 0
                for index in pos:
                    if en_licnese[index]  == ex_license[index] :
                        same_pos +=1
                if same_pos == 4:
                    print(en_licnese,ex_license)
                    return 0,en_licnese,ex_license
                else:
                    return 1,record['C_CARD_LICENSE'],record['C_EX_LICENSE']

        return 0,record['C_CARD_LICENSE'],record['C_EX_LICENSE']

    def axis_number_(self,record):
        print(record['axis_number'])
        return str(record['axis_number'])

    def make_row(self,record):
        record_list = list(self.label_(record))
        if (record_list==None):
            return None
        axis_number = self.axis_number_(record)
        record_list.append(axis_number)

        new_record = ','.join([str(value) for value in record_list])+'\n'


        return new_record
    #def turn_around(self,record):


con_axis = pymysql.Connect(host='12.1.150.35',user='user',
                      password='user',db='cico',port=8066,
                      cursorclass= pymysql.cursors.SSDictCursor,
                      use_unicode=True, charset="utf8")
con_exit = pymysql.Connect(host='12.1.150.35',user='user',
                      password='user',db='cico',port=8066,
                      cursorclass= pymysql.cursors.SSDictCursor,
                      use_unicode=True, charset="utf8")


cur_exit =con_exit.cursor()
cur_axis = con_axis.cursor()
sql_exit =  "select {columns} from  exit_jour  a left  join entry_jour b " \
            "on a.N_EN_DATE = b.N_EN_DATE and a.N_CARD_LANE_ID = b.N_EN_LANE_ID and a.N_CARD_SERIAL_NO = b.N_EN_SERIAL_NO " \
            "left join (select exit_jour.C_CARD_LICENSE,count(distinct N_AXIS_TYPE) axis_number from exit_jour left join axis_jour " \
            "on exit_jour.N_EN_DATE=axis_jour.N_DATE and exit_jour.N_EX_LANE_ID=axis_jour.N_LANE_ID " \
            "and exit_jour.N_EX_SERIAL_NO=axis_jour.N_SERIAL_NO " \
            "where exit_jour.N_EX_DATE={start_date1} and {end_date1} group by exit_jour.C_CARD_LICENSE) c " \
            "on a.C_CARD_LICENSE = c.C_CARD_LICENSE " \
            "where a.N_EX_DATE between {start_date} and {end_date} " \
            "and a.c_category = '1'"\
            "and a.N_EN_STATION_ID >= '1011'"\
            "and a.N_EN_STATION_ID <= '1731'"\
            "and substring(a.N_EX_LANE_ID,1,4) >= '1011' and substring(a.N_EX_LANE_ID,1,4) <= '1731'"\
            "and D_FEE_LENGTH!='0'"\
            "and D_WEIGHT!='0'" \
            "and a.N_BOX_ID >= b.N_BOX_ID " \
            "and a.C_EX_LICENSE regexp '^[京津冀晋蒙辽吉黑沪苏浙皖闽赣鲁豫鄂湘粤桂琼渝川黔滇藏陕甘青宁新台港澳]{{1}}[A-Z]{{1}}.*$' " \
            "and a.C_CARD_LICENSE regexp '^[京津冀晋蒙辽吉黑沪苏浙皖闽赣鲁豫鄂湘粤桂琼渝川黔滇藏陕甘青宁新台港澳]{{1}}[A-Z]{{1}}.*$' " \
            "{limit}".format(start_date='20180601',end_date='20180601',start_date1='20180601',end_date1='20180601',

                             columns='a.N_EN_DATE,a.N_EN_TIME,a.N_EN_STATION_ID,a.C_EN_VEHICLE_CLASS,a.N_EX_DATE,a.N_EX_TIME,'\
                                     'a.N_EX_SERIAL_NO,a.N_EX_LANE_ID,a.C_EX_VEHICLE_TYPE,a.VC_MARKS,a.N_CARD_LANE_ID,a.N_CARD_SERIAL_NO,'\
                                     'a.C_CARD_LICENSE,a.C_EX_LICENSE,a.C_PART_VEHICLE_TYPE,a.D_WEIGHT,a.D_OVER_WEIGHT,a.D_FEE_LENGTH,'\
                                     'a.D_FARE2,c.axis_number',


                             limit = 'limit 1000'

                                    )

print(sql_exit)
sql_axis = "select * from axis_jour where axis_jour.N_DATE BETWEEN 20180601 AND 20180631 limit 1000"


#def card

cur_exit.execute(sql_exit)
cur_axis.execute(sql_axis)
#def card_license():
fea = Fea_process()
result = cur_exit.fetchall()
fw = open("samples.txt", "w")


for record in result:

    new_record = fea.make_row(record)
    if new_record!=None:
        fw.writelines(new_record)
fw.close()
#print(cur_axis.fetchone())
#for row in cur.fetchone():
 #   print(row)

cur_exit.close()
cur_axis.close()
con_axis.close()
con_exit.close()
#"and a.C_EX_LICENSE regexp '^[京津冀晋蒙辽吉黑沪苏浙皖闽赣鲁豫鄂湘粤桂琼渝川黔滇藏陕甘青宁新台港澳]{1}[A-Z]{1}.*$' " \
#"and a.C_CARD_LICENSE regexp '^[京津冀晋蒙辽吉黑沪苏浙皖闽赣鲁豫鄂湘粤桂琼渝川黔滇藏陕甘青宁新台港澳]{1}[A-Z]{1}.*$' "\