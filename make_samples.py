import pymysql.cursors
import datetime
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
                    #print(en_licnese,ex_license)
                    return 0,record['C_CARD_LICENSE'],record['C_EX_LICENSE']

            return 1,record['C_CARD_LICENSE'],record['C_EX_LICENSE']

        return 0,record['C_CARD_LICENSE'],record['C_EX_LICENSE']

    def axis_number_(self,record):
        #轴载类型
        axis_number = record['axis_number']
        if (axis_number>2):
            return 1
        else:
            return 0
        #return str(record['axis_number'])

    def turn_around_(self,record,last_record):
        # 5分钟内出现某站出同站入的情况
        # return : None 下一次入口时间小于或等于上一次出口时间,
        # return :1 小于5分钟
        # renturn :0 大于5分钟
        if last_record:
            #print(last_record)
            last_ex_date, last_ex_station, last_ex_license = str(last_record['N_EX_DATE']) + str(last_record['N_EX_TIME']).zfill(6), str(last_record['N_EX_LANE_ID'])[0:4], \
                                                             last_record['C_EX_LICENSE']

            if str(record['N_EN_STATION_ID']) == last_ex_station and record['C_CARD_LICENSE'][0:7]==last_ex_license[0:7] :
                en_time = str(record['N_EN_DATE']) + str(record['N_EN_TIME']).zfill(6)
                #ex_time = str(record['N_EX_DATE']) + str(record['N_EX_TIME']).zfill(6)
                try:
                    en_time = datetime.datetime.strptime(en_time,'%Y%m%d%H%M%S')
                    last_ex_date = datetime.datetime.strptime(last_ex_date,'%Y%m%d%H%M%S')
                    cost_time = (en_time-last_ex_date).total_seconds()
                except:
                    print('turn_around error ',ValueError)
                    return None
                if cost_time>0:
                    if cost_time<300:
                        print('cost_time<300',record['C_CARD_LICENSE'],last_ex_license,record['N_EN_STATION_ID'],last_ex_station,en_time,last_ex_date,cost_time)
                        return 1
                    else:
                        #print('cost_time >300')
                        return 0
                else:
                    print('cost_time <0',record['C_CARD_LICENSE'],last_ex_license,record['N_EN_STATION_ID'],last_ex_station,en_time,last_ex_date,cost_time)
                    return None
            else:
                #print('NO TURN AROUND')
                return 0
        else:
            return 0

        # 同一天内或者同一月内,车辆进出次数,放到最后pandas里面去统计出口车牌即可。
        return

    def cost_time_(self, record):
        # 进出口用时
        en_time = str(record['N_EN_DATE']) + str(record['N_EN_TIME']).zfill(6)
        ex_time = str(record['N_EX_DATE']) + str(record['N_EX_TIME']).zfill(6)
        try:
            en_time = datetime.datetime.strptime(en_time, '%Y%m%d%H%M%S')
            ex_time = datetime.datetime.strptime(ex_time, '%Y%m%d%H%M%S')
            cost_time = (ex_time - en_time).total_seconds()/3600
        except:
            print('turn_around error ', ValueError)
            return None

        return cost_time


    def over_weight_(self,record):
        #总载重与行驶距离异常，如return 1:里程30公里以下，总重大于轴限的80%；
        # return None : D_FARE2不存在
        if record['D_FARE2'] <=0:
            print('D_FRE2 <=0:',record['D_FARE2'] )
            return None
        weight = float(record['D_WEIGHT'])
        fee_lenth =  float(record['D_FEE_LENGTH'])
        if (fee_lenth<30) & (weight>float(record['D_FARE2'])*0.9):
            #print('over_weight', fee_lenth,weight,record['D_FARE2'])
            return 1
        else:
            return 0

    def light_weight_(self,record):
        #总载重与行驶距离异常，return 1: 如里程100公里以上，总重小于轴限的30%；
        # return None : D_FARE2不存在

        if record['D_FARE2'] <= 0:
            print('D_FRE2 <=0_:',record['D_FARE2'] )

            return None
        weight = float(record['D_WEIGHT'])
        fee_lenth = float(record['D_FEE_LENGTH'])
        if (fee_lenth >100 ) & (weight < float(record['D_FARE2']) * 0.5):
            #print('light_weight', fee_lenth,weight,record['D_FARE2'])
            return 1
        else:
            return 0

    def over_delay_(self,record):
        delay = record['C_PART_VEHICLE_TYPE'].strip()
        if delay == '1F':
            #print('delay:',delay)
            return 1
        else:
            return 0

    def vehicle_class_(self,record):
        # return 1:同一车牌两种车型以上
        if record['C_EN_VEHICLE_CLASS']!=record['C_EX_VEHICLE_CLASS']:
            #print('vehicle_class:',record['C_EN_VEHICLE_CLASS'],record['C_EX_VEHICLE_CLASS'])
            return 1
        else:
            return 0

    def strange_marks_(self,record):
        #卡内标志站与应记录标识站（系统自动规划出的标识站）不一致，通常为卡内标识站出现不应出现的应记录标识站点记录
        if record['VC_MARKS'] == None:
            return 0

        if record['VC_FIX_MARKS'] == None:
            return 1
        vc_marks = list(record['VC_MARKS'])
        vc_fix_marks = list(record['VC_FIX_MARKS'])
        #print(vc_marks)

        for m in vc_marks:
            if m not in vc_fix_marks:
                #print('vc_marks={vc_marks} {vc_fix_marks}:'.format(vc_marks=vc_marks,vc_fix_marks=vc_fix_marks))
                return 1
        return 0

    def lost_marks_(self,record):
        #卡内标志站与应记录标识站不一致（三个或三个以上），通常为卡内标识站只缺失应出现的标识站点记录。即经过标志站但卡中无标志站
        if record['VC_MARKS'] == None:
            return 1

        if record['VC_FIX_MARKS'] == None:
            return 0
        i = 0
        vc_marks = list(record['VC_MARKS'])
        vc_fix_marks = list(record['VC_FIX_MARKS'])
        for m in vc_fix_marks:
            if m not in vc_marks:

                i +=1
            if i >= 3:
                print('vc_marks={vc_marks} {vc_fix_marks}:'.format(vc_marks=vc_marks,vc_fix_marks=vc_fix_marks))

                return 1
        return 0

    def fee_length_(self,record):
        return record['D_FEE_LENGTH']
    def weight_(self,record):
        return record['D_WEIGHT']

    def over_weight_original_(self, record):
        if record['D_OVER_WEIGHT'] >100:
            print('big than 100:',record['D_OVER_WEIGHT'] )
            return None
        return record['D_OVER_WEIGHT']

    def speed_(self,cost_time,fee_length):
        if cost_time==0 or cost_time==None :
            print('cost_time is 0 or None,exit')
            return None
        return float(fee_length)/float(cost_time)





    def make_row(self,record,last_record):
        record_list = []
        lab = self.label_(record)
        turn_around = self.turn_around_(record,last_record)
        over_weight = self.over_weight_(record)
        light_weight = self.light_weight_(record)
        over_weight_original = self.over_weight_original_(record)
        if (lab!=None and turn_around!=None and over_weight!=None and light_weight!=None and over_weight_original!=None):
            #record_list = list(lab)
            axis_number = self.axis_number_(record)
            over_delay = self.over_delay_(record)
            vehicle_class = self.vehicle_class_(record)
            strange_marks = self.strange_marks_(record)
            lost_marks = self.lost_marks_(record)
            fee_length = self.fee_length_(record)
            weight = self.weight_(record)
            cost_time = self.cost_time_(record)
            speed = self.speed_(cost_time,fee_length)
            fea_list = [lab,vehicle_class,turn_around,strange_marks,lost_marks,over_weight,light_weight,over_delay,axis_number,
                        fee_length,weight,over_weight_original,cost_time,speed]

            for fea in fea_list:
                if isinstance(fea,tuple):
                    for value in fea:
                        record_list.append(value)
                else:

                    record_list.append(fea)
            new_record = ','.join([str(value) for value in record_list])+'\n'
            return new_record
        else:
            return None
        return
    #def turn_around(self,record):

