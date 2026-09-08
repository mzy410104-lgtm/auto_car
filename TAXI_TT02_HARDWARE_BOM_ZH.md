# Taxi autonome：TT-02 硬件清单与已有实物更新

## 当前采购依据：先复用已有车

2026-09-08，用户累计提供十三张照片：前十一张展示已有硬件及标签，第十二张展示包装底盘示意，第十三张展示CARSON REFLEX WHEEL PRO 3手持遥控器。当前以[已有硬件盘点](EXISTING_HARDWARE_INVENTORY_ZH.md)作为补购依据。

**2026-09-08采购决定：用户明确暂不购买双目摄像头。**当前采用二维雷达导航路线；双目摄像头不列入本轮待购项。已确定需要准备的仍为1只OPB815WZ、1件开孔传动齿轮、1件配套齿轮罩，以及按现有材料补齐的接口电路和固定件。用户已确认有可启动SD卡、数据线够用及手持遥控器，这三项登记为已有，不再询问是否存在或默认补购。供电及配电保护配件继续盘点；通信、停车和人工接管仍需测试，不把尚未核实等同于缺少。

当前可行性判断：已有硬件可作为室内低速二维导航原型的开发基础，主要计算、感知和执行部件已覆盖；尚无整车测试证明全部目标均能达成或无需补件。用户已确认现车缺少测速组件，需要自行购买。当前优先完成测速组件选型与机械适配，并核验运动反馈、带载5V供电、低速/转弯表现与避障停车能力；其他尚未核实的物品不直接记为缺件。现有电机和舵机型号未知不构成默认换购理由，充电器型号不再确认。详细判断见已有硬件盘点中的“项目支撑能力评估”。

