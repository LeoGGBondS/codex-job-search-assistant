# Codex Job Search Assistant

用 Codex 做自己的求职助手：首次问答建档、寻找合适的 JD、轻量修改简历、执行授权的申请，并自动维护投递文档。

这是一个可复用的 **Codex skill + 本地记录工具**。无需为记录工具配置模型 API key，也没有内置候选人资料。Codex 本身的账户/使用条件，以及搜索、浏览器和自动化工具需由使用者自己的环境提供。

## 开始使用

1. 下载本仓库 ZIP 并解压，或 clone 到本地。
2. 在 Codex 中打开该文件夹，确认它是当前工作目录。
3. 发一句：**“帮我初始化求职助手。”** 或 **“Use $job-search-assistant to get started.”**
4. 助手会分批询问你的简历、目标职位、地点、毕业/入职时间、工作授权等；已有信息不会反复问。缺少信息可以先留空。
5. 可以先给一个 JD 测试，也可以让助手开始找岗。需要定时运行时，再告诉它时间、时区和每日上限。

下载本身不会弹出问卷或自动提交。首次在 Codex 中开始对话后，仓库的 AGENTS.md 和 `.agents/skills/job-search-assistant/` 引导助手完成建档；skill 的加载方式以 [Codex 官方说明](https://learn.chatgpt.com/docs/build-skills) 为准。如果没有自动选中，可明确输入 `$job-search-assistant`。

## 它能做什么

- 从你的求职偏好寻找公开招聘信息，读取完整 JD 后筛选，分清硬条件、加分项和未知项。
- 默认沿用现有简历；必要时只改少量措辞或顺序，不要求每个岗位重写。
- 使用你自己的 Codex 可用浏览器工具填写和提交已授权的申请。没有浏览器工具时准备待投队列并说明限制。
- 保存岗位、状态、提交时间、实际简历版本、确认凭证及待处理问题，生成 `outputs/applications.md`。
- 在支持 Automations 的环境中，按你的请求创建定时任务；仓库本身不内置或启动调度器。

不能保证任意网站、任意验证码或任意账户流程都能无人值守完成。LinkedIn 自动抓取/站内自动操作不在此工作流内，可使用其 JD 文本及雇主官网链接。新公司首次接收个人信息、验证码或法律条款等，按实际工具要求取得确认/交接；不会因为“自动投递”就绕过这些步骤。每日上限是上限，不保证每天投满。

## 个人资料留在本地

| 位置 | 内容 | 默认上传 GitHub？ |
|---|---|---|
| `personal/` | 简历、个人资料、经历库、授权记录、原始投递记录 | 否 |
| `outputs/` | 投递文档、岗位材料和成功截图 | 否 |
| `work/` | 临时输入与中间文件 | 否 |
| `.agents/`、`scripts/`、`tests/` | 通用流程和记录工具 | 是 |

`.gitignore` 防止正常提交时误带这些目录，但不防强制添加、第三方同步或已被提交的文件。公开前运行检查，检查暂存文件，不要强制添加个人资料。向招聘公司发送资料会走该公司的申请系统；“本地保存”不意味着申请时不会发送给雇主。

## 可选：本地记录工具

需要 Python 3.10+。日常可让 Codex 执行，无需自己输入命令。Windows 如缺少 IANA 时区库，运行 `python -m pip install -r requirements.txt`；Codex 的捆绑 Python 也可使用。

```sh
python scripts/job_assistant.py init
python scripts/job_assistant.py status
python scripts/job_assistant.py record --file work/candidate.json
python scripts/job_assistant.py gate --file work/candidate.json
python scripts/job_assistant.py render
python -m unittest discover -s tests -v
python scripts/check_public.py
```

这些命令管理本地资料、去重、每日上限和文档，**不自行搜索或提交网页**。网页操作由可用 Codex 工具执行。`gate` 不是招聘资格、授权或网站合规检查器；它仅检查本地状态及额度。只支持一个顺序运行的投递执行者，不要并发启动多个提交进程。

`record` 输入示例见 [examples/candidate.json](examples/candidate.json)。示例均为虚构数据，不是已投递记录。真实输入存放到 `work/`。正式提交记录必须有带时区的 submitted_at 和明确 submission_evidence；结果不明须用 submission_unknown，不能自动重投。

## English quick start

Open this downloaded repository as your Codex workspace and say “Use $job-search-assistant to get started.” The assistant asks for your own resume and preferences, then prepares a local profile. Search/browser/scheduler capabilities come from your Codex environment, not the Python helper. Candidate data and outputs are ignored by Git. Submission confirmations, site rules, accurate eligibility answers, and uncertainty handling still apply. No personal data from the publisher is included.

MIT licensed. Contributions should contain only reusable code, documentation, and synthetic test fixtures.
