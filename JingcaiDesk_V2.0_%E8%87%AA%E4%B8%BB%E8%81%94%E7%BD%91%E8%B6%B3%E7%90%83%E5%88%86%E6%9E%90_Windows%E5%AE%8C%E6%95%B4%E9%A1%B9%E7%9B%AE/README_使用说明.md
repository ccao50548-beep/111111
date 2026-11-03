# JingcaiDesk V2.0｜AI自主联网足球分析终端

## 产品说明

这是非官方第三方足球研究工具，**并非中国体育彩票官方APP**，不销售彩票、不自动投注，也不保证命中。这里的“AI”指自动抓取结构化赛程、规则化概率建模与研究说明，**当前不包含外部大语言模型、自动网页搜索引擎或保证盈利的算法**。

### 已完成的能力

- 中文 Windows GUI：查询日期、赛程、来源、胜平负概率、比分前5、总进球0—7+分布。
- 自主联网：默认 TheSportsDB 公开赛事 API 取当日（北京时间）的足球比赛；可配置 football-data.org API Token 查询多个联赛近135天比赛及当天比赛。
- 当双方至少有5场赛前历史比赛时，使用历史进失球估算 **泊松模型的进球均值代理值**；不是官方xG。无足够数据不预测。
- 支持已获授权的体彩竞彩足球 JSON 数据接口（需符合项目原有JSON schema）或 CSV 导入。
- Windows EXE 的“每天11点自动刷新”按钮：使用 schtasks 创建系统任务。失败写到 `%APPDATA%\JingcaiDesk\refresh.log`。
- 导出 HTML 研究报告，自动存档（每天执行成功后写入 reports 文件夹）。

### 重要限制

1. **TheSportsDB 和 football-data.org 返回的是普通足球比赛，不是中国体育彩票官方竞彩足球受注场次。** 两者的比赛不得被当成可投注场次，更无法保证覆盖所有竞彩比赛。体彩受注信息须独立核实：https://www.sporttery.cn/。
2. TheSportsDB 免费接口可能限流，部分比赛没有UTC时间，不会强行填充。通常无法提供足够球队历史，因此默认只展示赛程，不编造概率。
3. football-data.org 要自己去 https://www.football-data.org/ 注册并取得 API Token；不同套餐覆盖赛事不同、存在调用频率上限。建议最多先设3—4个联赛，必要时分批。Token 在本机 config.json 明文存储，不适合共享电脑；也可以使用环境变量 `FOOTBALL_DATA_TOKEN` 替代并在设置里留空。
4. 每天11:00使用Windows系统**本地时区**，请将Windows设置为 **UTC+08:00 中国标准时间**，否则要自行在任务计划程序调整运行时刻。电脑需开机联网。网页接口失效会记录日志，而不是伪造赛程。
5. 该模型基于历史比赛进失球的保守代理参数，忽略首发、伤停、战术、红牌、临场波动、奖金赔率等因素；不能据此判断可盈利投注。程序中的“优先研究”只是概率集中度标签，不是下注推荐。竞彩足球多种玩法规则与模型概率不完全等同。
6. 任何比赛预测和外部接口使用须遵守数据提供方条款。**本软件不含可直接商用的彩票赛程授权**。

## 如何得到 Windows EXE（自己无需安装 Python）

1. 在 GitHub 建立一个**新仓库** `JingcaiDesk`，勿上传到AStockPro仓库。
2. **解压本压缩包，上传其中所有项目文件到仓库根目录**，需保留 `.github/workflows/build-windows.yml`。GitHub网页上传时可能忽略隐藏的 `.github` 目录，可通过“Add file → Create new file”创建对应路径。
3. Actions → `Build JingcaiDesk V2 Windows EXE` → Run workflow → main → Run workflow。
4. 构建绿勾后，在 Artifacts 下载 `JingcaiDesk-V2-Windows-EXE.zip`，解压得到 `JingcaiDesk.exe`。
5. Windows 双击启动。PyInstaller 构建完成不代表网络数据接口一定可用，应实测。

## 首次使用

- 先点击“联网搜索当日比赛”，默认 TheSportsDB 免费接口直接调用；请允许网络连接。
- 若想要模型预测，请点击“数据源设置”并选择 `football-data.org（需Token）`，填入自行获取的 Token，然后选择支持的联赛。联网获取后的比赛若历史数据不足仍会显示“参数不足”。
- 如已获得**合法的竞彩受注清单**，点击“导入体彩场次CSV”。示例路径 `sample/示例数据_请勿当作真实比赛.csv` 仅供测试，不能用于购彩。
- 点击“每天11点自动刷新”，创建系统计划任务。要查看调度运行结果，打开“查看更新日志”或 Windows 的“任务计划程序”。
- 导出报告支持 HTML，报告内标记场次来源和参数来源。

## 开发者本地测试

Python 3.12+（源代码可运行），无需额外安装 Python 库：

```shell
python -m unittest discover -s tests -v
python app.py
python app.py --refresh
```

## 核心文件

- `app.py`：GUI、数据源设置、联网操作、定时任务。
- `core.py`：SQLite数据、概率、HTML报告。
- `sources.py`：TheSportsDB / football-data.org 联网源、历史进失球参数估算。
- `refresh.py`：API配置、自动批量同步、任务入口。
- `.github/workflows/build-windows.yml`：Windows云端编译。

**不建议把私人Token发布到 GitHub 代码中；软件配置默认保存在你的电脑，不放在仓库。**
