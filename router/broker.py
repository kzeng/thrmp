import serial
import time

from router.utility import *


import serial.tools.list_ports
import configparser

class Broker(serial.Serial):
    # 57600bps,数据位8,停止位1,校验位无
    def __init__(self):
        super(Broker, self).__init__()
        self.baudrate = 57600
        # self.baudrate = 38400
        # port will get from config file
        cf = configparser.ConfigParser()
        cf.read("Config.ini")
        SER_PORT = cf.get("dev", "port")
        self.port = SER_PORT
        # self.port = "COM4"


    ##############################################################
    #
    # 获取参数
    #
    ###############################################################
    # 1,获取当前记录的总块
    # 格式:55 02 FA AA
    # 返回: 55 04 FA xx xx AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # Xx xx表示总块 16进制表示,高位在前,低位在后
    @property
    def current_record_count(self):
        self.open()
        cmd = [0x55, 0x02, 0xFA, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        # print(str(buffer_string))


    # 2, 获取当前临时记录的字节数
    # 格式:55 02 FB AA
    # 返回:  55 04 FB xx xx AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # Xx xx表示总块 16进制表示,高位在前,低位在后
    @property
    def current_temporary_record_bytes(self):
        self.open()
        cmd = [0x55, 0x02, 0xFB, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        # print(str(buffer_string))


    # 3, 发送临时存储区的数据
    # 格式: 55 02 FC AA
    # 返回: 55 xx xx fc xx xx xx xx ……………… AA
    # 55后两字节表示后续有多少个字节
    # FC 命令字，FC后数据
    # 数据格式：按下面的顺序排例，依次顺序排列
    # 通道4温度（2字节），通道4湿度（2字节），通道2湿度（2字节），通道2湿度（2字节），
    # 通道3温度（2字节），通道3湿度（2字节），通道1温度（2字节），通道1湿度（2字节），
    # 分（1字节），时（1字节），日（1字节），月（1字节），年（1字节）
    @property
    def send_temporary_area_data(self):
        self.open()
        cmd = [0x55, 0x02, 0xFC, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        # print(str(buffer_string))


    # 4, 发送所有存储区的数据
    # 格式: 55 02 FD AA
    # 返回: 55 xx xx xx xx fDxx xx xx xx ……………… AA
    # 55后四字节表示后续还有多少个字节
    # FD 命令字，FD后数据
    # 数据格式：按下面的顺序排例，依次顺序排列
    # 通道4温度（2字节），通道4湿度（2字节），通道2湿度（2字节），通道2湿度（2字节），
    # 通道3温度（2字节），通道3湿度（2字节），通道1温度（2字节），通道1湿度（2字节），
    # 分（1字节），时（1字节），日（1字节），月（1字节），年（1字节）
    # 数据存储的策略是先在存储器中开一个小区域用于存放临时的记录数据，存满一个区块的数块的数据后，再统一存在数据存储器中。用于提高效率
    @property
    def send_all_area_data(self):
        # self.open()
        # cmd = [0x55, 0x02, 0xFD, 0xAA]
        # self.write(cmd)
        # time.sleep(0.5)
        # buffer_string = b''
        # while True:
        #     buffer_string = buffer_string + self.read(self.inWaiting())
        #     # time.sleep(0.1)
        #     if self.read(self.inWaiting()) == b'':
        #         break
        # self.close()
        self.open()
        self.flushInput()
        self.flushOutput()

        cmd = [0x55, 0x02, 0xFD, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while self.inWaiting() > 0:
            b=self.read(1)
            time.sleep(0.0001)
            buffer_string += b

        self.close()        
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        return data
        # print(str(buffer_string))


    # 5, 获取当前运行的时间
    # 格式:55 02 FEAA
    # 返回:  55 06 FE xx xx xx xx AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # FE命令字，后续四字节按 16进制表示总运行时间,高位在前,低位在后
    @property
    def current_run_time(self):
        self.open()
        cmd = [0x55, 0x02, 0xFE, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        return "{}".format(data)
        # print(str(buffer_string))


    # 6, 获取各通道的控制设置数据
    # 格式:55 03 F9 xx AA 其中xx 取值（00,01,02,03）
    # 返回:  55 1B F9 aa xx xx xx ……… AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # F9命令字，aa表示当前通道，取值（00,01,02,03）
    def channel_control_settings(self, ch):
        self.open()
        cmd = [0x55, 0x03, 0xF9, ch, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        
        if data == '':
            self.channel_control_settings(ch)
        
        print('CHANNEL #', ch)
        print("DATA: {}".format(data))
        return "{}".format(data)
        # return 'channel_control_settings ok...'
        # print(str(buffer_string))


    # 7, 获取仪表的重开机次数
    # 格式:55 02 F8 AA
    # 返回:  55 04 F8 xx xx AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # F8命令字，后续二字节按 16进制表示重开机次数,高位在前,低位在后
    @property
    def device_reboot_count(self):
        self.open()
        cmd = [0x55, 0x02, 0xF8, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        # print(str(buffer_string))


    # 8, 获取当前各通道采集数据
    # 格式:55 02 F7 AA
    # 返回:  55 14 F7 xx xx xx xx ……………… AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # F7命令字，后续每两字节按 16进制表示采集数据,高位在前,低位在后
    # 排列顺序如下：
    # 通道1湿度（2字节），通道1温度（2字节），通道2湿度（2字节），通道2温度（2字节）
    # 通道3湿度（2字节），通道3温度（2字节），通道4湿度（2字节），通道4温度（2字节）
    @property
    def channel_collect_data(self):
        self.open()
        cmd = [0x55, 0x02, 0xF7, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        return "{}".format(data)
        # print(str(buffer_string))


    # 9, 获取当前各通道校正数据
    # 格式:55 02 F5 AA
    # 返回:  55 1A F5 xx xx xx xx ……………… AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # F5命令字，后续每三字节按 16进制表示校正数据,第一位表示符号位，后两位表示校正数据，高位在前,低位在后
    # 排列顺序如下：
    # 通道1温度符号（1字节）通道1温度校正值（2字节）
    # 通道1湿度符号（1字节）通道1湿度校正值（2字节），
    # 通道2温度符号（1字节）通道2温度校正值（2字节），
    # 通道2湿度符号（1字节）通道2湿度校正值（2字节）
    # 通道3温度符号（1字节）通道3温度校正值（2字节），
    # 通道3湿度符号（1字节）通道3湿度校正值（2字节），
    # 通道4温度符号（1字节）通道4温度校正值（2字节），
    # 通道4湿度符号（1字节）通道4湿度校正值（2字节）
    # 其中符号位0表示－，1表示+
    @property
    def current_channel_verify_data(self):
        self.open()
        cmd = [0x55, 0x02, 0xF5, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        return "{}".format(data)
        # print(str(buffer_string))


    # 10, 获取仪表的控制通道数
    # 格式:55 02 F4 AA
    # 返回:  55 03F4 xx AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # F4命令字，后续一字节按 16进制表示重开机次数 (控制通道数？)
    @property
    def device_control_channel_count(self):
        self.open()
        cmd = [0x55, 0x02, 0xF4, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        # print(str(buffer_string))


    # 11, 获取记录数据设置
    # 格式:55 02 F3 AA
    # 返回:  55 08 F3 xx xx xx xx xx xx AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # F4命令字，后续一字节按 16进制表示记录设置参数，每一参数占用一字节(应为F3？)
    @property
    def record_data_setting(self):
        self.open()
        cmd = [0x55, 0x02, 0xF3, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        return data
        # print(str(buffer_string))


    # 12, 获取每通道控制输出状态
    # 格式:55 02 F2 AA
    # 返回:  55 06 F2 xx xx xx xx AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # F4命令字，后续一字节按 16进制表示每通道输出状态，每一参数占用一字节，每个控制状态按位表示，如0X04 二进制为 00 00 01 00，表示化霜状态，   从低到高每个状态为：加热，制冷，化霜，加湿，抽湿。
    @property
    def channel_control_output_state(self):
        self.open()
        cmd = [0x55, 0x02, 0xF2, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        # print(str(buffer_string))


    # 13, 获取高级设置参数
    # 格式:55 02 F1 AA
    # 返回:  55 12 F1 xx xx xx xx……… AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # F1命令字，后续字节按 16进制表示，每一参数占用二字节，
    @property
    def advance_setting_param(self):
        self.open()
        cmd = [0x55, 0x02, 0xF1, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        d = data.split(' ')
        # ['55', '12', 'F1', '00', '59', '03', '1F', '03', 'DE', '00', '13', '00', '00', '00', '00', '00', '00', '00', '01', 'AA','']
        # # 仪表编号	
        device = int('0x' + d[3] + d[4], 16)
        # 运行时间	
        run_time = int('0x' + d[5] + d[6], 16)
        # 水温设置
        water_temp = int('0x' + d[7] + d[8], 16)/10
        # 水温容差	
        water_temp1 = int('0x' + d[9] + d[10], 16)/10
        # 时钟选择	
        clock = int('0x' + d[11] + d[12], 16)
        # 存储单位
        save_id = int('0x' + d[13] + d[14], 16)
        # 整点存储
        save_point = int('0x' + d[15] + d[16], 16)
        return str(device)+','+ str(run_time) +',' + str(water_temp) + ',' + str(water_temp1) + ',' + str(clock) + ',' + str(save_id) + ',' + str(save_point)




    # 14, 获取加湿器节能设置参数
    # 格式:55 02 F0 AA
    # 返回:  55 0C F0 xx xx xx xx……… AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # F0命令字，后续字节按 16进制表示，每一参数占用一字节，
    @property
    def humidifier_energy_saving_settings_param(self):
        self.open()
        cmd = [0x55, 0x02, 0xF0, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        return data
        # print(str(buffer_string))


    # 15, 获取空调相关设置参数
    # 格式:55 02 EF AA
    # 返回:  55 22 EF xx xx xx xx……… AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # EF命令字，后续字节按 16进制表示，每一参数占用二字节，
    @property
    def air_conditioning_settings_param(self):
        self.open()
        cmd = [0x55, 0x02, 0xEF, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        return data
        # print(str(buffer_string))


    # 10a，主界面数据及状态
    # 格式：55 02 EE AA
    # 返回：55 56 EE  aa  bb cc  d1 d2  ee  t1 t2 t3 t4  t5  t6  
    # 01  00 C8 03 26  00 C8  00 0A  03 C0  00 32  01 00 00 00 00 	  第一通道数据
    # 00  00 00 00 00  00 C8  00 0A  02 94  00 32  00 00 00 00 00    第二通道数据
    # 00  00 00 00 00  00 C8  00 0A  03 C0  00 32  01 00 00 00 00     第三通道数据
    # 00  00 00 00 00  00 C8  00 0A  03 C0  00 32  01 00 00 01 00     第四通道数据
    # AA

    # 说明：55开头,AA结尾第二字表示后续还有几个字节，56指后续有86字节，所有字节均为16进制

    # aa,表示设备编号
    # bb,表示控制通道数
    # cc,表示当前运行状态
    # d1,d2表示当前运行的总时间 高位在前，低位在后
    # ee,	表示记录间隔
    # t1,t2,t3,t4,t5,t6 表示当时间，按年，月，日，周，时，分依次
    # 后续表示各通道数据，以第一通道说明，其它通道依次类推。
    # 下面的表述字节按格式来说明，字节的位置仅表示在当前的位置 ，不表示在整个命令中的位置
    # 第1字节，表示传感器存在与否（1表示存在，0表示不存在），不存在时，温湿度上传数据为0，在界面上显示为“――――”
    # 第2，3字节为温度数据，高位在前，低位在后。实际显示时应缩小10位，取得一位小数。如本次收到00C8，实际显示为20.0.
    # 第4，5字节为湿度数据，高位在前，低位在后。实际显示时应缩小10位，取得一位小数。如本次收到0326，实际显示为80.6.

    # 第6，7字节为温度设置目标数据，高位在前，低位在后。实际显示时应缩小10位，取得一位小数。如本次收到00C8，实际显示为20.0.
    # 第8，9字节为温度设置容差数据，高位在前，低位在后。实际显示时应缩小10位，取得一位小数。如本次收到000A，实际显示为1.0.

    # 第10，11字节为湿度设置目标数据，高位在前，低位在后。实际显示时应缩小10位，取得一位小数。如本次收到03C0，实际显示为96.0.
    # 第12，13字节为湿度设置容差数据，高位在前，低位在后。实际显示时应缩小10位，取得一位小数。如本次收到0032，实际显示为5.0.
    # 第14字节，表示控制模式（1表示循环，0表示自动），显示时应判断传感器是否存在，存在显示对应的模式，不存在不显示。
    # 第15字节，表示控制策略（1表示节能， 0表示无（不显示））， 显示时应判断传感器是否存在，存在显示节能，不存在不显示。
    # 第16字节，表示空调保护状态，以位的形式表示制冷与加热（二进制00，10，01，分别对应没有保护，制冷保护，加热保记）， 显示时应判断传感器是否存在，存在时00不显示，10显示制冷保护，10显示加热保护。
    # 第17字节，表示控制输出状态，以位的形式表示控制输出状态，显示时应判断传感器是否存在，存在时显示对应的状态，不存在时不显示。
    # 请注意，如0X05 二进制为 00000101，表示化霜状态，（化霜时要保持加热功能打开）
    # 其它 ，如0X01 二进制为 00000001，表示加热状态，
    # 其它 ，如0X01 二进制为 00010001，表示加热状态和抽湿状态

    # 从低到高每个状态为：加热，制冷，化霜，加湿，抽湿.
    # 第18字节，保留
    @property
    def dashboard_info(self):
        self.open()
        cmd = [0x55, 0x02, 0xEE, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        return data
        # print(str(buffer_string))


    # ####################################################################
    #
    # #16-18 清除命令
    #
    # ####################################################################
    # 16, 清除所有参数
    # 格式:55 02 EA AA
    # 返回:  55 02 EA AA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # EA命令字
    @property
    def remove_all_param(self):
        self.open()
        cmd = [0x55, 0x02, 0xEA, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        # print(str(buffer_string))


    # 17, 清除所有记录
    # 格式:55 02 EB AA
    # 返回:无
    @property
    def remove_all_records(self):
        self.open()
        cmd = [0x55, 0x02, 0xEB, 0xAA]
        self.write(cmd)
        # rx = self.readline()
        self.close()
        # print(rx)
        return "OK"


    # 18, 清除运行时间
    # 格式:55 02 EC AA
    # 返回: 55 02 EC AA
    @property
    def remove_run_time(self):
        self.open()
        cmd = [0x55, 0x02, 0xEC, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        # print(str(buffer_string))



    # 19, 获取试用标记和试用时间参数
    # 格式:55 02 ED AA
    # 返回:  55 06 ED xx xx xx xxAA
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # ED命令字，后续字节按 16进制表示，每一参数占用二字节，前两字节表示试用标记，以0和1表示，0表示未开启试用（默认），1表示开启试用。后两字节表示试用时间
    @property
    def try_mark_and_try_time_param(self):
        self.open()
        cmd = [0x55, 0x02, 0xED, 0xAA]
        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while True:
            buffer_string = buffer_string + self.read(self.inWaiting())
            if self.read(self.inWaiting()) == b'':
                break
        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        # print(str(buffer_string))


    ##############################################################
    #
    # 设置参数
    #
    ###############################################################
    # 1,时间设置
    # 格式：55 09 D9 XX XX XX XX XX XX XX AA
    # 返回： 无
    # 55 开头，AA 结尾 
    # 数据区按年，月，日，周(不用输入，0占位)，时，分，秒 （不用输入，0占位）排列，每个参数占一字节，以16进制表示
    @property
    def datetime_setting(self):
        pass

    @datetime_setting.setter
    def datetime_setting(self, vals):
        self.open()
        cmd = [0x55, 0x09, 0xD9]
        for v in vals:
            cmd.append(int(v))

        cmd.append(0xAA)
        self.write(cmd)
        time.sleep(0.5)
        self.close()
        print("datetime_setting ok...")


    # 3，设置记录参数
    # 格式：55 08 DC XX XX XX XX XX XX AA
    # 返回：无
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # DC命令字，后续字节按 16进制表示，后续每一参数占用一字节，共6个参数，一起6字节
    # Get method, See #11, 
    @record_data_setting.setter
    def record_data_setting(self, vals):
        self.open()
        cmd = [0x55, 0x08, 0xDC]
        for v in vals:
            cmd.append(int(v))

        cmd.append(0xAA)
        self.write(cmd)
        time.sleep(0.5)
        self.close()
        print("record_data_setting ok...")


    # 5，设置高级设置参数
    # 格式：55 12 D8 XX XX XX XX XX XX……… AA
    # 返回：无
    # 55开头,AA结尾 第二字表示后续还有几个字节
    # D8命令字，后续字节按 16进制表示，后续每一参数占用二字节，共8个参数 
    @advance_setting_param.setter
    def advance_setting_param(self, vals):
        self.open()
        cmd = [0x55, 0x12, 0xD8]
    
        for v in vals:
            # cmd.append(int(v))
            cmd.append(int("{:04x}".format(int(v))[0:2], 16))
            cmd.append(int("{:04x}".format(int(v))[2:4], 16))

        cmd.append(0xAA)
        self.write(cmd)
        time.sleep(0.5)
        self.close()
        print("advance_setting_param ok...")




    # 2，设置各通道控制参数
    # 格式：55 1B DA aa  XX XX XX XX XX XX XX………AA
    # 返回：无
    # 55开头,AA结尾第二字表示后续还有几个字节
    # DA命令字，后续字节按 16进制表示，aa 表示要设置的通道，后续每一参数占用二字节，共12个参数，加上通道数，一共是13个参数，一起25字节

    @property
    def channel_control_settings_by_ch(self):
        pass

    @channel_control_settings_by_ch.setter
    def channel_control_settings_by_ch(self, vals):
        self.open()
        cmd = [0x55, 0x1B, 0xDA]
        n = 0

        for v in vals:
            # cmd.append(int(v))
            if n == 0:
                # fill channel number, only 1 byte
                # cmd.append(int("{:04x}".format(int(v))[0:2], 16))
                cmd.append(int("{:04x}".format(int(v[0])), 16))
            else:
                # fill other param, 2 bytes
                cmd.append(int("{:04x}".format(int(v))[0:2], 16))
                cmd.append(int("{:04x}".format(int(v))[2:4], 16))
            n = n + 1

        cmd.append(0xAA)
        print(cmd)
        self.write(cmd)
        time.sleep(0.5)
        self.close()
        print("channel_control_settings ok...")        


    # 4, 设置当前各通道校正数据
    # 格式:55 1A DD xx xx xx xx ……………… AA
    # 返回:  无
    # DD 命令字，后续每三字节按 16进制表示校正数据,第一位表示符号位，后两位表示校正数据，高位在前,低位在后
    # 排列顺序如下：
    # 通道1温度符号（1字节）通道1温度校正值（2字节）
    # 通道1湿度符号（1字节）通道1湿度校正值（2字节），
    # 通道2温度符号（1字节）通道2温度校正值（2字节），
    # 通道2湿度符号（1字节）通道2湿度校正值（2字节）
    # 通道3温度符号（1字节）通道3温度校正值（2字节），
    # 通道3湿度符号（1字节）通道3湿度校正值（2字节），
    # 通道4温度符号（1字节）通道4温度校正值（2字节），
    # 通道4湿度符号（1字节）通道4湿度校正值（2字节）
    # 其中符号位0表示－，1表示+
    @current_channel_verify_data.setter
    def current_channel_verify_data(self, vals):
        self.open()
        cmd = [0x55, 0x1A, 0xDD]
        n = 0
        # 551ADD000000010000010000010000010000010000010000010000AA
        for v in vals:
            # cmd.append(int(v))
            if n in (0,2,4,6,8,10,12,14):
                # fill channel number, only 1 byte
                # cmd.append(int("{:04x}".format(int(v))[0:2], 16))
                cmd.append(int("{:02x}".format(int(v)), 16))
            else:
                # fill other param, 2 bytes
                cmd.append(int("{:04x}".format(int(v))[0:2], 16))
                cmd.append(int("{:04x}".format(int(v))[2:4], 16))

            n = n + 1

        cmd.append(0xAA)
        self.write(cmd)
        time.sleep(0.5)
        self.close()
        print("current_channel_verify_data ok...")



    # 6，设置加湿器设置参数
    # 格式：55 0C D7 XX XX XX XX XX XX……… AA
    # 返回：无
    # 55开头,AA结尾第二字表示后续还有几个字节
    # D7命令字，后续字节按 16进制表示，后续每一参数占用一字节，共10个参数
    # 从D7到AA之间共10字节,每一个字节表一个参数, 共10个参数
    # 例如: 0C 表示12.
    # 参数1,循环模式(取值0或1)
    # 参数2:节能模式(取值0或1)
    # 参数3,节能开始时间(取值0到23)
    # 参数4, 节能结束时间(取值0到23)
    # 参数5: 第一路节能(取值0或1)
    # 参数6: 第二路节能(取值0或1)
    # 参数7: 第三路节能(取值0或1)
    # 参数8: 第四路节能(取值0或1)
    # 参数9: 保留(无实际意义)
    # 参数10: 保留(无实际意义)
    @humidifier_energy_saving_settings_param.setter
    def humidifier_energy_saving_settings_param(self, vals):
        self.open()
        cmd = [0x55, 0x0C, 0xD7]
        print('+++++++++++++++++++++++++++++++++++')
        print(vals)
        print('+++++++++++++++++++++++++++++++++++')
        for v in vals:
            cmd.append(int("{:02x}".format(int(v)), 16))
            
        cmd.append(0x01)
        cmd.append(0x01)
        cmd.append(0xAA)
        self.write(cmd)
        time.sleep(0.5)
        self.close()
        print("humidifier_energy_saving_settings_param ok...")



    # 7，设置空调的相关设置参数
    # 格式：55 22 D6 XX XX XX XX XX XX……… AA
    # 返回：无
    @air_conditioning_settings_param.setter
    def air_conditioning_settings_param(self, vals):
        self.open()
        cmd = [0x55, 0x22, 0xD6]
        n = 0
        print('---------------------------')
        print(vals)
        print('---------------------------')

        for v in vals:
            cmd.append(int("{:04x}".format(int(v))[0:2], 16))
            cmd.append(int("{:04x}".format(int(v))[2:4], 16))

        cmd.append(0x00)
        cmd.append(0x00)
        cmd.append(0x00)
        cmd.append(0x00)
        cmd.append(0x00)
        cmd.append(0x00)
        cmd.append(0x00)
        cmd.append(0x00)
        cmd.append(0xAA)
        self.write(cmd)
        time.sleep(0.5)
        self.close()
        print("air_conditioning_settings_param ok...")


    # send commands from console
    def send_debug_cmdstr(self, cmdstr):
        self.open()
        self.flushInput()
        self.flushOutput()
        # cmd = [0x55, 0x02, 0xFA, 0xAA]
        cmd = []
        cmd_words = cut(cmdstr, 2)

        for i in cmd_words:
            cmd.append( int('0x'+ str(i), 16) )

        self.write(cmd)
        time.sleep(0.5)
        buffer_string = b''
        while self.inWaiting() > 0:
            b=self.read(1)
            time.sleep(0.0001)
            buffer_string += b

        self.close()
        data = ''.join(['%02X ' %x  for x in buffer_string])
        print("DATA: {}".format(data))
        return(str(data))

