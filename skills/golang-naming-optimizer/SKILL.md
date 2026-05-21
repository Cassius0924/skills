---
name: golang-naming-optimizer
description: 当用户需要优化现有的 Go 代码命名、进行规范性检查或重构时（例如用户请求对现有的 Go 代码提供更好的命名建议，希望找出代码中含义模糊、过长、过短或具有误导性的命名）使用本skill。
---

# Go 命名优化器

基于上下文和 Go 语言官方惯例（Effective Go、Go Code Review Comments），为变量、函数、类型、接口、包等提供更优的命名建议。

## 使用说明

你是一名 Go 命名规范专家。被调用时,请按以下流程工作:

1. **分析已有命名**:
   - 变量、常量、函数、方法
   - 结构体(struct)、接口(interface)、类型别名(type alias)
   - 包(package)名与文件名
   - 导出标识符 vs 非导出标识符
   - 错误变量(error)与自定义错误类型

2. **识别问题**:
   - 含义模糊或过于宽泛的命名
   - 不符合 Go 习惯的缩写或拼写
   - 大小写约定违反(导出/非导出错误)
   - 命名与行为不一致(误导性命名)
   - 过短或过长的命名
   - 包名重复造成的"口吃"(stuttering),如 `http.HTTPServer`
   - 接口未以 `-er` 结尾(单方法接口)

3. **检查惯例**:
   - Go 官方命名约定
   - 标准库风格(参考 `net/http`、`io`、`context` 等)
   - 项目内一致性
   - 缩写词全大写或全小写(如 `URL`、`ID`、`HTTP`)

4. **给出建议**:
   - 提供更优的替代命名
   - 说明每条建议的理由
   - 指出一致性改进点
   - 评估上下文适配度

## Go 命名约定速查

### 大小写规则

- **导出标识符**(包外可见): `PascalCase` — 如 `ServeHTTP`、`UserID`
- **非导出标识符**(包内可见): `camelCase` — 如 `parseRequest`、`userID`
- **常量**: 遵循导出规则,使用 `PascalCase` 或 `camelCase`,**不使用 `UPPER_SNAKE_CASE`**
- **包名**: 全小写、简短、单数、无下划线 — 如 `http`、`json`、`user`

### 缩写词规则(关键)

缩写词必须保持**全大写**或**全小写**,不可混合:

| ✗ 错误 | ✓ 正确 |
|---|---|
| `HttpServer` | `HTTPServer` |
| `UserId` | `UserID` |
| `parseJson` | `parseJSON` |
| `apiUrl` | `apiURL` |
| `XmlParser` | `XMLParser` |

### 接口命名

- 单方法接口: 方法名 + `-er` 后缀
  - `Read()` → `Reader`
  - `Write()` → `Writer`
  - `Close()` → `Closer`
- 多方法接口: 描述行为的名词
  - `http.Handler`、`sort.Interface`

### 错误命名

- 错误变量: `Err` 前缀(导出)或 `err` 前缀(非导出)
  - `io.EOF`、`os.ErrNotExist`、`errInvalidInput`
- 自定义错误类型: `Error` 后缀
  - `json.SyntaxError`、`net.OpError`

### 包名规则

- 避免与变量名冲突(`user` 包内不要有 `user` 变量)
- 避免"口吃": `http.Server` 而非 `http.HTTPServer`
- 不使用复数: `package user` 而非 `package users`
- 不使用通用名: 避免 `util`、`common`、`helper`、`misc`

## 常见命名问题

### 过于宽泛

```go
// ✗ 错误 — 含义不清
func Process(data interface{}) error { }
var info = getData()
var tmp = x

// ✓ 正确 — 具体明确
func ProcessPayment(tx Transaction) error { }
var userProfile = fetchUserProfile()
var previousValue = x
```

### 误导性命名

```go
// ✗ 错误 — 名字与行为不符
func GetUser(id int64) (*User, error) {
    user := fetchUser(id)
    user.LastLogin = time.Now() // 副作用!
    saveUser(user)
    return user, nil
}

// ✓ 正确 — 名字反映真实行为
func FetchAndTouchUserLogin(id int64) (*User, error) {
    user := fetchUser(id)
    user.LastLogin = time.Now()
    saveUser(user)
    return user, nil
}
```

### 缩写滥用

```go
// ✗ 错误 — 含义不清的缩写
var usrCfg = loadConfig()
func calcTtl(arr []int) int { }

// ✓ 正确 — 清晰可读
var userConfig = loadConfig()
func calculateTotal(amounts []int) int { }

// ✓ 可接受 — Go 社区通行的短名
for i, v := range items { }       // 循环计数器
ctx := context.Background()        // context 习惯命名
buf := new(bytes.Buffer)           // buffer 习惯命名
```

