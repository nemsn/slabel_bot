# -*- coding:utf-8 -*-
import os
import psutil
from datetime import datetime

MEGA = 1024 * 1024
GIGA = MEGA * 1024
MINUTES = 60
HOUR = MINUTES * 60


############################## CPU ###############################
# CPU time
def get_cpu_time():
	cpu_times = psutil.cpu_times()
	s = "---------- CPU time ---------- \n"
	s += "* ユーザー時間(分)      \t" + str(round(cpu_times.user/MINUTES, 1)) + "\n"
	s += "* カーネル時間(分)      \t" + str(round(cpu_times.system/MINUTES, 1)) + "\n"
	s += "* 待機時間(分)        \t" + str(round(cpu_times.idle/MINUTES, 1)) + "\n"

	return s


### CPU使用率
def get_cpu_percent(count=3):
	count = 3 #とりあえず1秒間計測を3回
	per = 0
	for x in range(count):
		# コアごとの使用率を取得したい場合percpuを引数でTrueに指定
		# 初回はinterval必須っぽいが一度実行すれば引数なしで最後に計測してからのパーセンテージになる
		n = psutil.cpu_percent(interval=1)
		per += n

	s = "---------- CPU percentage ---------- \n"
	s += "* 現在のcpu使用率(3秒平均)   \t" + str(round(per/count, 1)) + "\n"

	return s

### CPUコア数
def get_cpu_count():
	s = "---------- CPU count ----------\n"
	s += "* CPUコア数（物理）      \t" + str(psutil.cpu_count(logical=False)) + "\n"

	return s

### ブートしてからのCPUの様々な情報（適当）
def get_cpu_stat():
	cpu_stats = psutil.cpu_stats()
	s = "---------- CPU status ----------\n"
	s += "* コンテキストスイッチ回数 \t" + str(cpu_stats.ctx_switches) + "\n"
	s += "* 割り込み回数        \t" + str(cpu_stats.interrupts) + "\n"
	s += "* ソフトによる割り込み回数\t" + str(cpu_stats.soft_interrupts) + "\n"
	s += "* システムコール回数     \t" + str(cpu_stats.syscalls) + "\n"

	return s


############################## MEMORY ###############################
### メモリ 
def get_virtual_memory():
	mem = psutil.virtual_memory()
	s = "---------- virtual memory ----------\n"
	s += "* メモリ総量(MB)        \t" + str(round(mem.total/MEGA, 1)) + "\n"
	s += "* 利用可能(MB)         \t" + str(round(mem.available/MEGA, 1)) + "\n"
	s += "* メモリ使用率（%）        \t" + str(mem.percent) + "\n"
	s += "* メモリ使用量(MB)       \t" + str(round(mem.used/MEGA, 1)) + "\n"
	s += "* メモリ未使用領域(MB)   \t" + str(round(mem.free/MEGA, 1)) + "\n"

	return s

### スワップメモリ情報
def get_swap_memory():
	smem = psutil.swap_memory()
	s = "---------- swap memory ----------\n"
	s += "* スワップメモリ総量(MB)    \t" + str(round(smem.total/MEGA, 1)) + "\n"
	s += "* スワップメモリ使用量(MB)  \t" + str(round(smem.used/MEGA, 1)) + "\n"
	s += "* スワップ空き容量(MB)     \t" + str(round(smem.free/MEGA, 1)) + "\n"
	s += "* スワップ使用率（%）      \t" + str(smem.percent) + "\n"
	s += "* sin                 \t" + str(smem.sin) + "\n"
	s += "* sout                \t" + str(smem.sout) + "\n"

	return s

############################## DISK ###############################
# ディスクパーティション
def get_disk_partitions():
	### ディスクパーティション
	# 引数にall=Trueで仮想ドライブも表示？
	partitions = psutil.disk_partitions()
	s = "---------- disk partitoins ----------\n"
	for p in partitions:
		s += "--------------------\n"
		s += "* デバイス名    \t" + str(p.device) + "\n"
		s += "* マウントポイント \t" + str(p.mountpoint) + "\n"
		s += "* ファイルシステム \t" + str(p.fstype) + "\n"
		s += "* ドライブタイプ   \t" + str(p.opts) + "\n"

	return s

# ディスク詳細
def get_disk_usage():
	# Linuxならこっちのほうがいいかも
	#usage = psutil.disk_usage("/")
	partitions = psutil.disk_partitions()
	s = "---------- disk usage ----------\n"
	for p in partitions:
		if p.fstype is not None:
			# Todo: 存在確認しないとPermissionErrorになる(Windows)　なんででしょうか？木霊でしょうか？
			if os.path.exists(p.device):
			### ディスク詳細
				u = psutil.disk_usage(p.device)
				s += "* デバイス名       \t" + str(p.device) + "\n"
				s += "* ディスク総量(GB)  \t" + str(round(u.total/GIGA, 1)) + "\n"
				s += "* ディスク使用量(GB)  \t" + str(round(u.used/GIGA, 1)) + "\n"
				s += "* 空き容量(GB)    \t" + str(round(u.free/GIGA, 1)) + "\n"
				s += "* ディスク使用率(%)  \t" + str(u.percent) + "\n"

	return s

### ディスクI/O情報
def get_disk_io_counters():
	iocount = psutil.disk_io_counters(perdisk=True)
	s = "---------- disk I/O counter ----------\n"
	for k, io in iocount.items():
		s += "* ドライブ         \t" + str(k) + "\n"
		s += "* 読み込み回数    \t" + str(io.read_count) + "\n"
		s += "* 書き込み回数    \t" + str(io.write_count) + "\n"
		s += "* 読み込み容量（MB）\t" + str(round(io.read_bytes/MEGA, 1)) + "\n"
		s += "* 書き込み容量（MB）\t" + str(round(io.write_bytes/MEGA, 1)) + "\n"

	return s

### CPU
def get_cpuinfo():
	s = get_cpu_time()
	s += get_cpu_percent()
	s += get_cpu_count()
	s += get_cpu_stat()

	return s

### MEMORY
def get_memoryinfo():
	s = get_virtual_memory()
	s += get_swap_memory()

	return s

### Disk
def get_diskinfo():
	s = get_disk_partitions()
	s += get_disk_usage()
	s += get_disk_io_counters()
	
	return s

## BOTの返信用　個別機能の判定をする予定（CPU使用率のみとか）
def get_miku_houseinfo(text=None):
	s = "\n"
	#s += get_cpuinfo()
	s += get_memoryinfo()
	s += get_diskinfo()

	return s

if __name__ == "__main__":
	#print(get_miku_houseinfo())
	print(get_cpuinfo())
	#print(get_memoryinfo())
	#print(get_diskinfo())
