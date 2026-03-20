# hyakumeiten

## 概述
这是一个用于从 Tabelog（日本餐厅评分网站）爬取“百名店”与 Top 排名餐厅数据并输出 CSV 的项目。

目录结构（核心）：
- `code/`：爬虫与数据合并脚本
- `output/`：脚本输出的 CSV 文件
- `index.html`, `index_kanto.html`, `template_v2.html`：可选展示/分析页面

---
## 关键文件说明

### `code/config.py`
项目配置文件，定义爬虫 URL、输出 CSV 路径、目标字段列名。
常用变量：
- `hyakumeiten_main_site`：百名店主页
- `award_main_site`：奖项页面基址
- `ranking_main_site`：排名页面基址
- `col_list`：最终 CSV 字段顺序
- 各 CSV 路径：`HYAKUMEITEN_ADDITION_PATH`, `HYAKUMEITEN_OUTPUT_PATH`, `TABELOG_OUTPUT_PATH`, `TABELOG_INPUT_PATH`, `TOP_ADDITION_PATH`

### `code/utils.py`
通用爬虫工具：
1. `get_session(...)`：创建带重试的 `requests.Session`
2. `fetch_url(...)`：带异常处理和延迟的单 URL 请求
3. `generate_sub_site_res_list(...)`：从百名店分类页抓取所有餐厅详情页 URL
4. `generate_top_sub_site_res_list(...)`：从排名列表页抓取餐厅详情页 URL
5. `generate_res_details(...)`：解析每个餐厅详情页，提取20+字段并返回 DataFrame

### `code/tabelog_scrapping.py`
基础脚本（单步）
- 输入：`output/tabelog_input.csv`，该文件应包含 `tabelog_site` 一列（目标餐厅详情页 URL）
- 过程：调用 `generate_res_details` 解析每个链接
- 输出：`output/tabelog_output.csv`

运行方式：
```bash
python code/tabelog_scrapping.py
```

---
### `code/tabelog_top_addition.py`
Top 页面批量抓取脚本
- 范围：`start=1` 到 `end=61`，从 `ranking_main_site` + 页码 + `ranking_suffix` 抓取链接
- 过程：先抓取 Top 列表页餐厅链接，再解析 Detail
- 输出：
  - `output/tabelog_top_output.csv`
  - `output/tabelog_top_addition.csv`（与 `TOP_ADDITION_PATH` 一致）

运行方式：
```bash
python code/tabelog_top_addition.py
```

---
### `code/tabelog_hyakumeiten_addition.py`
百名店补充脚本（追加&合并）
- 步骤：
  1. 从 `hyakumeiten_main_site` 抓取百名店分类子页面列表
  2. 用 `start` 和 `end` 控制采集某个子页面范围
  3. 抓取该子页面内所有餐厅链接
  4. 调用 `generate_res_details` 解析
  5. 写入 `output/tabelog_hyakumeiten_addition.csv`
  6. 读取 `output/tabelog_hyakumeiten_output.csv` 并合并去重，再写回该文件

运行方式：
```bash
python code/tabelog_hyakumeiten_addition.py 0 2
```
(这是左闭右开，也就是会抓取第0和第1个list)

本脚本适合用于“百名店更新”时追加新链接并保持输出文件最新。

---
### `code/update_hyakumeiten.py`
（如果存在，可补充运行逻辑，此项目当前文件未检查到完整脚本注释，可按实际需求扩充）

### `output/` CSV 对应说明
- `output/tabelog_input.csv`：手动或程序补充的目标餐厅详情页链接输入（脚本 `tabelog_scrapping.py` 的输入）
- `output/tabelog_output.csv`：`tabelog_scrapping.py` 解析结果
- `output/tabelog_top_output.csv`：Top 列表抓取后结果
- `output/tabelog_top_addition.csv`：Top 补充输出（与 `tabelog_top_output.csv` 内容相近）
- `output/tabelog_hyakumeiten_addition.csv`：百名店补充解析结果
- `output/tabelog_hyakumeiten_output.csv`：百名店主输出（合并后结果）
- `output/tabelog_been_input.csv`：已有店铺标记/历史输入（备份 etc.）

字段说明（部分）:
- `restaurant_name`, `rating`, `main_genre`, `address_region`, `address_locality`, `address_street`, `closest_station`
- `rating_users`, `save_users`, `lunch_budget`, `dinner_budget`, `review_lunch_budget`, `review_dinner_budget`
- `award_medals`, `award_selections`, `award_kamiawa`, `genre`, `transportation`, `opening_hrs`, `payment_methods`, `no_of_seats`
- `official_website`, `social_account`, `opening_date`, `remarks`, `branches`, `tabelog_site`, `lat`, `lng`, `image`, `price_range`

---
## 运行建议流程
1. 先更新 `output/tabelog_input.csv`（输入链接）
2. 运行 `python code/tabelog_scrapping.py` 得到初始 `tabelog_output.csv`
3. 运行 `python code/tabelog_top_addition.py` 获取排名补充数据
4. 运行 `python code/tabelog_hyakumeiten_addition.py` 获取百名店补充并合并
5. 用 `index.html` 或 `index_kanto.html` 做可视化/进一步分析

---
## 环境与依赖
建议创建虚拟环境并安装：
```bash
python -m venv .venv
source .venv/bin/activate
pip install requests beautifulsoup4 pandas urllib3
```

---
## 注意事项
- Tabelog 反爬机制会对频繁请求限速，请避免短时间大量请求。
- `start`/`end` 参数可调节抓取范围，防止一次性抓取过多页面导致超时。
- 若页面结构变动，`generate_res_details` 中字段定位可能失效，需要根据网页源码更新解析逻辑。
