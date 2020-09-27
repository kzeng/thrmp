import sys
import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, request, Response, send_file, send_from_directory, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from router.models import User, query_user

import serial
import serial.tools.list_ports
import configparser

import zipfile
import re
import json
import time
import csv

import io
import random
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from router.broker import Broker

# here define a route
module_bp = Blueprint(
    'module',
    '__name__',
)


##################################################
# SETTINGS
##################################################
@module_bp.route('/')
@module_bp.route('/dashboard')
@login_required
def dashboard():
    print(current_user.get_id())
    return render_template('dashboard.html', title='首页-仪表盘', curr_user=current_user.get_id())


@module_bp.route('/api/dashboard_get_info1', methods=['POST'])
def dashboard_get_info1():
    try:
        b = Broker()
        print("dashboard_get_info1 ...")
        dashboard_get_info1_dict = {}
            
        # 系统时间
        # t1,t2,t3,t4,t5,t6 表示当时间，按年，月，日，周，时，分依次
        data = b.dashboard_info
        data_list = data.split(" ")
        year = int('0x' + data_list[9], 16)
        month = int('0x' + data_list[10], 16)
        day = int('0x' + data_list[11], 16)
        week_str = ['日', '一', '二', '三', '四', '五', '六', '---' ]
        week = int('0x' + data_list[12], 16)

        hour = int('0x' + data_list[13], 16)
        mins = int('0x' + data_list[14], 16)
        dashboard_get_info1_dict.update({"system_time" : "20{:0>2d}年{:0>2d}月{:0>2d}日 星期{} {:0>2d}:{:0>2d}".format(year, month,day, week_str[week], hour, mins) })

        dashboard_get_info1_dict.update({"device_id" : str( int('0x' + data_list[3], 16) ) })

        if int('0x' + data_list[5], 16) == 1:
            run_status = "运行"
        else:
            run_status = "停止"
        dashboard_get_info1_dict.update({"run_status" : run_status })

        dashboard_get_info1_dict.update({"run_time" : str( round(int('0x' + data_list[6] + data_list[7], 16)/24)) })

        dashboard_get_info1_dict.update({"record_interval" : str( round(int('0x' + data_list[8], 16))) })
        
        # 01  00 C8 03 26  00 C8  00 0A  03 C0  00 32  01 00 00 00 00 	  第一通道数据
        # 第1字节，表示传感器存在与否（1表示存在，0表示不存在），不存在时，温湿度上传数据为0，在界面上显示为“――――”
        # 第2，3字节为温度数据，高位在前，低位在后。实际显示时应缩小10位，取得一位小数。如本次收到00C8，实际显示为20.0.
        # 第4，5字节为湿度数据，高位在前，低位在后。实际显示时应缩小10位，取得一位小数。如本次收到0326，实际显示为80.6.
        ch = 1
        for idx in (15,33,51,69): #各通道数据起始地址在整个响应数据中的位置
            if int('0x' + data_list[idx], 16) == 0:
                dashboard_get_info1_dict.update({"temp_" + str(ch) : "----" })
                dashboard_get_info1_dict.update({"hum_" + str(ch) : "----" })
                dashboard_get_info1_dict.update({"control_mode_" + str(ch) : "hide" })
                dashboard_get_info1_dict.update({"control_method_" + str(ch) : "hide" })
                dashboard_get_info1_dict.update({"air_protect_status_" + str(ch) : "hide" })
                dashboard_get_info1_dict.update({"control_output_status_" + str(ch) : "hide" })
            else:
                dashboard_get_info1_dict.update({"temp_" + str(ch) : str(int('0x' + data_list[idx+1] + data_list[idx+2], 16)/10.0) })
                dashboard_get_info1_dict.update({"hum_" + str(ch) : str(int('0x' + data_list[idx+3] + data_list[idx+4], 16)/10.0) })
                if int('0x' + data_list[idx+13], 16) == 1:
                    dashboard_get_info1_dict.update({"control_mode_" + str(ch) : "循环" })
                else:
                    dashboard_get_info1_dict.update({"control_mode_" + str(ch) : "自动" })
                
                if int('0x' + data_list[idx+14], 16) == 1:
                    dashboard_get_info1_dict.update({"control_method_" + str(ch) : "节能" })
                else:
                    dashboard_get_info1_dict.update({"control_method_" + str(ch) : "hide" })

                if int('0x' + data_list[idx+15], 16) == 0: #00
                    dashboard_get_info1_dict.update({"air_protect_status_" + str(ch) : "hide" })
                elif int('0x' + data_list[idx+15], 16) == 2: #10
                    dashboard_get_info1_dict.update({"air_protect_status_" + str(ch) : "制冷保护" })
                elif int('0x' + data_list[idx+15], 16) == 1: #01
                    dashboard_get_info1_dict.update({"air_protect_status_" + str(ch) : "加热保护" })
                else:
                    dashboard_get_info1_dict.update({"air_protect_status_" + str(ch) : "hide" })

                bin_str="{:>08}".format(bin(int('0x' + data_list[31], 16))[2:])
                bin_str_list = list(bin_str)
                cos_str = ''
                # ['0', '0', '0', '0', '0', '1', '0', '1']
                # 从低到高每个状态为：加热，制冷，化霜，加湿，抽湿.
                if bin_str_list[7] == '1':
                    cos_str += "加热 "
                if bin_str_list[6] == '1':
                    cos_str += "制冷 "
                if bin_str_list[5] == '1':
                    cos_str += "化霜 "
                if bin_str_list[4] == '1':
                    cos_str += "加湿 "            
                if bin_str_list[3] == '1':
                    cos_str += "抽湿 " 
                if cos_str == '':
                    cos_str = "hide"
                dashboard_get_info1_dict.update({"control_output_status_" + str(ch) : cos_str })

            dashboard_get_info1_dict.update({"target_temp_" + str(ch) : str(int('0x' + data_list[idx+5] + data_list[idx+6], 16)/10.0) })
            dashboard_get_info1_dict.update({"control_temp_" + str(ch) : str(int('0x' + data_list[idx+7] + data_list[idx+8], 16)/10.0) })
            dashboard_get_info1_dict.update({"target_hum_" + str(ch) : str(int('0x' + data_list[idx+9] + data_list[idx+10], 16)/10.0) })
            dashboard_get_info1_dict.update({"control_hum_" + str(ch) : str(int('0x' + data_list[idx+11] + data_list[idx+12], 16)/10.0) })

            ch = ch + 1

        print(dashboard_get_info1_dict)
        return json.dumps(dashboard_get_info1_dict)
    except:
        print("Something wrong, try again ...")
        time.sleep(3)
        dashboard_get_info1()