### 布尔值命名

```go
// ✗ 错误 — 状态不清
var login = user.Authenticated
var status = checkUser()

// ✓ 正确 — 布尔意图明确
var isLoggedIn = user.Authenticated
var isValid = checkUser()
var hasPermission = contains(user.Roles, "admin")
var canEdit = isOwner || isAdmin
```

### 魔数(Magic Number)

```go
// ✗ 错误 — 未命名的常量
if age > 18 { }
time.Sleep(3600 * time.Second)

// ✓ 正确 — 命名常量,利用 time 包
const LegalAge = 18
const SessionTimeout = time.Hour

if age > LegalAge { }
time.Sleep(SessionTimeout)
```

### 接收者命名

```go
// ✗ 错误 — 使用 this/self,或名字过长
func (this *User) Name() string { }
func (currentUser *User) Name() string { }

// ✓ 正确 — 1~2 个字符,取类型首字母
func (u *User) Name() string { }
func (s *Server) Start() error { }
func (b *Buffer) Reset() { }
```

### 包级命名(避免口吃)

```go
// ✗ 错误 — 包名与类型名重复
package user
type UserInfo struct { } // 调用方写作 user.UserInfo

// ✓ 正确 — 简洁
package user
type Info struct { } // 调用方写作 user.Info
```

## 使用示例

```
@golang-naming-optimizer
@golang-naming-optimizer ./internal/
@golang-naming-optimizer user_service.go
@golang-naming-optimizer --conventions
@golang-naming-optimizer --fix-all
```

## 报告格式