def make_samples():
    data_list = [ '2018060'+str(i) if i<10 else '201806'+str(i) for i in range(1,31)]
    con_exit = pymysql.Connect(host='12.1.150.35',user='user',
                          password='user',db='cico',port=8066,
                          cursorclass= pymysql.cursors.SSDictCursor,
                          use_unicode=True, charset="utf8")
    cur_exit =con_exit.cursor()
    fw = open("samples.txt", "w")
    for date in data_list:
        sql_exit =  "select {columns} from  exit_jour  a " \
                    "left  join entry_jour b " \
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
                    "and a.N_EX_DATE >= a.N_EN_DATE " \
                    "and a.C_EX_LICENSE regexp '^[京津冀晋蒙辽吉黑沪苏浙皖闽赣鲁豫鄂湘粤桂琼渝川黔滇藏陕甘青宁新台港澳]{{1}}[A-Z]{{1}}.*$' " \
                    "and a.C_CARD_LICENSE regexp '^[京津冀晋蒙辽吉黑沪苏浙皖闽赣鲁豫鄂湘粤桂琼渝川黔滇藏陕甘青宁新台港澳]{{1}}[A-Z]{{1}}.*$' " \
                    "ORDER  by a.C_CARD_LICENSE, a.N_EN_DATE,a.N_EN_TIME ASC " \
                    "{limit}".format(start_date=date,end_date=date,start_date1=date,end_date1=date,

                                     columns='a.N_EN_DATE,a.N_EN_TIME,a.N_EN_STATION_ID,a.C_EN_VEHICLE_CLASS,a.N_EX_DATE,a.N_EX_TIME,'\
                                             'a.N_EX_SERIAL_NO,a.N_EX_LANE_ID,a.C_EX_VEHICLE_CLASS,a.VC_MARKS,a.N_CARD_LANE_ID,a.N_CARD_SERIAL_NO,'\
                                             'a.C_CARD_LICENSE,a.C_EX_LICENSE,a.C_PART_VEHICLE_TYPE,a.D_WEIGHT,a.D_OVER_WEIGHT,a.D_FEE_LENGTH,'\
                                             'a.D_FARE2,a.VC_MARKS,a.VC_FIX_MARKS,b.C_EN_VEHICLE_CLASS,c.axis_number',


                                     limit = 'limit 1000'
                                     )

        print(sql_exit)



        cur_exit.execute(sql_exit)
        fea = Fea_process()
        result = cur_exit.fetchall()
        last_record = []
        for index ,record in enumerate(result):
            if index>1:
                last_record = result[index - 1]
            new_record = fea.make_row(record,last_record)
            if new_record!=None:
                fw.writelines(new_record)
    fw.close()
    #print(cur_axis.fetchone())
    #for row in cur.fetchone():
     #   print(row)

    cur_exit.close()
    con_exit.close()



def main():
    make_samples()
if __name__ == '__main__':
    main()