2026-09-08官网核查补充：[田宫TT-02通用装配说明](https://www.tamiya.com/cms/english/rc/rcmanual/tt02.pdf)的传动装配、电子设备接线及第22–23页零件表没有车速编码器配置，标准TT-02不标配该传感器。随后用户明确确认现车也没有该组件，登记为缺少、待购；尚未采购或安装。不将通用说明书中的电机和齿比套用为实车参数。

| 项目 | 当前状态 | 采购处理 |
|---|---|---|
| 底盘、四轮及打孔安装平台 | 照片确认已有；TT-02来自用户此前陈述，58631料号未确认 | 先检查复用，取消默认整套新购 |
| RPLIDAR A2M8激光雷达 | 已有1台，图11底部标签确认A2M8；USB适配器、实际供电及工作状态未核实 | 采用现有A2M8，取消默认另购A1M8；先核对适配器并测试扫描数据 |
| DFRobot SEN0253 Gravity姿态与气压传感器板 | 已有1块，型号由用户确认；原厂对应BNO055＋BMP280，3.3–5V供电，Gravity-I2C接口；工作与校准状态未测试 | 优先复用SEN0253，取消默认另购BNO085；采集设计按BNO055与BMP280进行 |
| LM2596S可调降压电源模块 | 已有1块；用户提供名称“Arduino LM2596S”，型号按用户确认登记；整板厂家、实际输入/输出电压、持续电流及所接负载未核实 | 保留已有模块，先核对供电并测试；尚不能确定它能否稳定为Pi4及外设供电，也未确定需要新增移动电源 |
| SHARP GP2Y0A21YK0F红外测距传感器 | 已有2个，数量由用户确认；图10标记与原厂说明确认型号；10–80cm、4.5–5.5V供电、模拟电压输出；各自安装位置未核实 | 先复用这2个并测试，按覆盖范围决定补购；小于10cm不在规定测距范围内，不按数量直接替代原表VL53L1X |
| CARSON遥控接收机 | 已有1台，正面可识别Reflex Wheel PRO3系列及CH1至CH4；完整货号未核实；用户已确认另有手持遥控器，配对状态未测试 | 复用现有遥控设备，不默认另购FlySky套装；后续验证配对、控制与失联停车 |
| CARSON REFLEX WHEEL PRO 3手持遥控器 | 已有1台，用户确认且图13可读品牌和系列；与现有接收机的配对、人工接管及失联停车尚未测试 | 从存在性待确认项移除，不重复购买遥控器；按现有设备设计并验证控制链路 |
| TAMIYA TBLE-04S电调 | 已有1块，型号由用户读取标签并确认；当前电机模式和运行状态未测试 | 优先复用TBLE-04S，取消默认另购WP-1060；核对电机、电池与舵机配套 |
| 转向机构和驱动电机 | 已见相应实物或局部；用户明确说明两者型号当前均无法确认，记为未知；电机类型及功能状态未验证 | 移除型号补充要求，不再索要标签；保留已有件，不因型号未知默认购买S-U300或替换电机；不能仅由TBLE-04S名称推定现车电机为无刷 |
| PTH08 NiMH镍氢动力电池，标称7.2V | 已有1包；品牌PTH08、类型和标称电压均按用户说明登记；容量及单位、具体型号由用户说明当前无法确认，记为未知；健康状态未测试 | 暂不重复索要未知参数，不因信息缺失直接另购；后续依据电池状态证据评估复用，续航估算暂留空；按用户要求不再确认充电器型号 |
| Raspberry Pi 4 Model B | 已有1块，丝印确认；实际内存容量未核实；SD卡可启动由用户确认，整车软件运行状态未测试 | 取消默认购买KIT-PI4-4，先使用现有Pi4 |
| 系统SD卡 | 用户确认已有可启动SD卡；容量、系统版本未登记，未由助手独立观察启动 | 从存在性待确认项移除，复用现有SD卡，不默认另购 |
| 数据线 | 用户确认现有数据线够用；实际连接与通信尚未测试 | 从存在性待确认项移除，不默认补购数据线；不据此推定雷达USB转换板已存在或通信已通过 |
| 树莓派底壳和散热片 | 已见红色底壳及4块散热片，外壳型号未确认 | 先检查现有配套，风扇型号须与现有外壳匹配 |
| NUCLEO-F103RB | 已有1块，标签确认；PCB为MB1136 rev C；带板载ST-LINK区域 | 取消默认购买NUCLEO-F446RE及独立ST-LINK，底层控制按现有F103RB设计 |
| 双目摄像头 | 用户明确决定现阶段不购买 | 从本轮待购范围排除；后续依据正式任务和实际障碍覆盖再评估 |
| 单通道测速组件 | 用户明确选择CoVAPSy官方开孔传动齿轮方法，光电叉为OPTEK OPB815WZ共1只 | 准备开孔齿轮、专用罩、1只光电叉及接口/固定件；取消直接读轴孔、双叉与Seeed方案。方向仍属推定，安装与功能未验证 |
| 电源配件及保护装置 | 本轮照片尚未提供完整证据 | 记为尚未核实，不直接记为缺件；不再将已确认的SD卡、数据线和手持遥控器纳入此项 |
| 电池充电器 | 尚无实物与规格证据；用户明确说明型号不需要确认 | 从待确认型号项移除，不再索要；不据此认定缺件、确定补购或确认配套已验证 |

包装图中的电调标记为TEU-105BK，电机标注为540类型；电调、舵机和电池均标注NOT INCLUDED。上述信息仅描述包装示意，不代表现车配置。现车电调已由用户另行确认为TBLE-04S，电池品牌PTH08、类型NiMH、标称7.2V按用户说明登记。电机、舵机型号，以及电池具体型号、容量及单位均由用户说明当前无法确认，保留未知并移除补充要求；不从照片中的3000推定容量或充电参数，也不因型号未知直接换购电机、舵机。

电源板用户原称“Arduino LM2596S”，不据此认定Arduino为整板厂家，也不补全芯片后缀。[TI原厂资料](https://www.ti.com/product/LM2596)中的降压功能和3A参数属于LM2596芯片系列，不能直接当作这块整板的持续输出能力。现有模块的电压设定、负载下电压、纹波及温升尚未测试，整车5V供电方案暂未定型。

现有TBLE-04S按[田宫官方产品资料](https://www.tamiya.de/tamiya_en/spare-parts-accessories/rc-electronics/tamiya-esc-tble-04s-300045069-en.html)及[官方说明书](https://cdn.simba-dickie-group.de/downloads/300045069/300045069_TBLE-04S.pdf)核对：厂商标称最大连续电流75A、输入电源规格6.6–7.2V、BEC输出6V/1.5A。支持原厂指定的有刷及有传感器无刷电机；现车电机、电池、舵机的配套和电调当前设置尚未验证。BEC的6V输出不直接用作树莓派5V电源。

上述ITEM 45069英文说明书对数字舵机或电流超过1.5A的舵机提出可能损坏电调的警告。现车舵机型号未确认；不得把此前S-U300方案直接套用为TBLE-04S的BEC供电方案。后续依据实际舵机与厂家要求核对或重新设计供电。

当前控制组合采用已有的**Raspberry Pi 4 Model B＋NUCLEO-F103RB**开展设计：树莓派承担地图与导航计算，F103RB承担执行控制和传感器采集。Pi4实际内存容量、F103RB最终接口分配及整车运行负载尚需核对。

姿态测量采用已有的**DFRobot SEN0253**。[原厂产品页](https://www.dfrobot.com/product-1793.html)确认其集成BNO055九轴姿态传感器与BMP280气压/温度传感器，模块供电3.3–5V、接口Gravity-I2C。规划由F103RB采集角速度和姿态数据，再发送给树莓派；接线、固定安装、校准及数据质量仍需验证。下方历史方案中的BNO085不再作为默认新购项。

雷达按已有**RPLIDAR A2M8**配置。[SLAMTEC官方规格](https://www.slamtec.com/en/lidar/a2spec)列出360°扫描、0.2–12m测距、8kHz采样、5V供电与UART 115200bps；这些是厂商规格，不是本机实测。规划经匹配的USB适配器连接树莓派，适配器和电源仍需核对。

SHARP型号及参数已核对[原厂GP2Y0A21YK0F数据手册](https://global.sharp/products/device/lineup/data/pdf/datasheet/gp2y0a21yk_e.pdf)。规划由F103RB的ADC采集其模拟输出；具体接线、输入保护、距离标定及停车距离仍需设计和实测。照片未证明传感器已正常工作，也未证明车端所有光学模块均为该型号。

### 当前已确认待购：测速组件

**2026-09-08用户确定方案：采用CoVAPSy官方开孔传动齿轮方法。**按[官方机械说明](https://ajuton-ens.github.io/CourseVoituresAutonomesSaclay/voiture_type/)，使用开孔传动齿轮兼作码盘，光电叉固定在配套替换齿轮罩上。开孔齿轮和专用罩恢复为需要准备的机械件，取消直接读取轴本体孔及其尺寸测量待办。该选择仅针对测速安装，不把田宫底盘描述为原厂已预留测速接口，也不因此更换已有Pi4或NUCLEO-F103RB。

官方机械原始文件和两份装配PDF已归档至[来源与文件索引](sources/CoVAPSy_encoder_official/SOURCE_INDEX.md)。STP和DXF已核对下载完整性，文件保持原样；尚未完成CAD尺寸、公差、材料或制造工艺核验。所查机械目录没有STL文件，不能将已下载STP写成已完成打印准备。

用户进一步说明Seeed光电叉太短、不能直接配合开孔测速齿轮，明确选择**OPTEK OPB815WZ**，并报告“经过验证只能安装一个”。据此将配置确定为**1只OPB815WZ**，取消双叉改装及其空间核对待办。空间容量依据用户验证记录；购买、接线与测速功能尚未确认。

用户已确认轴本体的孔横向贯穿且内部为空，保留为实物记录；当前选定的官方方案读取齿轮上的孔，不使用该轴孔，也不再要求测量该孔尺寸。该观察不证明现车已有官方开孔齿轮，孔的原有用途不作推断。

| 项目 | 官方资料对应部件 | 当前采购边界 |
|---|---|---|
| 开孔测速齿轮 | 官方套件`Photos_kit_CoVAPSy_2024.pdf`第2页23号；机械文件`Pignon intermediaire 70dts.dxf` | **需准备1件**：取得官方配套件或按核对后的官方图纸加工；单独供货和报价尚未确认，不以文件名替代加工尺寸核验 |
| 光电叉安装齿轮罩 | 官方套件同页24号；机械文件`Carter pignon support fourche.stp` | **需准备1件**：取得官方配套罩或交由加工/打印服务按官方模型制作；核对现车固定位置和平台间隙，报价未确认 |
| 光电叉 | **OPTEK OPB815WZ**，与CoVAPSy清单对应 | **1只**，用户已验证空间限制；用于测速度大小，方向结合控制状态推定；不再安排双叉改装 |
| 固定件 | 官方安装手册第5页，光电叉固定使用2枚MB1或MA2自攻螺钉 | 按配套罩和手册核对现有螺钉；不能推定用户手头已有足量配件，不自行指定未核实螺纹规格 |
| 电路与线缆 | OPB815WZ至现有NUCLEO-F103RB的LED限流、接收端上拉/负载电路及连接设计 | 需准备相应电阻和连接材料；阻值按供电与工作条件确定。滤波/整形按波形测试决定，已有材料先复用；不是Grove模块接法，引脚与报价未确定 |

**法国购买渠道，2026-09-08查询：**购买型号为`OPB815WZ`，数量1；不要用`OPB815L`或其他后缀代替。以下是光电叉器件价格，不包含CoVAPSy开孔齿轮、专用罩和接口电路。本次仅查询，未登录、加购或下单。

| 渠道 | 准确订货信息 | 价格与库存证据 |
|---|---|---|
| [RS France专业站](https://fr.rs-online.com/web/p/capteurs-optiques-a-fourche/1944030) | 制造商型号`OPB815WZ`；RS订货号`194-4030`；按1只销售 | 直接读取页面显示5.35欧元HT、**6.42欧元TTC/只**，不含配送/处理费；显示有库存。数量与交期会变化，最终以结账确认 |
| [Farnell France](https://fr.farnell.com/tt-electronics-optek-technology/opb815wz/optocommutateur-faisceau-trav/dp/1497919) | 制造商型号`OPB815WZ`；订货号`1497919`；官网检索内容显示最小1、倍数1 | 官网检索快照显示**4.540欧元HT/只**，未显示TTC；直接打开超时/拒绝访问，不能登记为实时价格或实时库存确认 |

个人自行购买可使用[RS Particuliers](https://www.rs-particuliers.com/)，在搜索栏输入准确型号`OPB815WZ`并核对商品制造商型号与数量。RS官网将专业与个人入口分开；本次已打开个人站首页，未取得该器件的个人站商品页价格/库存，不能直接套用专业站的报价。[RS个人销售条款](https://fr.rs-online.com/web/content/a-propos-rs/sommaire/conditions-generales-vente-particuliers?intcmp=FR-ARS-NAV2-_-Jan23)列明订单不超过60欧元TTC时处理及配送费10.20欧元TTC，最终按结账页面核对。

若由学校通过专业账户采购，RS[配送帮助](https://fr.rs-online.com/web/content/accueil/aide/options-livraison?intcmp=FR-WEB-_-CP-C3-MCC-0901-Livraison)列网上订单低于50欧元HT收9.50欧元HT处理费。Farnell[配送帮助](https://fr.farnell.com/help/delivery-information)列标准配送订单低于75欧元HT收11.99欧元HT处理费；检索到的商品快照另显示50欧元免标准配送门槛，两处说明不一致，因此不承诺Farnell单只订单的最终费用。学校已有账户的合同价格、优惠和配送资格未核查，适合在结账时比较总额。完整测速组件及整车补购预算仍未确定。

原始来源：[安装手册第5页](https://github.com/ajuton-ens/CourseVoituresAutonomesSaclay/blob/main/Hardware/Guide_Assemblage_kit_CoVAPSy.pdf)、[套件照片第2页](https://github.com/ajuton-ens/CourseVoituresAutonomesSaclay/blob/main/Hardware/Photos_kit_CoVAPSy_2024.pdf)、[机械文件目录](https://github.com/ajuton-ens/CourseVoituresAutonomesSaclay/tree/main/Hardware/pieces_mecaniques_stp_dxf)。已查看两份PDF的对应装配图，尚未完成现车机械试装或电气测试。

**型号和数量已确定，功能仍需验证。**[OPB815原厂手册](https://www.ttelectronics.com/TTElectronics/media/ProductFiles/Datasheet/OPB815.pdf)列出单个红外LED与NPN光敏三极管。采用1只时，速度大小来自脉冲测量，正负号来自运动控制状态推定；控制指令方向不等于实测方向。后续车速换算使用被测齿轮到车轮的实际转动关系，传动比与有效每转计数仍需核实。

建议使用先停车、后换向的控制流程；收到倒车命令不立即把测量速度改为负值。刹车、中位、启动及换向过渡中的方向标记为尚未确定，保留原始脉冲，不能把未知方向当作可信零速。停车观察时间、最低可分辨速度及TBLE-04S换向行为需要实车标定，不指定未经验证的阈值或延时。单叉不能识别与控制状态不一致的惯行或外力推动，不能单凭此方案宣布已满足独立后退检测或导航验收。此前基于[TI两相原理](https://www.ti.com/document-viewer/lit/html/SBOA200)提出的双叉安装方案已按用户验证结果撤销；相关原理不再构成当前硬件待办。完整状态处理建议见已有硬件盘点。

此前推荐的**Seeed Grove Optical Rotary Encoder 101020587 / TCUT1600X01**仅保留为双通道电子模块资料，**取消当前默认下单建议**。其3mm光电槽和板卡安装结构没有被证明兼容CoVAPSy齿轮罩；若使用，需要重新设计机械适配。[Seeed硬件说明](https://wiki.seeedstudio.com/Grove-Optical_Rotary_Encoder-TCUT1600X01/)与[完整原理图](https://files.seeedstudio.com/wiki/Grove-Optical_Rotary_Encoder-TCUT1600X01/res/Grove-Optical_Rotary_Encoder-TCUT1600X01.zip)的3.3V供电/Grove输出核查结论只适用于该模块，不适用于OPB815WZ。此前GoTronic标价12.20欧元TTC只是该Seeed模块价格，不是新机械方案报价。

中央轴54501长度140mm、直径5.5mm的官网资料保留在[已有硬件盘点](EXISTING_HARDWARE_INVENTORY_ZH.md)，不作为现车尺寸或当前齿轮方案的选购尺寸。下一步按官方齿轮与罩的文件核对现车安装关系，准备机械件及1只OPB815WZ，随后完成F103RB接口设计与脉冲/低速测试。实际每转计数、传动比及电调换向行为仍需验证；不因采用官方机械结构就宣布测速或导航已通过。本助手未执行购买、钻孔、加工或安装，完整测速组件及整车补购总额仍未确定。

下文保留此前的新购方案与来源，供识别确切缺项后参考。其型号表、连接图和779.33欧元小计均不代表现有车辆实物配置或当前补购预算。历史方案中对电机铭牌的补充要求不再适用于当前盘点；当前以用户已说明的型号未知状态为准。

---

核查日期：2026-09-08。适用项目：三人、约十二周、每人每周十小时，在法国采购；室内无地面标线，依据地图定位、选择目的地、规划路径、跟随路径并避障。

以下为提供实物照片前整理的新购配置参考。已核对所列商品型号、公开规格和来源；没有进行实车安装、负载、续航或导航验收。场地尺寸和课程正式任务书尚未确定。

## 1. 主要硬件

表中价格为本次法国销售页面公开价格，单位为欧元；未计运费、促销码或数量折扣。空缺表示未核实价格，不是零成本。型号中的商家编号和制造商编号按来源分别保留。

| 部件 | 确定型号 | 数量 | 已核单价 € | 用途与配套说明 | 来源 |
|---|---|---:|---:|---|---|
| 底盘套件 | **Tamiya 58631 / TT-02** | 1 | 119.80 | 含底盘、车轮、传动、转向机构、车壳和原配电机；需自行组装。 | [产品页](https://www.jjmstore.fr/tamiya-subaru-impreza-tt02-voiture-rc-kit-58631.html) |
| 推进电机 | **58631 套件内 Type 540 Motor** | 1 | 套件内 | 随套件；官方未公布独立电机料号，不把它写成其他具体电机型号。 | [产品页](https://www.tamiya.com/english/products/58631/index.html) |
| 有刷电调 ESC | **Hobbywing QuicRun WP-1060，Tamiya 插头版；Tecnimodel VAHW30120201** | 1 | 37.95 | 本版指定独立电调；套装商家附送的电调不作为本方案主电调。 | [产品页](https://www.tecnimodel.com/variateurscontroleurs/10032-variateur-hobbywing-1060-quicrun-compatible-lipo-2s-et-3s-avec-prise-tamiya.html) |
| 转向舵机 | **Futaba S-U300 / 01006009** | 1 | 16.95 | 标准舵机；4.8–6V，25T 花键；按 TT-02 说明书使用 Futaba 对应舵盘零件。 | [产品页](https://www.tecnimodel.com/servos-futaba/15745-servo-futaba-s-u300-numerique-41kg6v.html) |
| 动力电池 | **Carson 500608224，7.2V 3000mAh NiMH，Tamiya 插头** | 2 | 28.49 | 一次装一块；另一块作为周转备用。 | [产品页](https://www.carson-modelsport.com/carson_fr/categories/batteries-et-piles-rc/batterie-nimh/72v3000mah-nimh-race-batterie-tam-500608224-fr.html) |
| 动力电池充电器 | **Carson 500606099 Expert Charger NiMH 2A** | 1 | 22.99 | 4–8 节 NiMH、2A、110–240VAC 输入、Tamiya 接口。 | [产品页](https://www.carson-modelsport.com/carson_fr/pieces-detachees-accessoires/accessoires-rc/chargeurs/expert-charger-nimh-2a-500606099-fr.html) |
| 车载计算机套件 | **Raspberry Pi 4 Model B 4GB；GoTronic KIT-PI4-4 / 38684** | 1 | 159.50 | 包含官方外壳、32GB microSD、5V/3A 桌面电源、散热片、HDMI→micro-HDMI 线。 | [产品页](https://www.gotronic.fr/art-kit-raspberry-pi-4-b-kit-pi4-4-38590.htm) |
| 主动散热 | **Raspberry Pi 4 Case Fan SC0448** | 1 | 6.50 | 匹配官方 Pi 4 外壳；附带 CPU 散热片，不与套件 CPU 散热片叠贴。 | [产品页](https://www.gotronic.fr/art-module-ventilateur-sc0448-32950.htm) |
| 计算系统移动电源 | **Anker Nano PowerBank A1259，10000mAh，内置 USB-C 线** | 1 | 49.99 | USB-C 输出支持 5V/3A；不按商品名 30W 推定 5V 下输出 6A。 | [产品页](https://www.anker.com/fr/products/a1259-built-in-cable-powerbank-10000mah?Sort_by=Recommand%C3%A9&collections_batterie-externe-steam-deck=&variant=48187868152124) |
| 底层控制板 | **STMicroelectronics NUCLEO-F446RE** | 1 | 19.02 | 板载 ST-LINK/V2-1；负责电机/舵机控制、编码器和近距传感器采集、通信超时停车。 | [产品页](https://fr.rs-online.com/web/p/outils-de-developpement-pour-microcontroleurs/9064624) |
| 二维激光雷达 | **SLAMTEC RPLIDAR A1M8；GoTronic 36236** | 1 | 119.80 | 用于建图、定位和水平扫描；所列商品包含 USB-UART 适配器，不含 USB 数据线。 | [产品页](https://www.gotronic.fr/art-capteur-de-distance-rplidar-a1m8-29031.htm) |
| 惯性测量模块 | **Adafruit BNO085，Product ID 4754** | 1 | 29.90 | 本方案通过 SPI 接 STM32；安装后要检查电机附近的磁场干扰。 | [产品页](https://www.gotronic.fr/art-module-9-dof-bno085-ada4754-33477.htm) |
| 低位近距传感器 | **Pololu VL53L1X，Product #3415** | 4 | 23.95 | 建议前部低位两个、后部低位两个；实际角度与检测覆盖需用车辆验证。 | [产品页](https://www.gotronic.fr/art-capteur-de-distance-vl53l1x-3415-28058.htm) |
| I²C 多路复用器 | **Adafruit TCA9548A，Product ID 2717** | 1 | 9.20 | 四个同型号 ToF 分别接独立通道；BNO085 不接在其后面。 | [产品页](https://www.gotronic.fr/art-module-multiplexeur-i2c-ada2717-26051.htm) |
| 速度和方向编码器 | **Seeed Grove Optical Rotary Encoder 101020587 / TCUT1600X01** | 1 | 12.20 | 双路光电检测；含 Grove 线，不含码盘；必须制作 TT-02 安装件。 | [产品页](https://www.gotronic.fr/art-module-encodeur-optique-grove-101020587-28244.htm) |
| STM32 USB 数据线 | **StarTech.com USB2HABM50CM** | 1 | 4.90 | USB-A → Mini-B，0.5m；连接 NUCLEO 的 ST-LINK USB。 | [产品页](https://www.ldlc.com/fiche/PB00265154.html) |
| 雷达 USB 数据线 | **StarTech.com UUSBHAUB50CM** | 1 | 10.90 | USB-A → Micro-B，0.5m；连接雷达随附适配器。 | [产品页](https://www.materiel.net/produit/201702280552.html) |
| 机械动力总开关 | **DAIER R13-401-101；SVB/SEATEC 29847** | 1 | 6.95 | 直接串联在动力供电线上；12VDC/50A 额定，两端子，12mm 安装孔。 | [产品页](https://www.svb-marine.fr/fr/seatec-interrupteur-a-bascule-en-metal-12-v-50-a.html) |
| PWM 电平缓冲芯片 | **Texas Instruments SN74AHCT125N，PDIP-14** | 1 | 未核价 | 5V 供电，将 STM32 两路 3.3V PWM 转为 5V；需焊接、去耦和确定使能状态。 | [产品页](https://www.digikey.fr/en/products/detail/texas-instruments/SN74AHCT125N/375798) |

上述有价格项目小计 **779.33 €**。包含两块动力电池，但车上一次只安装一块；不包含未核价的缓冲芯片，也不包含下表其余器件、加工和运费，因此不是整车项目总预算。

## 2. 接管、保护与装配配套

我建议将下面这组也纳入完整采购清单。遥控器负责手动驾驶与接管；目的地仍在已有电脑上的导航界面选择。

| 部件 | 确定型号／规格 | 数量 | 配套说明 | 来源 |
|---|---|---|---|---|
| 遥控器＋接收机 | **FlySky FS-GT5＋FS-BS6，套装** | 1套 | 用于手动建图/调试及人工接管；接收机不要另重复购买。法国结算价未核实。 | [产品页](https://www.hf-modellsport.de/en/fs-gt5-6-channel-radio-set-with-1-receiver.html) |
| 人工/自动控制切换板 | **Pololu 4-Channel RC Servo Multiplexer (Assembled) #2806** | 1 | 页面25.45 € TTC；外部仓供货。将遥控器和STM32两套PWM切换到舵机/ESC。 | [产品页](https://opencircuit.fr/produit/pololu-4-channel-rc-servo-multiplexer) |
| 接收机至切换板连接线 | **Pololu #780，Servo Extension Cable 12″ Female–Female** | 3条 | 30cm，22AWG，母–母；页面5.90 €/条 TTC，三条17.70 €。 | [产品页](https://opencircuit.fr/produit/servo-extension-cable-12-inch-female-female) |
| 遥控器电池 | **Duracell Plus AA / LR6，1.5V 碱性电池** | 4节 | 按FS-GT5使用4节AA电池选定；不额外引入遥控器锂电充电系统。 | [产品页](https://www.duracell.fr/) |
| 动力保险座 | **Littelfuse FHAC0002LXN** | 使用1只 | ATO片式保险座，30A/32VDC，12AWG引线；所查RS页面5只装37.465 € TTC，不能按单只价当成实际采购总额。 | [产品页](https://fr.rs-online.com/web/p/porte-fusibles/3375234) |
| 保险丝备料包 | **Littelfuse 00940202ZP，ATO Fuse Assortment 6pc** | 1包 | 含5/10/15/20/25/30A各一只；具体装车额定值须按电机实测电流和线束保护要求确定，不能直接选30A。法国库存及价格未核实。 | [产品页](https://www.digikey.com/en/products/detail/littelfuse-inc/00940202ZP/3425348) |
| 焊接连接板 | **Adafruit Perma-Proto Half-sized Breadboard PCB，Product ID 1609** | 1 | 用于低电流信号、缓冲IC和传感器连接；动力电机电流不经过这块板。法国价格未核实。 | [产品页](https://www.adafruit.com/product/1609) |

## 3. 不能省略的通用材料与定制件

这些项目没有适用于所有TT-02改装车的统一成品型号。应按实物布局出加工图和线束表，不能虚构一个“TT-02导航支架套件”料号。

| 项目 | 需要完成的内容 |
|---|---|
| 电子设备安装平台 | 上层板、与底盘连接的支撑件；固定Pi外壳、NUCLEO、雷达和移动电源。板外形、孔位、材料厚度由实物测量确定；采用平板加工方式，不依赖3D打印。 |
| 雷达安装件 | 保持扫描平面稳定，安排车体和其他设备的位置以减少遮挡；高度以实际障碍和安装布局确定。 |
| 编码器码盘、轴夹和传感器支架 | 针对实际传动位置制作；码盘图案需满足双通道相位检测，检查机械间隙、每转计数和传动比。该Seeed模块不是TT-02直装编码器。 |
| 四个ToF的支架 | 支持前后低位布置及角度调整；检测不到的侧向区域不能当成已覆盖。 |
| 动力线束 | 电池正极经过保险和机械开关再到ESC；配置适配实际大Tamiya电池接口的线束、端子、绝缘和固定。现有证据没有确定整套线规、端子电流和最终长度。 |
| 电机接线 | WP-1060购买版本的电机端为4.0mm母香蕉插头；原配电机接头须按实物确认，再确定是否需要端子或转接线。 |
| 低电流线束 | STM32至IMU、ToF复用板、编码器及PWM缓冲；2.54mm排针/排母、传感器线和用于固定的连接件。实际线序须从板卡文档与最终引脚表获取。 |
| 缓冲电路小料 | PDIP-14插座、100nF去耦电容、输入/使能所需电阻与连接线；使能及未用输入状态必须在接线图中确定。不得让裸IC输入悬空。 |
| 紧固与绝缘耗材 | 螺钉、螺母、垫片、支撑柱、热缩管、扎带、线夹、软泡棉和电池固定带；长度和数量随加工图确定。 |
| 测试支撑与场地材料 | 让车轮离地的稳定调试支撑、软质测试障碍和现场测距标记。路线在软件中规划，不需要购买循黑线传感器或在地面铺导航线。 |

## 4. 连接关系

以下只说明模块关系，不是可以直接照接的引脚图。

```text
已有电脑（目的地选择、显示地图）
             │ 网络
Anker A1259 → Raspberry Pi 4B
                    ├─ USB → RPLIDAR A1M8 随附适配器 → 雷达
                    └─ USB → NUCLEO-F446RE
                                  ├─ SPI → BNO085
                                  ├─ I²C → TCA9548A → 四个VL53L1X
                                  ├─ 双路计数输入 ← 光学编码器
                                  └─ 两路PWM → SN74AHCT125N → Pololu #2806
                                                               ↓
FS-GT5 → FS-BS6 → 手动PWM及模式选择 ────────────────────────→ #2806
                                                               ├─ S-U300转向舵机
                                                               └─ WP-1060控制输入

Carson 7.2V NiMH → 保险 → 机械动力总开关 → WP-1060 → 原配电机
                                             └─ BEC → 舵机、接收机及#2806的VM电源
```

- NUCLEO通过板载ST-LINK的USB接口供电、调试和虚拟串口通信；不另购ST-LINK或USB-UART。具体串口与跳线以[ST官方UM1724](https://www.st.com/resource/en/user_manual/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf)为准，不能照搬旧CoVAPSy引脚表。
- #2806的主输入接接收机，副输入接经缓冲的STM32信号。其VM和VS电源域分开，所有地相连；STM32侧只接信号与公共地，VS不接。5V计算电源正极不与6V BEC正极相连。[Pololu官方手册](https://www.pololu.com/docs/0J60/all)
- SN74AHCT125N使用5V电源，TI规定其高电平输入门限最低2.0V，因此可接受STM32的3.3V PWM。最终接线仍须检查上电默认状态、使能状态及任一电源关断时的反灌情况。[TI数据手册](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf)
- 机械总开关切开动力电池线路，不依赖上层软件。撤去动力不等于车辆立即停稳，遥控接管也不等于已经完成停止距离验收。

## 5. 选型的依据与实际限制

### 底盘与动力

标准TT-02是轴传动四驱、前轮舵机转向的平台。它不能像差速机器人那样原地旋转；需要在场地上量测可用转角和最小转弯空间。[Tamiya 58631官方页](https://www.tamiya.com/english/products/58631/index.html)

此前新购方案核查时，58631官方只说明包含Type540电机，未提供其独立料号或绕组数。JJM商品页写明附送TBLE-02s，官方基本套装说明则将ESC列为另售，因此当时的新购参考指定WP-1060。该段保留当时选型依据；当前车辆已由用户确认使用TBLE-04S，现行采购处理以上方已有实物更新为准。

WP-1060当前官方规格为6–9节NiMH、6V/3A BEC；6节NiMH条件下还规定电机应满足至少12T或7.2V下低于30000rpm。原配电机标识需要据此核对。其倒车模式有不同控制过程，不能把上层负速度直接等同于立即倒车。[Hobbywing官方产品页](https://www.hobbywing.com/en/products/quicrun-wp-1060-brushed55)、[官方说明书](https://www.hobbywing.com/en/uploads/file/20240315/4806bbdbab8eb9fea0bb26da87d81b00.pdf)

Hobbywing全球产品页编号为30120200，本次法国购买页为VAHW30120201；两者保留原样，不自行改写成相同编号。S-U300的供电电压与BEC匹配，但公开资料没有给出其堵转电流，因此还不能声称BEC峰值余量已通过实车验证。[Futaba官方](https://futabausa.com/product/s-u300-standard-servo/)

Littelfuse保险座的30A是上限规格，不是应该安装的保险额定值。保险定值必须兼顾启动电流、正常运行电流、线束与连接器承受能力；不能按电调宣传的60A反推。[Littelfuse官方保险座数据表](https://www.littelfuse.com/assetdocs/littelfuse-fuse-holder-ato-fhac-datasheet?assetguid=272e0b1a-a576-4173-8740-c1eb469efd79)

### 计算供电

本版选择Pi4B 4GB，是为了使用成品5V/3A移动电源并降低车载供电集成工作。实际导航计算负载仍需测试。Pi4所有USB外设合计上限1.2A，需要把雷达启动、NUCLEO及其传感器负载合并核对；整个5V系统也须满足电源限制。[Raspberry Pi官方供电说明](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)

A1259官方尺寸104×52.3×26mm、重量215g；支持5V/3A输出。其低负载关闭行为和实际续航尚未实测，不作为UPS使用。套件的5V/3A桌面电源可分时用于Pi或给A1259充电。[Anker官方规格](https://service.anker.com/product-description/a085g00000GiZgpAAF)

### 感知与反馈

BNO085使用SPI，因为Adafruit明确列出其I²C与部分控制器和复用器的兼容性问题；不能按传感器都带I²C就全部挂到TCA9548A后面。[Adafruit官方说明](https://learn.adafruit.com/adafruit-9-dof-orientation-imu-fusion-breakout-bno085?view=all)

四个VL53L1X补充低位近距离观测，不能替代雷达，也不能保证所有低矮、透明或侧向障碍都会被检测到。检测距离与角度应按实际对象验收。[Pololu #3415官方规格](https://www.pololu.com/product/3415)

光学编码器用于速度和方向反馈，不能用ESC控制脉宽充当实际速度。安装后应校准每转计数、传动比、轮胎有效周长和正反方向。转向指令与实际轮角也应测量标定；本版没有另加转角传感器，不把舵机指令当成已测得的车轮角度。[Seeed官方编码器](https://www.seeedstudio.com/Grove-Optical-Rotary-Encoder-TCUT1600X01.html)

## 6. 已包含物品与可借用设备

Pi套件已经包含32GB microSD、外壳、桌面电源和显示线；RPLIDAR商品包含USB-UART适配器；NUCLEO包含调试器。底盘套件包含四个车轮及传动机构。这些物品无需重复购买。

操作者使用已有电脑。首版不新增摄像头、GPS/UWB、车载触摸屏、差速电机驱动板或3D打印机；当前确认的需求没有要求这些设备。

实验室需要可用的万用表、示波器或逻辑分析仪、限流直流电源、焊接工具及机械测量/加工工具。是否已有设备尚未确认，未将整套实验室仪器强加到车载采购预算。若需另购基础工具，本次核实型号包括[UNI-T UT139C](https://meters.uni-trend.com/product/ut139-series)及[Weller WE1010 230V](https://www.weller-tools.com/sites/default/files/products/documents/WE_TECH-DATA_T0053298392_WE1010BE_EN.pdf)。

## 7. 采购前仍需补齐的记录

1. 现有或到货的58631实物包装清单、电机铭牌、电机端子照片；已买底盘时不要再次购买。
2. 场地平面尺寸、最窄通道、地面类型和要检测的最小障碍，以确认TT-02转弯空间与传感器布置。
3. 设备实际安装尺寸、总重量、编码器机械图和完整线束表。
4. 动力启动/运行电流、转向最大负载和整套USB供电电流，随后确定保险额定值并测试关断、失联、超时和重新启动行为。

这些记录用于把型号清单落实为可接线、可安装和可验收的整车。当前没有把尚未完成的实测写成已通过。