@module_bp.route('/record_data_setting')
def record_data_setting():
    return render_template('record_data_setting.html', title='数据记录设置', curr_user=current_user.get_id())


@module_bp.route('/api/get_record_data_setting', methods=['POST'])
def get_record_data_setting():
    b = Broker()
    print("get_record_data_setting ...")
    return b.record_data_setting


@module_bp.route('/api/set_record_data_setting', methods=['POST'])
def set_record_data_setting():
    record_interval = int(request.form["record_interval"])
    refresh_interval = int(request.form["refresh_interval"])
    light = int(request.form["light"])
    sleep_time = int(request.form["sleep_time"])
    auto_refresh = int(request.form["auto_refresh"])
    # 数据记录间隔（小时）,数据更新间隔（秒）,背光亮度（%）,休眠时间（分）,自动刷新（分）,01 ??
    b = Broker()
    b.record_data_setting=record_interval,refresh_interval,light,sleep_time,auto_refresh,1
    print("set_record_data_setting ...")
    return "ok"


# 高级设置->仪表控制设置
@module_bp.route('/advance_setting_param')
def advance_setting_param():
    return render_template('advance_setting_param.html', title='高级设置', curr_user=current_user.get_id())


@module_bp.route('/api/get_advance_setting_param', methods=['POST'])
def get_advance_setting_param():
    b = Broker()
    print("get_advance_setting_param ...")
    # 55 12 F1 00 63 03 1F 00 C8 00 13 00 00 00 00 00 00 00 01 AA 
    # print(b.advance_setting_param)
    return b.advance_setting_param


