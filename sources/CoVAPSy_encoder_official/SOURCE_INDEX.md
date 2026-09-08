# CoVAPSy 官方测速机械资料来源

> Git归档说明：本仓库追踪来源索引；下述原厂PDF/CAD副本保留在本地，不随Git发布。其他成员可从表内原始来源获取文件并核对记录。

归档日期：2026-09-08（法国本地时间）。当前方案采用 1 只 OPTEK OPB815WZ，参考官方开孔传动齿轮与光电叉支撑罩。此目录仅保存原始资料，没有修改、格式转换或生成制造图。

## 原始机械文件

目录已通过[官方仓库页面](https://github.com/ajuton-ens/CourseVoituresAutonomesSaclay/tree/main/Hardware/pieces_mecaniques_stp_dxf)及[GitHub 目录 API](https://api.github.com/repos/ajuton-ens/CourseVoituresAutonomesSaclay/contents/Hardware/pieces_mecaniques_stp_dxf)核对；下列下载地址直接取自返回的 `download_url`，文件名保持原样。

| 文件 | 下载日期 | 字节数 | 原始下载地址 |
|---|---|---:|---|
| `Carter pignon support fourche.stp` | 2026-09-08 | 679821 | [官方原始 STP](https://raw.githubusercontent.com/ajuton-ens/CourseVoituresAutonomesSaclay/main/Hardware/pieces_mecaniques_stp_dxf/Carter%20pignon%20support%20fourche.stp) |
| `Pignon intermediaire 70dts.dxf` | 2026-09-08 | 311368 | [官方原始 DXF](https://raw.githubusercontent.com/ajuton-ens/CourseVoituresAutonomesSaclay/main/Hardware/pieces_mecaniques_stp_dxf/Pignon%20intermediaire%2070dts.dxf) |

下载后核对字节数，并按 Git blob 规则计算 SHA-1，与官方 API 值一致：

- `Carter pignon support fourche.stp`：`759dee53fa9a70020e5d86cf4b74f152f3568b81`
- `Pignon intermediaire 70dts.dxf`：`38b8328561d60877b978f7866b233528f22aa755`

## 装配资料副本

以下文件于 2026-09-08 从本项目 `tmp/pdfs/covapsy_encoder_mount/` 复制归档，逐字节确认副本与原文件一致；没有删除原件。本次未重新下载 PDF。

| 文件 | 字节数 | 原始来源 URL | 已查看的相关内容 |
|---|---:|---|---|
| `Guide_Assemblage_kit_CoVAPSy.pdf` | 2956991 | [原始 PDF（固定提交）](https://raw.githubusercontent.com/ajuton-ens/CourseVoituresAutonomesSaclay/079841a5aa8e59d97413295f268a9689767dbdb5/Hardware/Guide_Assemblage_kit_CoVAPSy.pdf) | 第 5 页光电叉固定位置，使用 2 枚 MB1 或 MA2 螺钉；第 6 页连接示意 |
| `Photos_kit_CoVAPSy_2024.pdf` | 5685712 | [原始 PDF（固定提交）](https://raw.githubusercontent.com/ajuton-ens/CourseVoituresAutonomesSaclay/079841a5aa8e59d97413295f268a9689767dbdb5/Hardware/Photos_kit_CoVAPSy_2024.pdf) | 第 2 页 23 号开孔测速齿轮、24 号光电叉安装罩及 15 号光电叉 |

## 核查范围与使用边界

- 官方机械目录本次实际列出 11 个文件，没有子目录，也没有 STL 文件。本次取得支撑罩的 STP 原始 CAD，未取得该目录内配套的 STL。此结论仅限已核查目录，不代表全网不存在该文件。
- 检查了文件存在、来源、大小、Git blob 校验值及格式开头；没有执行 CAD 几何解析、尺寸测量、公差检查、打印切片或制造适配验证。
- 文件名中的 `70dts`、零件名称以及文件格式不能代替尺寸验证；齿数、孔型、尺寸、单位、材料和加工方法应通过文件内容、装配资料及实车核对后确定。
- 下载 STP 不等于可以直接打印，下载 DXF 不等于已确定齿轮制造工艺。实车齿轮版本、罩固定点、OPB815WZ 光路与平台间隙仍需核对；本次未购买、加工、钻孔或安装。
