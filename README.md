## 一、房源情况介绍

### 数据规模
- 覆盖区域：北京 行政区（如海淀、朝阳、通州、昌平、大兴、房山、西城、丰台、顺义、东城）
- 价格区间：约 500–25000 元/月
- 支持查询：价格、户型、区域、地铁距离、附近地标、可入住日期、西二旗通勤时间等维度
- 地标数据：地铁站、世界 500 强企业、商圈地标（含商超/公园）

### 数据源说明
**1. 房源基础信息**

覆盖地址、户型、面积、租金、可入住日期与楼层，可按行政区与商圈检索。

- 地址：北京行政区，房源落在地铁站、商圈、世界 500 强企业所在地标周边，小区名与商圈具体名称由地标决定（例如西二旗、国贸、望京）。
- 户型：整租与合租约各占 50%；整租为一居至四居多种室厅卫组合，面积约 22～145 ㎡；合租为单间，整套为 2 室、3 室或 4 室一厅一卫或两卫，单间面积约 12～30 ㎡，月租约 1200～3500 元。
- 租金：整租月租约 800～28000 元/月，付款单位元/月。

**2. 通勤信息**

每条房源均带地铁与到西二旗通勤信息，支持按商圈、地铁距离、通勤时间筛选。

- 最近地铁站及距地铁站距离约 200～5500 米分段覆盖。
- 到西二旗通勤时间约 8～95 分钟。

**3. 配置信息**

仅覆盖周边生活配套中的商超与公园。

- 可查房源周边商超、公园及距离。

**4. 房屋设施**

含电梯、装修、朝向、卫生间（室厅卫中的几卫），。

- 装修：简装、精装、豪华、毛坯、空房。
- 朝向：朝南、朝北、朝东、朝西、南北、东西。
- 卫生间：以室、厅、卫中的「几卫」体现（如一卫、双卫）。

**5. 房源隐形信息**

含噪音水平、标签与房源状态，用于表达「近地铁但临街略吵」、采光等潜在信息。

- 噪音水平：安静、中等、吵闹、临街。
- 标签：近地铁、双地铁、多地铁；精装修、豪华装修、毛坯、空房；朝南、南北通透、采光好；有电梯、高楼层、高层；小户型、大户型、大两居、大三居、双卫；核心区、学区房、近高校；合租、小单间、商住；低价、高性价比、农村房、农村自建房；部分商圈或路名。
- 房源状态：可租、已租、下架（约 90%、5%、5%）。

---

## 二、接口使用硬性要求