@module_bp.route('/api/set_advance_setting_param', methods=['POST'])
def set_advance_setting_param():
    device_id = int(request.form["device_id"])
    run_time = int(request.form["run_time"])
    water_temp = int( float(request.form["water_temp"])*10 )
    water_temp1 = int( float(request.form["water_temp1"])*10 )
    clock = int(request.form["clock"])
    save_id = int(request.form["save_id"])
    save_point = int(request.form["save_point"])
    b = Broker()
    print(device_id,run_time,water_temp,water_temp1,clock,save_id,save_point)
    b.advance_setting_param=device_id,run_time,water_temp,water_temp1,clock,save_id,save_point,1
    print("set_advance_setting_param ...")
    return "ok"


@module_bp.route('/channel_control_settings')
def channel_control_settings():
    return render_template('channel_control_settings.html', title='控制参数设置', curr_user=current_user.get_id())


@module_bp.route('/api/get_channel_control_settings', methods=['POST'])
def get_channel_control_settings():
    b = Broker()
    print("get_channel_control_settings ...")
    channel_control_settings_dict = {}
    for ch in (0,1,2,3):
        ch_data = b.channel_control_settings(ch)
        ch_data_list = ch_data.split(" ")
        channel_control_settings_dict.update({"target_temp_" + str(ch+1) : int('0x' + ch_data_list[4] + ch_data_list[5], 16)/10})
        channel_control_settings_dict.update({"target_hum_" + str(ch+1) : int('0x' + ch_data_list[6] + ch_data_list[7], 16)/10})
        channel_control_settings_dict.update({"control_temp_" + str(ch+1) : int('0x' + ch_data_list[8] + ch_data_list[9], 16)/10})
        channel_control_settings_dict.update({"control_hum_" + str(ch+1) : int('0x' + ch_data_list[10] + ch_data_list[11], 16)/10})
        channel_control_settings_dict.update({"temp_convert_time_" + str(ch+1) : int('0x' + ch_data_list[12] + ch_data_list[13], 16)})
        channel_control_settings_dict.update({"hum_convert_time_" + str(ch+1) : int('0x' + ch_data_list[14] + ch_data_list[15], 16)})
        channel_control_settings_dict.update({"temp_heat_time_" + str(ch+1) : int('0x' + ch_data_list[16] + ch_data_list[17], 16)})
        channel_control_settings_dict.update({"hum_add_start_time_" + str(ch+1) : int('0x' + ch_data_list[18] + ch_data_list[19], 16)})
        channel_control_settings_dict.update({"temp_frost_time_" + str(ch+1) : int('0x' + ch_data_list[20] + ch_data_list[21], 16)})
        channel_control_settings_dict.update({"hum_add_stop_time_" + str(ch+1) : int('0x' + ch_data_list[22] + ch_data_list[23], 16)})
    print(channel_control_settings_dict)
    return json.dumps(channel_control_settings_dict)


