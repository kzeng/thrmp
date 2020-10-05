import time
from broker import Broker


b = Broker()
# b.port = "COM4"

print("-"*60)
print("-- API测试：获取参数")
print("-"*60)

print("1,获取当前记录的总块")
b.current_record_count
time.sleep(0.2)
print("\n")

print("2, 获取当前临时记录的字节数")
b.current_temporary_record_bytes
time.sleep(0.2)
print("\n")

print("3, 发送临时存储区的数据")
b.send_temporary_area_data
time.sleep(0.2)
print("\n")

print("4, 发送所有存储区的数据")
b.send_all_area_data
time.sleep(0.2)
print("\n")

print("5, 获取当前运行的时间")
b.current_run_time
time.sleep(0.2)
print("\n")

print("6, 获取各通道的控制设置数据")
b.channel_control_settings(0)
time.sleep(0.2)
b.channel_control_settings(1)
time.sleep(0.2)
b.channel_control_settings(2)
time.sleep(0.2)
b.channel_control_settings(3)
time.sleep(0.2)
print("\n")

print("7, 获取仪表的重开机次数")
b.device_reboot_count
time.sleep(0.2)
print("\n")

print("8, 获取当前各通道采集数据")
b.channel_collect_data
time.sleep(0.2)
print("\n")

print("9, 获取当前各通道校正数据")
b.current_channel_verify_data
time.sleep(0.2)
print("\n")

print("10, 获取仪表的控制通道数")
b.device_control_channel_count
time.sleep(0.2)
print("\n")

print("11, 获取记录数据设置")
b.record_data_setting
time.sleep(0.2)
print("\n")

print("12, 获取每通道控制输出状态")
b.channel_control_output_state
time.sleep(0.2)
print("\n")

print("13, 获取高级设置参数")
b.advance_setting_param
time.sleep(0.2)
print("\n")

print("14, 获取加湿器节能设置参数")
b.humidifier_energy_saving_settings_param
time.sleep(0.2)
print("\n")

print("15, 获取空调相关设置参数")
b.air_conditioning_settings_param
time.sleep(0.2)
print("\n")

# 16, 清除所有参数
# b.remove_all_param
# time.sleep(0.2)
# print("\n")

# 17, 清除所有记录
# b.remove_all_records
# time.sleep(0.2)
# print("\n")

# 18, 清除运行时间
# b.remove_run_time
# time.sleep(0.2)
# print("\n")

print("19, 获取试用标记和试用时间参数")
b.try_mark_and_try_time_param
time.sleep(0.2)
print("\n")


print("10a, 主界面数据及状态")
b.dashboard_info
time.sleep(0.2)
print("\n")


############################################################################################

print("-"*60)
print("-- API测试：设置参数")
print("-"*60)

print("1, 时间设置")
year = int(time.strftime("%Y", time.localtime())[2:])
month = int(time.strftime("%m", time.localtime()))
day = int(time.strftime("%d", time.localtime()))
hour = int(time.strftime("%H", time.localtime()))
min = int(time.strftime("%M", time.localtime()))
second = int(time.strftime("%S", time.localtime()))
print(year,month,day,0,hour,min,second)
b.datetime_setting=year,month,day,0,hour,min,second
time.sleep(0.2)
print("\n")


print("3，设置记录参数")
# 数据记录间隔（小时）,数据更新间隔（秒）,背光亮度（%）,休眠时间（分）,自动刷新（分）,01 ??
b.record_data_setting=3,5,90,60,3,1
time.sleep(0.2)
print("\n")


print("5，设置高级设置参数")
# 0059 031f 03de 0058 0001 0000 0000
b.advance_setting_param=29,99,90.0*10,1.9*10,1,1,0,1
time.sleep(0.2)
print("\n")


print("\n")
print("\n\nALL APIS TEST DONE!")