### 请求头
**房源相关接口（/api/houses/*）必须带请求头** `X-User-ID`，否则返回 400
地标接口（/api/landmarks/*）不需 X-User-ID

<font color=red>X-User-ID的值即为用户工号，注意必须传比赛平台注册的用户工号，比赛的用例会按照用户工号隔离执行，若传值有误，用例执行结果会有冲突影响成绩！</font>

### 房源数据重置
用例执行过程可能会改变房屋的状态（可租/已租/下架）,重复执行同一个用例时由于数据状态发生改变会导致执行失败，因此建议在agent中定义每新起一个session，就去调用房源数据重置接口，保障每次用例执行都能使用初始化的数据。
#### 房源数据重置接口
调用示例：curl -s -X POST -H "X-User-ID: 真实工号" "http://IP:8080/api/houses/init"
**注**自动打榜 在每个用例执行前会自动进行房源初始化

### 租房/退租/下架操作
必须调用 对应API 才算完成操作，仅对话生成 [ 已租 ] 无效

### 近距离概念说明
- **近地铁**：指房源到最近地铁站的直线距离。接口返回字段为 `subway_distance`（单位：米）。筛选时用参数 `max_subway_dist`：**800 米以内**视为近地铁，**1000 米以内**视为地铁可达。
- **地标附近房源**（接口 9）：以地标为圆心，按**直线距离**（米）筛选，参数 `max_distance` 默认 2000。返回结果中同时给出 `distance_to_landmark`（直线距离）、`walking_distance`（估算步行距离）、`walking_duration`（估算步行时间，分钟）。
- **小区周边地标**（接口 10）：以该小区为基准点，按**直线距离**（米）筛选，参数 `max_distance_m` 默认 3000，用于查商超、公园等周边配套。

## 三、可用接口列表
黄区IP：***
绿区IP：***
端口：8080
| 序号 | 方法 | 路径 | 用途 |
|------|------|------|------|
| 1 | GET | /api/landmarks | 获取地标列表，支持 category、district 同时筛选（取交集）。用于查地铁站、公司、商圈等地标。不需 X-User-ID。 |
| 2 | GET | /api/landmarks/name/{name} | 按名称精确查询地标，如西二旗站、百度。返回地标 id、经纬度等，用于后续 nearby 查房。不需 X-User-ID。 |
| 3 | GET | /api/landmarks/search | 关键词模糊搜索地标。支持 category、district 同时筛选，多条件取交集。不需 X-User-ID。 |
| 4 | GET | /api/landmarks/{id} | 按地标 id 查询地标详情。不需 X-User-ID |
| 5 | GET | /api/landmarks/stats | 获取地标统计信息（总数、按类别分布等）。不需 X-User-ID。 |
| 6 | GET | /api/houses/{house_id} | 根据房源 ID 获取单套房源详情。无 query 参数，仅路径带 house_id，返回一条（安居客），便于智能体解析。调用时请求头必带 X-User-ID。 |
| 7 | GET | /api/houses/listings/{house_id} | 根据房源 ID 获取该房源在链家/安居客/58同城等各平台的全部挂牌记录。无 query 参数。调用时请求头必带 X-User-ID。响应 data 为 { total, page_size, items }。 |
| 8 | GET | /api/houses/by_community | 按小区名查询该小区下可租房源。默认每页 10 条、未传 listing_platform 时只返回安居客。用于指代消解、查某小区地铁信息或隐性属性。调用时请求头必带 X-User-ID。 |
| 9 | GET | /api/houses/by_platform | 查询可租房源，支持按挂牌平台筛选。listing_platform 可选：不传则默认使用安居客；传 链家/安居客/58同城 则只返回该平台。调用时请求头必带 X-User-ID。 |
| 10 | GET | /api/houses/nearby | 以地标为圆心，查询在指定距离内的可租房源，返回带直线距离、步行距离、步行时间。默认每页 10 条、未传 listing_platform 时只返回安居客。需先通过地标接口获得 landmark_id。调用时请求头必带 X-User-ID。 |
| 11 | GET | /api/houses/nearby_landmarks | 查询某小区周边某类地标（商超/公园），按距离排序。用于回答「附近有没有商场/公园」。调用时请求头必带 X-User-ID。 |
| 12 | GET | /api/houses/stats | 获取房源统计信息（总套数、按状态/行政区/户型分布、价格区间等），按当前用户视角统计。调用时请求头必带 X-User-ID。 |
| 13 | POST | /api/houses/{house_id}/rent | 将当前用户视角下该房源设为已租。传入房源 ID 与 listing_platform（必填，链家/安居客/58同城）以明确租赁哪个平台；三平台状态一并更新，响应返回该条。调用时请求头必带 X-User-ID。 |
| 14 | POST | /api/houses/{house_id}/terminate | 将当前用户视角下该房源恢复为可租。传入房源 ID 与 listing_platform（必填）以明确操作哪个平台；三平台状态一并更新，响应返回该条。调用时请求头必带 X-User-ID。 |
| 15 | POST | /api/houses/{house_id}/offline | 将当前用户视角下该房源设为下架。传入房源 ID 与 listing_platform（必填）以明确操作哪个平台；三平台状态一并更新，响应返回该条。调用时请求头必带 X-User-ID。 |


## 四、客户端组件使用说明

本项目提供基于需求文档实现的 **Python API 客户端**，便于 Agent 或评测脚本直接调用接口。

### 安装

```bash
pip install -r requirements.txt
# 或以可编辑方式安装当前目录
pip install -e .
```

### 直接运行示例

在项目根目录执行（将 `http://IP:8080` 和 `你的工号` 换成实际值）：

```bash
# 完整演示：创建客户端 + 房源重置 + 地标/房源统计与列表
python run_example.py --base-url http://IP:8080 --user-id 你的工号

# 不调用房源重置，仅查询
python run_example.py --base-url http://IP:8080 --user-id 你的工号 --no-init

# 仅演示地标接口（不依赖工号，适合先验证服务连通性）
python run_example.py --base-url http://IP:8080 --landmarks-only
```

### 基本用法

```python
from agent_game_fake_app_api import FakeAppApiClient, create_client_and_init

base_url = "http://你的IP:8080"
user_id = "你的工号"  # 比赛平台注册的用户工号，必填

# 方式一：仅创建客户端
client = FakeAppApiClient(base_url=base_url, user_id=user_id)

# 方式二：创建客户端并执行一次房源重置（建议每个新 session 调用）
client = create_client_and_init(base_url=base_url, user_id=user_id)
```

### 地标接口（不需 X-User-ID，客户端内部已区分）

```python
landmarks = client.get_landmarks(category="subway", district="海淀")
xierqi = client.get_landmark_by_name("西二旗站")
list_res = client.search_landmarks("国贸", category="landmark")
stats = client.get_landmark_stats()
```

### 房源接口（自动附带 X-User-ID）

```python
# 房源数据重置（新 session 建议先调用）
client.init_houses()

house = client.get_house("HF_2001")
listings = client.get_house_listings("HF_2001")
by_community = client.get_houses_by_community(community="建清园(南区)")
by_platform = client.get_houses_by_platform(
    district="海淀",
    min_price=2000,
    max_price=5000,
    max_subway_dist=800,
    page=1,
    page_size=10,
)
nearby = client.get_houses_nearby(landmark_id="SS_001", max_distance=2000)
nearby_landmarks = client.get_nearby_landmarks(community="建清园(南区)", landmark_type="shopping")
house_stats = client.get_house_stats()
```

### 租房 / 退租 / 下架（必须调用 API 才算完成）

```python
client.rent_house("HF_2001", "安居客")
client.terminate_rental("HF_2001", "安居客")
client.take_offline("HF_2001", "链家")
```

### OpenAPI 规范

接口定义见 `fake_app_agent_tools.json`（含房源数据重置 `POST /api/houses/init`），可供 Agent 工具描述或代码生成使用。

---

## 五、测试

### 运行单元测试（无需真实服务，可直接跑）

```bash
# 安装测试依赖
pip install -r requirements.txt
pip install pytest

# 运行全部单元测试（Mock 请求，不访问真实 API）
python -m pytest tests/ -v

# 或使用项目内脚本
python run_tests.py
```

单元测试覆盖需求文档中的全部 16 个接口：请求方法、路径、查询参数、以及房源接口必带 `X-User-ID`、地标接口不带等行为。

### 运行集成测试（需真实服务）

使用脚本（推荐，自动注入环境变量）：

```bash
python run_integration_tests.py --base-url http://你的服务IP:8080 --user-id 你的工号
```

或使用环境变量后直接调 pytest：

```bash
# Windows
set RUN_INTEGRATION=1
set BASE_URL=http://你的服务IP:8080
set USER_ID=你的工号
python -m pytest tests/test_integration.py -v

# Linux / macOS
RUN_INTEGRATION=1 BASE_URL=http://你的服务IP:8080 USER_ID=你的工号 python -m pytest tests/test_integration.py -v
```

---

## 六、部署到服务器（商用）

1. **环境**：Python 3.10+，安装依赖 `pip install -r requirements.txt`。
2. **安装方式二选一**：
   - 直接拷贝项目到服务器，在应用代码中把项目目录加入 `sys.path` 后 `from agent_game_fake_app_api import FakeAppApiClient, create_client_and_init`。
   - 或在本机打包：`pip install build && python -m build`，将生成的 dist 内 wheel/sdist 上传至服务器后 `pip install xxx.whl`。
3. **配置**：在业务中通过环境变量或配置中心注入 `BASE_URL`（租房仿真 API 基地址）和 `USER_ID`（用户工号），再创建客户端调用。
4. **上线前**：在目标环境执行 `python -m pytest tests/ -v`，确认 29 个单元测试通过；若有真实服务，可再跑集成测试做连通性校验。

---

## 七、FAQ

Q：重复执行同一个用例，第二次执行后房源数据查不到了  
A：首次执行用例时，将房源状态更新为了已租，再次执行用例，查询可租房源时返回结果必然为空。此时可以手动触发房源重置接口（见章节二）。

