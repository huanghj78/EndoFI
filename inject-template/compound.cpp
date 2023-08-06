#include <iostream>
#include <chrono>
#include <unistd.h>
#include <cmath>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h> // 导入系统调用函数所需的头文件
#include <fcntl.h> // 导入open函数所需的标志位

__attribute__((constructor))
void load() {
  // 设置目标 CPU 利用率，范围为 0 到 100
  const int TARGET_CPU_USAGE=80; 
  // 设置每次循环的时间间隔，单位为微秒
  const int INTERVAL = 10000; 
  // 设置程序的持续时间，单位为毫秒
  const int DURATION; 
  // 设置程序达到目标 CPU 利用率的时间，单位为毫秒
  const int RAMP_UP_TIME; 
  // 计算循环的次数
  const int LOOP_COUNT = DURATION * 1000 / INTERVAL; 
  // 计算达到目标 CPU 利用率的次数
  const int RAMP_UP_COUNT = RAMP_UP_TIME * 1000 / INTERVAL; 
  // 计算每次循环增加的 CPU 利用率，使用浮点数
  const double CPU_USAGE_INCREMENT = (double) TARGET_CPU_USAGE / RAMP_UP_COUNT; 

  // 初始化当前 CPU 利用率为 0
  double current_cpu_usage = 0; 

  // 记录初始时间
  auto start = std::chrono::high_resolution_clock::now ();
  
  for (int i = 0; i < LOOP_COUNT; i++) {
    // 如果还没有达到目标 CPU 利用率，每次循环增加一定的 CPU 利用率
    if (current_cpu_usage < TARGET_CPU_USAGE) {
      current_cpu_usage += CPU_USAGE_INCREMENT;
    }
    // 计算取指执行的时间，单位为微秒，使用 round 函数四舍五入
    int exec_time = round(INTERVAL * current_cpu_usage / 100); 
    // 计算睡眠的时间，单位为微秒，使用 round 函数四舍五入
    int sleep_time = round(INTERVAL - exec_time); 
    // 取指执行的时间为 exec_time 微秒
    while (std::chrono::duration_cast<std::chrono::microseconds> (std::chrono::high_resolution_clock::now () - start).count () < exec_time) {
    }
    // 睡眠的时间为 sleep_time 微秒
    usleep (sleep_time);
    // 更新初始时间
    start = std::chrono::high_resolution_clock::now ();
  }

}