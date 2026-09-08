# TT-02 Taxi autonome：补全架构图说明

日期：2026-09-08。

依据：用户手绘架构图，以及本项目当前已有硬件盘点。用户本轮明确确认：图中的 Interrupteur 表示电池总开关。

本次交付是功能架构与供电分配方案，不是已经核验的实车接线图；没有执行接线、上电、固件修改、模式切换、采购或硬件测试。原始手绘照片保持不变。

补全后的图片：[法语架构图PNG](TAXI_TT02_ARCHITECTURE_COMPLETED.png)。

对应的实际核对操作与记录表：[逐步核对规程](TAXI_TT02_VERIFICATION_STEPS_ZH.md)。规程尚未填入实测结果。

## 图片检查

已逐条查看最终生成图：雷达USB路径单独连接树莓派；UART指令与反馈分开标向；I²C、经过输入适配的ADC与光电叉定时器路径分别进入STM32；电调功率输出和舵机控制分开；BEC从电调单独分支；总开关位于动力与电子支路分叉之前。此处检查只针对图片表达，不是硬件通电或性能验收。

“Confirmé”对应用户对总开关用途的确认，不表示已实测其切断能力。图中虚线和“à vérifier / à valider / à définir”标注的电源、接口及控制实现仍待落实。

## 图中补全的关系

1. PC与Raspberry Pi 4通过网络交换目的地和车辆状态；树莓派承担地图、定位、规划、路径跟随与避障。
2. RPLIDAR A2M8通过匹配的USB适配器与树莓派连接。适配器连接、供电及USB负载需核验。
3. 树莓派与NUCLEO-F103RB之间为双向通信方案。下行是目标速度、目标转角和运行/停车指令；上行是测速、IMU、红外距离及状态。具体UART物理连接、引脚、参数和消息格式尚未确定。
4. STM32内提出控制权选择、停车条件判断、测速、速度PID与转向控制功能。停机条件优先于手动和自动命令；这表示待实现的逻辑，不表示固件已具备这些功能。
5. CARSON遥控器经过接收机，将手动指令交给STM32进行选择。接收机信号采集及手动/自动切换尚待设计和验证。本方案依赖STM32正常工作，不是STM32故障时仍可独立工作的硬件接管。
6. STM32输出RC控制脉冲到TBLE-04S电调，电调输出驱动功率到电机；STM32另一路控制转向舵机。两种输出不得混为一条电路。现车电机类型未确认，因此图中使用“驱动电机”名称。
7. 驱动电机经TT-02机械传动带动开孔齿轮，由单只OPB815WZ检测。LED端需要限流，光敏三极管输出需要适配后进入STM32定时器；图中接口方框不是具体电阻接线图。
8. 单叉反馈提供速度大小；方向按照经过验证的控制状态推定。开孔齿轮到车速的换算仍需实际孔结构、计数方式、传动关系及轮胎有效周长。
9. SEN0253通过I²C接入STM32；两个GP2Y0A21YK0F的模拟输出通过经核对的输入适配接入ADC。供电、信号电平、引脚和保护方式仍需落实。

## 供电图的解释

- 7.2V是NiMH电池的标称电压，不是各状态下固定不变的实测电压。
- 电池经过总开关后分为电调动力支路和电子系统供电支路；电调主输入不由5V降压输出供电。
- “Distribution + régulation”表示分配与稳压功能；已确认的模块是LM2596S，不据此认定已拥有独立PDB板，也不据模块名称判定整车带载能力。
- 树莓派、NUCLEO、传感器与接口电路按各自要求设计供电；总负载能力、实际压降和温升尚未验证。Pi4的5.1V/3A是官方供电参考，不是整车全部电子负载的已验证预算。
- TBLE-04S的BEC输出6V/1.5A是厂商规格。向接收机/舵机供电的路径在图中标注适配和负载待核验，不代表现车舵机与接收机已通过配套检查。
- BEC正输出不能与另一稳压器正输出直接并联，也不能接入树莓派供电。公共地用于有线信号参考，不等同于将各正电源相连。
- NUCLEO具体电源输入与跳线由实际使用接口和板卡手册确定；若使用USB调试/通信，还需明确与外部供电的选择关系。

## 下一次接线设计需要填入的实测或已核实信息

每条接口记录源端、目的端、信号类型、工作电平、实际插头和引脚、供电来源及地线关系；UART还需记录实际参数与双方约定，模拟输入需核对量程，RC控制需核对时序与端点。没有来源的具体数值继续留空。

## 原始材料与生成方式

- 用户提供的原始图文件名：`0874c16f93c3d3743d81840d84a89624.jpg`；原始本机路径保留在本地备份中。
- 原图已另行原样归档：[原始架构图](sources/architecture/ARCHITECTURE_ORIGINAL_2026-09-08.jpg)。
- 已有硬件：[盘点文件](EXISTING_HARDWARE_INVENTORY_ZH.md)。
- 使用内置image_gen工具，根据原图进行补全和重新排版。
- 完整生成提示词：[提示词](TAXI_TT02_ARCHITECTURE_COMPLETED_PROMPT.txt)。
- 连线校正提示词：[校正提示词](TAXI_TT02_ARCHITECTURE_CORRECTION_PROMPT.txt)。
- 最终旧线清理提示词：[清理提示词](TAXI_TT02_ARCHITECTURE_FINAL_CLEANUP_PROMPT.txt)。
- IMU连线恢复提示词：[I²C连线提示词](TAXI_TT02_ARCHITECTURE_IMU_LINK_PROMPT.txt)。

## 参数来源

- [Raspberry Pi官方供电说明](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply)。
- [TAMIYA TBLE-04S官方说明书](https://cdn.simba-dickie-group.de/downloads/300045069/300045069_TBLE-04S.pdf)。
- [OPTEK OPB815官方数据手册](https://www.ttelectronics.com/TTElectronics/media/ProductFiles/Datasheet/OPB815.pdf)。
- [NUCLEO MB1136官方手册](https://www.st.com/resource/en/user_manual/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf)。