@module_bp.route('/api/get_channel_control_settings_by_ch', methods=['POST'])
def get_channel_control_settings_by_ch():
    b = Broker()
    print("get_channel_control_settings_by_ch ...")
    channel_control_settings_dict = {}
    ch = int(request.form["ch"])
    ch_data = b.channel_control_settings(ch)
    ch_data_list = ch_data.split(" ")
    channel_control_settings_dict.update({"target_temp_" + str(ch+1) : int('0x' + ch_data_list[4] + ch_data_list[5], 16)/10})
    channel_control_settings_dict.update({"target_hum_" + str(ch+1) : int('0x' + ch_data_list[6] + ch_data_list[7], 16)/10})
    channel_control_settings_dict.update({"control_temp_" + str(ch+1) : int('0x' + ch_data_list[8] + ch_data_list[9], 16)/10})
    channel_control_settings_dict.update({"control_hum_" + str(ch+1) : int('0x' + ch_data_list[10] + ch_data_list[11], 16)/10})
    channel_control_settings_dict.update({"temp_convert_time_" + str(ch+1) : int('0x' + ch_data_list[12] + ch_data_list[13], 16)})
    channel_control_settings_dict.update({"hum_convert_time_" + str(ch+1) : int('0x' + ch_data_list[14] + ch_data_list[15], 16)})
    channel_control_settings_dict.update({"temp_heat_time_" + str(ch+1) : int('0x' + ch_data_list[16] + ch_data_list[17], 16)})
    channel_control_settings_dict.update({"hum_add_start_time_" + str(ch+1) : int('0x' + ch_data_list[18] + ch_data_list[19], 16)})
    channel_control_settings_dict.update({"temp_frost_time_" + str(ch+1) : int('0x' + ch_data_list[20] + ch_data_list[21], 16)})
    channel_control_settings_dict.update({"hum_add_stop_time_" + str(ch+1) : int('0x' + ch_data_list[22] + ch_data_list[23], 16)})
    print(channel_control_settings_dict)
    return json.dumps(channel_control_settings_dict)


@module_bp.route('/api/set_channel_control_settings_by_ch', methods=['POST'])
def set_channel_control_settings_by_ch():
    print('set_channel_control_settings_by_ch .')
    channel = request.form["arg0"]
    target_temp = int( float(request.form["arg1"])*10 )
    target_hum = int( float(request.form["arg2"])*10 )
    control_temp = int( float(request.form["arg3"])*10 )
    control_hum = int( float(request.form["arg4"])*10 )
    temp_convert_time = int(request.form["arg5"])
    hum_convert_time = int(request.form["arg6"])
    temp_heat_time = int(request.form["arg7"])
    hum_add_start_time = int(request.form["arg8"])
    temp_frost_time = int(request.form["arg9"])
    hum_add_stop_time = int(request.form["arg10"])    
    b = Broker()
    print('set_channel_control_settings_by_ch params ....')
    print(channel)
    # 2 210 960 10 50 3 3 40 50 3 40
    print(channel,target_temp,target_hum,control_temp,control_hum,temp_convert_time,hum_convert_time,temp_heat_time,hum_add_start_time,temp_frost_time,hum_add_stop_time)
    b.channel_control_settings_by_ch=channel,target_temp,target_hum,control_temp,control_hum,temp_convert_time,hum_convert_time,temp_heat_time,hum_add_start_time,temp_frost_time,hum_add_stop_time,0,0
    print("set_channel_control_settings_by_ch ...")
    return "ok"


@module_bp.route('/current_channel_verify_data')
def current_channel_verify_data():
    return render_template('current_channel_verify_data.html', title='传感器校正', curr_user=current_user.get_id())