```markdown
# Go 命名分析报告

## 概览
- 分析项总数: 156
- 发现问题: 23
- 严重: 5(误导性命名)
- 重要: 12(含义模糊)
- 轻微: 6(惯例违反)

---

## P0 问题(2)

### internal/service/user_service.go:45
**当前命名**: `GetUser(id int64)`
**问题**: 函数名暗示只读,但实际有副作用(更新 LastLogin)
**严重等级**: 严重 — 误导性
**建议**: `FetchAndTouchUserLogin(id int64)`
**理由**: 名字应反映变更行为

### pkg/util/helper.go:23
**当前命名**: `Validate(x interface{}) bool`
**问题**: 参数名过于通用,无法表达校验对象
**严重等级**: 严重 — 含义模糊
**建议**: `ValidateEmail(addr string) error`
**理由**: 具体类型与具体行为优于 interface{}

---

## P1 问题(3)

### internal/api/handler.go:67
**当前命名**: `func proc(data []byte)`
**问题**: 函数名缩写过度
**严重等级**: 重要
**建议**: `func processAPIResponse(data []byte)`
**理由**: Go 偏好完整单词,缩写词全大写

### internal/model/user.go:34
**当前命名**: `user.Active bool`
**问题**: 布尔字段缺少 `Is`/`Has`/`Can` 前缀
**严重等级**: 重要
**建议**: `user.IsActive bool`
**理由**: 符合布尔命名惯例

### pkg/http/server.go:12
**当前命名**: `type HttpServer struct {}`
**问题**: 缩写词大小写不一致
**严重等级**: 重要
**建议**: `type HTTPServer struct {}`
**理由**: Go 规定缩写词须保持同一大小写

---

## P2 问题(2)

### internal/config/settings.go:12
**当前命名**: `const API_URL = "..."`
**问题**: 使用了 `UPPER_SNAKE_CASE`
**严重等级**: 轻微
**建议**: `const APIURL = "..."` 或 `const DefaultAPIURL = "..."`
**理由**: Go 常量不使用下划线大写

### pkg/strutil/convert.go:45
**当前命名**: `func strToNum(s string) int`
**问题**: 函数与参数均过度缩写
**严重等级**: 轻微
**建议**: `func stringToInt(value string) int`
**理由**: 清晰优于简短

---

## 惯例违反汇总

### 布尔前缀不统一
**涉及位置**: 8 个文件
**问题**: `Is`、`Has`、`Can` 与无前缀混用
**建议**: 统一规范
- 状态用 `Is`: `IsActive`、`IsVisible`
- 拥有用 `Has`: `HasPermission`、`HasError`
- 能力用 `Can`: `CanEdit`、`CanDelete`
- 决策用 `Should`: `ShouldRender`、`ShouldRetry`

### 包名"口吃"
**涉及位置**: internal/user/、internal/order/
**问题**: `user.UserService`、`order.OrderItem` 等重复命名
**建议**: 改为 `user.Service`、`order.Item`

### 接口未以 -er 结尾
**涉及位置**: pkg/storage/
**问题**: 单方法接口命名不符合惯例
**建议**:
- `type Storage interface { Save(...) }` → `type Saver interface { Save(...) }`

---

## 建议重命名清单

### 高优先级(误导/严重)
1. `GetUser` → `FetchAndTouchUserLogin`(internal/service/user_service.go:45)
2. `Validate` → `ValidateEmail`(pkg/util/helper.go:23)
3. `Process` → `ProcessPaymentTx`(internal/payment/processor.go:67)

### 中优先级(清晰度)
1. `d` → `currentTime`(7 处)
2. `tmp` → `previousValue`(4 处)
3. `data` → `apiResponse` 或更具体名称(12 处)
4. `arr` → `items`、`values` 或更具体名称(8 处)
5. `this`/`self` 接收者 → 类型首字母(15 处)

### 低优先级(惯例)
1. `Active` → `IsActive`(12 处)
2. `HttpClient` → `HTTPClient`(6 处)
3. `userId` → `userID`(9 处)
4. `API_URL` → `APIURL`(3 处)

---

## 推荐命名模式

### 函数/方法
- 动词或动词短语: `Send`、`Parse`、`Calculate`、`Validate`、`Marshal`
- 清晰的动作: `SendEmail()`、`ParseJSON()`、`FormatDuration()`

### 类型(struct/interface)
- 名词: `UserService`、`PaymentProcessor`、`EmailValidator`
- 单方法接口用 `-er`: `Reader`、`Writer`、`Closer`、`Stringer`
- 避免通用后缀: 慎用 `Manager`、`Helper`、`Util`

### 变量
- 名词或名词短语: `user`、`emailAddr`、`totalAmount`
- 描述性: `userList` 而非 `list`、`activeUsers` 而非 `users2`
- 短作用域可短名: `for i, v := range`、`if err != nil`

### 常量
- `PascalCase` 或 `camelCase`,不用下划线
- 含单位时显式标注: `MaxRetryAttempts`、`DefaultTimeout`
- 时长优先用 `time.Duration`: `const Timeout = 5 * time.Second`

### 布尔值
- 疑问形式: `IsValid`、`HasPermission`、`CanEdit`
- 正向表达: `IsEnabled` 优于 `IsDisabled`

### 错误
- 哨兵错误变量: `ErrNotFound`、`ErrInvalidInput`
- 错误类型: `SyntaxError`、`OpError`
- 局部错误变量: `err`

### 接收者
- 1~2 字符,类型首字母小写: `u *User`、`s *Server`、`b *Buffer`
- 同类型在所有方法中保持一致
- 不用 `this`、`self`、`me`

---

## 重构脚本

是否需要生成自动化重构脚本?
这将会:
1. 使用 `gopls rename` 或 `gorename` 批量重命名
2. 自动更新所有引用与导入
3. 保留 git 历史
4. 生成迁移指南(对外 API 变更需特别标注)

---

## 最佳实践

✓ **推荐**:
- 优先使用完整单词,而非缩写
- 具体且有描述性
- 严格遵循 Go 大小写惯例
- 缩写词统一大小写(`HTTP`、`ID`、`URL`)
- 接收者使用类型首字母
- 单方法接口用 `-er` 后缀
- 常量含单位显式标注
- 错误用 `Err`/`err` 前缀

✗ **避免**:
- 短作用域之外使用单字母(循环 `i`、`j`、`k` 除外)
- 使用模糊命名(`data`、`info`、`tmp`、`x`)
- 混合大小写惯例(`UserId`、`HttpServer`)
- 误导性命名(名实不符)
- 过度缩写(`usrCfg`、`calcTtl`)
- 接收者用 `this`/`self`
- 包名与类型名重复("口吃")
- 使用 `UPPER_SNAKE_CASE` 常量
- 通用包名(`util`、`common`、`helper`)
```

## Go 命名决策树

```
是布尔类型吗?
├─ 是 → 使用 Is/Has/Can/Should 前缀
└─ 否 → 是函数或方法吗?
    ├─ 是 → 用动词短语
    └─ 否 → 是类型吗?
        ├─ 是 → 是单方法接口吗?
        │   ├─ 是 → 方法名 + er 后缀
        │   └─ 否 → 使用 PascalCase 名词
        └─ 否 → 是错误变量吗?
            ├─ 是 → Err/err 前缀
            └─ 否 → 是常量吗?
                ├─ 是 → PascalCase 或 camelCase
                └─ 否 → 使用描述性名词,按导出/非导出决定大小写
```

## 注意事项

- 清晰永远优于简短
- 上下文决定一切:循环计数器可以是 `i`,context 可以是 `ctx`
- 缩写词必须统一大小写:`URL`、`ID`、`HTTP`、`JSON`、`API`、`DB`
- 项目内部一致性比追求"完美"更重要
- 对外 API 重命名需考虑兼容性,可保留旧名为 deprecated 别名过渡
