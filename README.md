# WeChat Chat Export for Windows

一个面向 Codex 的本地 Skill，用于在用户明确授权的前提下，从已经登录的 Windows 微信 4.x 客户端中，安全导出指定联系人的聊天记录及其关联媒体。

本项目强调以下原则：

- 只处理用户有权访问的本机微信数据。
- 先尝试只读方法，只有在用户明确授权后才允许临时 Hook。
- Hook 授权与重启微信授权相互独立。
- 数据库快照、解密和消息整理均在离线副本上完成，不修改微信原始数据库。
- 数据库密钥不得输出到终端、日志、报告或交付文件。
- 最终交付只包含指定联系人的消息和关联媒体，不包含其他联系人数据。

## 适用范围

适用于以下任务：

- 识别 Windows 微信 4.x 的程序版本和本地数据目录。
- 只读优先地恢复本地数据库解密所需信息。
- 在单独授权后执行临时 Hook 捕获，并在完成后卸载。
- 创建包含 WAL/SHM 文件的稳定数据库快照。
- 离线解密并验证 SQLite 数据库完整性。
- 按指定联系人和时间范围合并消息分库。
- 整理图片、语音、视频和文件等关联媒体。
- 生成可离线阅读的 HTML、Excel 和导出清单。

不适用于远程账号访问、密码或凭据恢复、监控他人、绕过系统权限，或导出用户无权访问的聊天。

## 安装

将整个仓库复制或克隆到 Codex 的个人 Skills 目录：

```text
%USERPROFILE%\.codex\skills\wechat-chat-export-windows
```

然后重新打开相关 Codex 任务，或让 Codex 重新发现可用 Skills。

## 使用

在 Codex 中调用：

```text
使用 $wechat-chat-export-windows，导出当前电脑微信里与“联系人名称”的全部聊天记录，包含图片、语音、视频和文件，生成可以离线阅读的 HTML 和 Excel。
```

执行过程中，Skill 会根据实际情况分别请求必要授权。允许临时 Hook 不等于允许重启微信；如果需要重启，会再次明确说明。

## 目录结构

```text
wechat-chat-export-windows/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   └── windows-v4-workflow.md
└── scripts/
    ├── snapshot_db_storage.py
    └── validate_sqlite_tree.py
```

- `SKILL.md`：Skill 入口、授权边界和执行路由。
- `references/windows-v4-workflow.md`：Windows 微信 4.x 的完整导出流程。
- `scripts/snapshot_db_storage.py`：创建并验证稳定的数据库目录快照。
- `scripts/validate_sqlite_tree.py`：批量执行 SQLite 完整性检查。
- `agents/openai.yaml`：Codex 中显示的名称、简介和默认提示。

## 隐私与安全

请勿向本仓库提交以下内容：

- 微信聊天记录、联系人信息或媒体文件。
- 原始或解密后的微信数据库及 WAL/SHM 文件。
- 数据库密钥、DPAPI 保护文件或 Hook 捕获产物。
- 微信账号目录、本机日志、导出结果或临时工作目录。
- 包含真实账号、联系人或本机绝对路径的测试材料。

仓库提供的 `.gitignore` 会拦截常见数据库、密钥、临时目录和导出目录，但它不能代替提交前的人工检查。

## Hook 说明

本仓库不捆绑 Hook 二进制文件，也不固化特定微信版本的偏移。微信小版本更新可能改变内存布局，执行前必须重新确认精确版本、审计所使用的实现，并取得用户的明确授权。

## 校验

创建或修改 Skill 后，可以使用 Codex 自带的 Skill 校验工具检查目录结构和元数据；两个 Python 脚本也都提供 `--help` 参数。数据库验证脚本以只读方式打开 SQLite 数据库，并可输出 JSON 检查报告。

## 许可

当前仓库暂未附加开源许可证。未经版权所有者明确许可，不代表允许复制、再发布或用于商业用途。