@module_bp.route('/api/get_current_channel_verify_data', methods=['POST'])
def get_current_channel_verify_data():
    b = Broker()
    print("get_current_channel_verify_data ...")
    current_channel_verify_data_dict = {}
    ch_data = b.current_channel_verify_data
    ch_data_list = ch_data.split(" ")
    for ch in (1,2,3,4):
        current_channel_verify_data_dict.update({"temp_offset_mark_" + str(ch) : int('0x' + ch_data_list[3], 16)})
        current_channel_verify_data_dict.update({"temp_offset_" + str(ch) : int('0x' + ch_data_list[4] + ch_data_list[5], 16)/10})
        current_channel_verify_data_dict.update({"hum_offset_mark_" + str(ch) : int('0x' + ch_data_list[6], 16)})
        current_channel_verify_data_dict.update({"hum_offset_" + str(ch) : int('0x' + ch_data_list[7] + ch_data_list[8], 16)/10})
        current_channel_verify_data_dict.update({"temp_offset_mark_2" : int('0x' + ch_data_list[9], 16)})
        current_channel_verify_data_dict.update({"temp_offset_2" : int('0x' + ch_data_list[10] + ch_data_list[11], 16)/10})
        current_channel_verify_data_dict.update({"hum_offset_mark_2" : int('0x' + ch_data_list[12], 16)})
        current_channel_verify_data_dict.update({"hum_offset_2" : int('0x' + ch_data_list[13] + ch_data_list[14], 16)/10})
        current_channel_verify_data_dict.update({"temp_offset_mark_3" : int('0x' + ch_data_list[15], 16)})
        current_channel_verify_data_dict.update({"temp_offset_3" : int('0x' + ch_data_list[16] + ch_data_list[17], 16)/10})
        current_channel_verify_data_dict.update({"hum_offset_mark_3" : int('0x' + ch_data_list[18], 16)})
        current_channel_verify_data_dict.update({"hum_offset_3" : int('0x' + ch_data_list[19] + ch_data_list[20], 16)/10})
        current_channel_verify_data_dict.update({"temp_offset_mark_4" : int('0x' + ch_data_list[21], 16)})
        current_channel_verify_data_dict.update({"temp_offset_4" : int('0x' + ch_data_list[22] + ch_data_list[23], 16)/10})
        current_channel_verify_data_dict.update({"hum_offset_mark_4" : int('0x' + ch_data_list[24], 16)})
        current_channel_verify_data_dict.update({"hum_offset_4" : int('0x' + ch_data_list[25] + ch_data_list[26], 16)/10})

    print(current_channel_verify_data_dict)
    return json.dumps(current_channel_verify_data_dict)


@module_bp.route('/api/set_current_channel_verify_data', methods=['POST'])
def set_current_channel_verify_data():
    print('set_current_channel_verify_data .')
    arg1 = int( request.form["arg1"] )
    arg2 = int( float(request.form["arg2"])*10 )
    arg3 = int( request.form["arg3"] )
    arg4 = int( float(request.form["arg4"])*10 )
    arg5 = int( request.form["arg5"] )
    arg6 = int( float(request.form["arg6"])*10 )
    arg7 = int( request.form["arg7"] )
    arg8 = int( float(request.form["arg8"])*10 )
    arg9 = int( request.form["arg9"] )
    arg10 = int( float(request.form["arg10"])*10 )
    arg11 = int( request.form["arg11"] )
    arg12 = int( float(request.form["arg12"])*10 )
    arg13 = int( request.form["arg13"] )
    arg14 = int( float(request.form["arg14"])*10 )
    arg15 = int( request.form["arg15"] )
    arg16 = int( float(request.form["arg16"])*10 )        
    b = Broker()
    print('set_current_channel_verify_data params ....')
    print(arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,arg10,arg11,arg12,arg13,arg14,arg15,arg16)
    b.current_channel_verify_data=arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,arg10,arg11,arg12,arg13,arg14,arg15,arg16
    print("set_current_channel_verify_data ...")
    return "ok"


@module_bp.route('/humidifier_energy_saving_settings_param')
def humidifier_energy_saving_settings_param():
    return render_template('humidifier_energy_saving_settings_param.html', title='加湿器控制设置', curr_user=current_user.get_id())


