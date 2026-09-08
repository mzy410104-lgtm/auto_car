# 三人Git与GitHub协作说明

Git记录文件版本；GitHub提供共享仓库、Issues、Pull Requests和Projects等协作工具。当前采用一个main主分支加短期任务分支，不按成员长期分成三个互不集成的版本。

## 1. 每项工作如何管理

1. 在Issue中写明问题/目标、负责人、对应计划任务、依赖与完成证据。六项初始任务见[TASK_BOARD.md](TASK_BOARD.md)。
2. 一次选一个有明确边界的任务；需要多人配合时写明参与者，仍按个人实际时间计入计划。
3. 从同步后的main创建任务分支，在分支修改源码、配置、文档或测试记录。
4. 查看差异，只暂存本任务文件，提交并推送该分支。
5. 创建Pull Request，写明改变了什么、为什么、验证到了哪一步、关联哪项Issue，由另一位组员复核。
6. 合并后按实际完成证据更新任务。硬件Issue不因提交或PR合并而自动认定通过。

GitHub账号与A/B/C尚未一一对应，不能凭职责标签指定远程账号。看板状态按本组规则维护；仓库文件中的状态名不代表GitHub Projects字段已经配置。

## 2. 日常操作

其他成员首次获取项目，在其选定的父目录执行：

```sh
git clone https://github.com/mzy410104-lgtm/auto_car.git
cd auto_car
```

已有本地仓库不再次初始化或重复克隆。下列命令在实际仓库目录中执行：

```sh
git status -sb
git remote -v
git branch --show-current
```

确认当前改动已妥善保存、主分支确为main且已配置上游后，再同步：

```sh
git switch main
git pull --ff-only
```

本项目约定分支名使用task/加实际任务编号；完整名字由本次任务明确填写。创建前检查是否已有同名分支，不把文档示例当现存分支。

```text
git switch -c <本次新建的准确分支名>
git diff
git add -- <本次实际修改的文件路径>
git diff --cached
git commit -m "说明本次具体改变"
git push --set-upstream <git remote中已确认的名称> <当前准确分支名>
```

尖括号内容是必须替换的说明，不可原样运行。不要为方便直接暂存整个工作目录。推送完成才在GitHub创建PR；PR的源分支和目标main以页面实际内容核对。

如果pull --ff-only因分叉失败，保留报错与现有改动，检查两端历史后处理；不以强制推送、硬重置或清理未跟踪文件作为默认修复。

## 3. 三类结果分别登记

| 内容 | 证明什么 | 不能据此认定 |
|---|---|---|
| Commit / PR | 文件变化、审查与合并 | 硬件已经正常运行 |
| 编译/下载记录 | 工程构建、写入过程 | 主程序已运行、通信或控制通过 |
| 实测记录 | 所记录接线、软件版本和条件下的结果 | 未测试条件也通过 |

测试记录使用[模板](tests/records/TEMPLATE.md)。记录提交版本、实际供电/接线、数据、测试时长、成功/失败和下一步。没有结果就保留待补证据，不填写示例电压或速度冒充实测。

## 4. 文件与设备协作

- A重点维护硬件/供电/机械记录，B维护树莓派与雷达软件，C维护STM32工程；interfaces中的约定由B/C共同复核。
- 同一份接线、接口或CubeMX工程修改前协调负责人，避免两人同时更改后难以合并。
- Git分支只能隔离文件修改，不能隔离实车接线。单车改线、静态扫描和动作测试仍按工作计划错开。
- 当前没有实际固件/树莓派工程，导入时保留原工程与依赖依据，再按真实构建输出补充忽略规则，不先猜生成目录或引脚。
- tmp、本机配置、原厂下载副本和大型原始数据按.gitignore保留在本地；测量表、小型日志与数据索引可以提交到tests/records。
- 对公开提交逐项检查数据内容与来源，团队凭据保存在Git凭据管理工具或本地配置中，不写入仓库。

## 5. 首次三人协作

1. 仓库拥有者在确认另外两位的准确GitHub账号后添加协作者，组员接受邀请。
2. 各人用仓库实际地址克隆到自己的工作目录，使用各自真实Git提交身份。
3. 各人选一个已明确任务，提交一次小改动并互相审查；不修改另一人的本机工作目录。
4. 每周复盘在Issue中更新实际投入、结果、阻塞与下一步，文档计划保留总体安排。

当前决定为暂不邀请协作者；没有发送邀请，也未按A/B/C指派GitHub账号。以后开展多人协作时再落实准确账号。初次导入后建议通过PR修改main；这是一条团队约定，是否已配置服务器端保护须另行核验。

## 官方资料

- [Git初始化](https://git-scm.com/docs/git-init)、[查看差异](https://git-scm.com/docs/git-diff)、[推送](https://git-scm.com/docs/git-push)。
- [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow)、[Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects)。

本次操作文档通过Context7及官方资料核对；实际命令仍以仓库当前状态和已确认标识符为准。