@module_bp.route('/api/get_humidifier_energy_saving_settings_param', methods=['POST'])
def get_humidifier_energy_saving_settings_param():
    b = Broker()
    print("get_humidifier_energy_saving_settings_param ...")
    humidifier_energy_saving_settings_param_dict = {}
    ch_data = b.humidifier_energy_saving_settings_param
    ch_data_list = ch_data.split(" ")
    # DATA: 55 0C F0 01 01 14 17 01 01 01 01 01 01 AA
    humidifier_energy_saving_settings_param_dict.update({"loop_mode" : int('0x' + ch_data_list[3], 16)})
    humidifier_energy_saving_settings_param_dict.update({"save_mode" : int('0x' + ch_data_list[4], 16)})
    humidifier_energy_saving_settings_param_dict.update({"save_start_time" : int('0x' + ch_data_list[5], 16)})
    humidifier_energy_saving_settings_param_dict.update({"save_end_time" : int('0x' + ch_data_list[6], 16)})
    humidifier_energy_saving_settings_param_dict.update({"ch1_save" : int('0x' + ch_data_list[7], 16)})
    humidifier_energy_saving_settings_param_dict.update({"ch2_save" : int('0x' + ch_data_list[8], 16)})
    humidifier_energy_saving_settings_param_dict.update({"ch3_save" : int('0x' + ch_data_list[9], 16)})
    humidifier_energy_saving_settings_param_dict.update({"ch4_save" : int('0x' + ch_data_list[10], 16)})
    print(humidifier_energy_saving_settings_param_dict)
    return json.dumps(humidifier_energy_saving_settings_param_dict)



@module_bp.route('/api/set_humidifier_energy_saving_settings_param', methods=['POST'])
def set_humidifier_energy_saving_settings_param():
    print('set_humidifier_energy_saving_settings_param .')
    arg1 = int( request.form["arg1"] )
    arg2 = int( request.form["arg2"] )
    arg3 = int( request.form["arg3"] )
    arg4 = int( request.form["arg4"] )
    arg5 = int( request.form["arg5"] )
    arg6 = int( request.form["arg6"] )
    arg7 = int( request.form["arg7"] )
    arg8 = int( request.form["arg8"] )
    b = Broker()
    print('set_humidifier_energy_saving_settings_param params ....')
    print(arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8)
    b.humidifier_energy_saving_settings_param=arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8
    print("set_humidifier_energy_saving_settings_param ...")
    return "ok"


@module_bp.route('/send_all_area_data')
def send_all_area_data():
    try:
        b = Broker()
        print('send_all_area_data .')
        ch_data = b.send_all_area_data
        ch_data_list = ch_data.split(" ")

        # DATA: 55 0C F0 01 01 14 17 01 01 01 01 01 01 AA
        ch_data_list1 = ch_data_list[6:len(ch_data_list)-2]

        ch_data_list2 = []

        for i in range(0, len(ch_data_list1), 21):
            k = ch_data_list1[i:i+21]
            ch_data_list2.append(k)
        
        f = open('./static/files/history.csv','w',newline='')
        csv_write = csv.writer(f,dialect='excel')
        csv_write.writerow(("时间", "CH1温度", "CH1湿度", "CH2温度", "CH2湿度", "CH3温度", "CH3湿度", "CH4温度", "CH4湿度"))
  
        all_data = []
        for v in ch_data_list2:
            one_data = []
            one_data.append( str(int('0x' + v[20], 16)) + "/" + str(int('0x' + v[19], 16)) + "/" + str(int('0x' + v[18], 16)) + " " + str(int('0x' + v[17], 16)) + ":" + str(int('0x' + v[16], 16)) )
            
            for idx in( 12, 14, 4, 6, 8, 10, 0, 2 ):
                if str(int('0x' + v[idx] + v[idx+1], 16)/10) == '0.0':
                    cd = '-'
                else:
                    cd = str(int('0x' + v[idx] + v[idx+1], 16)/10)
                one_data.append(cd)

            all_data.append(one_data)
            # write a row to csv file ---------------------------------
            csv_write.writerow(one_data)

        f.close()
        print('--------------------------')
        print(all_data)
        print('--------------------------')
        return render_template('send_all_area_data.html', all_data=all_data, title='历史数据查询', curr_user=current_user.get_id())        
    except:
        print("try again ...")
        time.sleep(1)
        return render_template('hint.html', title='温馨提示', curr_user=current_user.get_id())    


@module_bp.route('/air_conditioning_settings_param')
def air_conditioning_settings_param():
    return render_template('air_conditioning_settings_param.html', title='空调保护设置', curr_user=current_user.get_id())


@module_bp.route('/api/get_air_conditioning_settings_param', methods=['POST'])
def get_air_conditioning_settings_param():
    b = Broker()
    print("get_air_conditioning_settings_param ...")
    air_conditioning_settings_param_dict = {}
    data = b.air_conditioning_settings_param
    data_list = data.split(" ")
    # DATA: 55 22 EF 
    # 00 00 00 01 00 00 00 00 03 E6 00 00 03 E6 03 E6 00 00 00 C8 03 E6 00 27 00 78 00 1E 00 78 00 1E AA
    # 参数1:制冷保护(取值0或1)
    # 参数2: 加热保护(取值0或1)
    # 参数3,制冷模式H1(取值0到999)
    # 参数4, 加热模式H1 (取值0到999)
    # 参数5: 制冷模式H2(取值0到999)
    # 参数6: 加热模式H2 (取值0到999)
    # 参数7: 制冷模式T1(取值0到999)
    # 参数8: 加热模式T1 (取值0到999)
    # 参数9: 制冷模式T2(取值0到999)
    # 参数10: 加热模式T2 (取值0到999)
    # 参数11: 抽湿时间(取值0到999)
    # 参数12: 抽湿停止(取值0到999)
    # 参数13: 保留(无实际意义)
    # 参数14: 保留(无实际意义)
    # 参数15: 保留(无实际意义)
    # 参数16: 保留(无实际意义)

    air_conditioning_settings_param_dict.update({"cold_protect" : int('0x' + data_list[3+0] + data_list[3+1], 16)})
    air_conditioning_settings_param_dict.update({"heat_protect" : int('0x' + data_list[3+2] + data_list[3+3], 16)})
    air_conditioning_settings_param_dict.update({"cold_mode_h1" : int('0x' + data_list[3+4] + data_list[3+5], 16)})
    air_conditioning_settings_param_dict.update({"heat_mode_h1" : int('0x' + data_list[3+6] + data_list[3+7], 16)})
    air_conditioning_settings_param_dict.update({"cold_mode_h2" : int('0x' + data_list[3+8] + data_list[3+9], 16)})
    air_conditioning_settings_param_dict.update({"heat_mode_h2" : int('0x' + data_list[3+10] + data_list[3+11], 16)})
    air_conditioning_settings_param_dict.update({"cold_mode_t1" : int('0x' + data_list[3+12] + data_list[3+13], 16)/10 })
    air_conditioning_settings_param_dict.update({"heat_mode_t1" : int('0x' + data_list[3+14] + data_list[3+15], 16)/10 })
    air_conditioning_settings_param_dict.update({"cold_mode_t2" : int('0x' + data_list[3+16] + data_list[3+17], 16)/10 })
    air_conditioning_settings_param_dict.update({"heat_mode_t2" : int('0x' + data_list[3+18] + data_list[3+19], 16)/10 })
    air_conditioning_settings_param_dict.update({"rid_hum_time" : int('0x' + data_list[3+20] + data_list[3+21], 16)})
    air_conditioning_settings_param_dict.update({"rid_hum_stop" : int('0x' + data_list[3+22] + data_list[3+23], 16)})
    print(air_conditioning_settings_param_dict)
    return json.dumps(air_conditioning_settings_param_dict)


@module_bp.route('/api/set_air_conditioning_settings_param', methods=['POST'])
def set_air_conditioning_settings_param():
    print('set_air_conditioning_settings_param .')
    arg1 = int( request.form["arg1"] )
    arg2 = int( request.form["arg2"] )
    arg3 = int( request.form["arg3"] )
    arg4 = int( request.form["arg4"] )
    arg5 = int( request.form["arg5"] )
    arg6 = int( request.form["arg6"] )
    arg7 = int( float(request.form["arg7"])*10 )
    arg8 = int( float(request.form["arg8"])*10 )
    arg9 = int( float(request.form["arg9"])*10 )
    arg10 = int( float(request.form["arg10"])*10 )
    arg11 = int( request.form["arg11"] )
    arg12 = int( request.form["arg12"] )
    b = Broker()
    print('set_air_conditioning_settings_param params ....')
    print(arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,arg10,arg11,arg12)
    b.air_conditioning_settings_param=arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,arg10,arg11,arg12
    print("set_air_conditioning_settings_param ...")
    return "ok"




@module_bp.route('/history_chart')
def history_chart():
    return render_template('histry_chart.html', title='历史数据图表', curr_user=current_user.get_id())

@module_bp.route('/plot1.png')
def plot1_png():
    fig = create_figure1()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure1():
    count = 1
    ch1_time_list = []
    ch1_temp_list = []
    ch1_hum_list = []
    with open('./static/files/history.csv', 'r') as f:
        reader = csv.reader(f)
        for item in reader:
            print(item)
            if count > 30:
                break
            if item[1] == '-' or 'CH' in item[1]:
                continue
            ch1_time_list.append(item[0])
            #CH1 TEMP
            ch1_temp_list.append(item[1])
            #CH1 HUM
            ch1_hum_list.append(item[2])
            count = count + 1
    f.close()

    fig = Figure(figsize=(15, 4))
    # fig = Figure()
    fig.subplots_adjust(wspace = 0.3, hspace = 8)
    #CH1 TEMP

    axis_ch1_temp = fig.add_subplot(1, 2, 1)
    axis_ch1_temp.set_xticklabels(ch1_time_list, rotation='vertical', ha='center')
    axis_ch1_temp.plot(ch1_time_list, ch1_temp_list, label='CH1 Temperature')
    axis_ch1_temp.legend()

    #CH1 HUM
    axis_ch1_hum = fig.add_subplot(1, 2, 2)
    axis_ch1_hum.set_xticklabels(ch1_time_list, rotation='vertical', ha='center')
    axis_ch1_hum.plot(ch1_time_list, ch1_hum_list, label='CH1 Humidity')
    axis_ch1_hum.legend()
    return fig


@module_bp.route('/setting')
def setting():
    return render_template('setting.html', title='系统设置', curr_user=current_user.get_id())


cf = configparser.ConfigParser()
cf.read("Config.ini")
SER_PORT = cf.get("dev", "port")
# SER_BAUDRATE = cf.getint("device", "baudrate")
# GUI_VER = cf.get("GUI Info","Version")

@module_bp.route('/api/get_device_settings', methods=['POST'])
def get_device_settings():
    print('get_device_settings ...')
    data = {}
    portname_str = ""
    for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
        if portname == SER_PORT:
            portname_str = portname_str + "<option selected>" + portname + "</option>"
        else:
            portname_str = portname_str + "<option>" + portname + "</option>"

    data = {"port": portname_str}
    # "baudrate": str(SER_BAUDRATE)
    return json.dumps(data)


@module_bp.route('/api/set_device_settings', methods=['POST'])
def set_device_settings():
    print('set_device_settings ...')
    device_port_val = request.form["device_port_val"]
    cf.set("dev", "port", device_port_val)

    with open("Config.ini", "w+") as f:
	    cf.write(f)
	
    return "Set successfully."


@module_bp.route('/api/get_temp_hum_chart_data_by_ch', methods=['POST'])
def get_temp_hum_chart_data_by_ch():
    count = 1
    ch1_time_list = []
    ch1_temp_list = []
    ch1_hum_list = []
    with open('./static/files/history.csv', 'r') as f:
        reader = csv.reader(f)
        for item in reader:
            print(item)
            if count > 30:
                break
            if item[1] == '-' or 'CH' in item[1]:
                continue
            ch1_time_list.append(item[0])
            #CH1 TEMP
            ch1_temp_list.append(item[1])
            #CH1 HUM
            ch1_hum_list.append(item[2])
            count = count + 1
    f.close()

    ch1_time_list.reverse()
    ch1_temp_list.reverse()
    ch1_hum_list.reverse()
    return json.dumps([ch1_time_list,ch1_temp_list,ch1_hum_list])

