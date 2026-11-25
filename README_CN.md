# Codex Job Search Assistant

[English](README.md) | 简体中文

用 Codex 做自己的求职助手：首次问答建档、寻找合适的 JD、轻量修改简历、执行授权的申请，并自动维护投递文档。

这是一个可复用的 **Codex skill + 本地记录工具**。无需为记录工具配置模型 API key，也没有内置候选人资料。Codex 本身的账户/使用条件，以及搜索、浏览器和自动化工具需由使用者自己的环境提供。

## 开始使用

1. 下载本仓库 ZIP 并解压，或 clone 到本地。
2. 在 Codex 中打开该文件夹，确认它是当前工作目录。
3. 发一句：**“帮我初始化求职助手。”**（中文）或 **“Initialize my job assistant.”**（English）。也可明确调用 `$job-search-assistant`。
4. 助手先确认中文/英文输出和普通/精准投递模式，再分批询问简历、目标职位、地点、毕业/入职时间、工作授权等。支持多页简历和多份源文件；已有信息不会反复问。
5. 首次生成的记录默认放到你实际桌面的 `Codex Job Search` 文件夹；以后更新同一个目录。设置每日运行时间、时区和上限后，每日自动运行会刷新总记录和当天的日期记录。没有调度能力时可手动运行，不能把下载等同于已启用自动化。

下载本身不会弹出问卷或自动提交。首次在 Codex 中开始对话后，仓库的 AGENTS.md 和 `.agents/skills/job-search-assistant/` 引导助手完成建档；skill 的加载方式以 [Codex 官方说明](https://learn.chatgpt.com/docs/build-skills) 为准。如果没有自动选中，可明确输入 `$job-search-assistant`。

## 它能做什么

- 从你的求职偏好寻找公开招聘信息，读取完整 JD 后筛选，分清硬条件、加分项和未知项。
- **普通 / General**：沿用现有简历，必要时小改。**精准 / Precise**：读取多页来源，针对 JD 生成一页、便于 ATS 解析的简历，检查真实页数、可读性和文字顺序。不会编造经历，也不承诺 ATS 分数。
- 使用你自己的 Codex 可用浏览器工具填写和提交已授权的申请。没有浏览器工具时准备待投队列并说明限制。
- 保存岗位、状态、提交时间、实际简历版本、确认凭证及待处理问题，生成桌面总记录 `applications.md` 和 `daily/YYYY-MM-DD.md`，状态与说明按所选语言输出。
- 在支持 Automations 的环境中，按你的请求创建定时任务；仓库本身不内置或启动调度器。

不能保证任意网站、任意验证码或任意账户流程都能无人值守完成。LinkedIn 自动抓取/站内自动操作不在此工作流内，可使用其 JD 文本及雇主官网链接。新公司首次接收个人信息、验证码或法律条款等，按实际工具要求取得确认/交接；不会因为“自动投递”就绕过这些步骤。每日上限是上限，不保证每天投满。

## 个人资料留在本地

| 位置 | 内容 | 默认上传 GitHub？ |
|---|---|---|
| `personal/` | 简历、个人资料、经历库、授权记录、原始投递记录 | 否 |
| 桌面 `Codex Job Search/` | 总记录、带日期的每日记录、按日期/编号分组的材料和截图 | 否（在仓库外） |
| `outputs/` | 旧安装或使用者明确选择的本地输出目录 | 否 |
| `work/` | 临时输入与中间文件 | 否 |
| `.agents/`、`scripts/`、`tests/` | 通用流程和记录工具 | 是 |

`.gitignore` 防止正常提交时误带这些目录，但不防强制添加、第三方同步或已被提交的文件。公开前运行检查，检查暂存文件，不要强制添加个人资料。向招聘公司发送资料会走该公司的申请系统；“本地保存”不意味着申请时不会发送给雇主。

## 可选：本地记录工具

需要 Python 3.10+。日常可让 Codex 执行，无需自己输入命令。Windows 如缺少 IANA 时区库，运行 `python -m pip install -r requirements.txt`；Codex 的捆绑 Python 也可使用。

```sh
python scripts/job_assistant.py init --message "帮我初始化求职助手"
python scripts/job_assistant.py configure --language zh --mode general --output-dir desktop
python scripts/job_assistant.py status
python scripts/job_assistant.py record --file work/candidate.json
python scripts/job_assistant.py gate --file work/candidate.json
python scripts/job_assistant.py render
python scripts/job_assistant.py lookup J0001
python scripts/job_assistant.py resume J0001 --material personal/transcript.pdf
python -m unittest discover -s tests -v
python scripts/check_public.py
```

这些命令管理本地资料、去重、每日上限和文档，**不自行搜索或提交网页**。网页操作由可用 Codex 工具执行。`gate` 不是招聘资格、授权或网站合规检查器；它仅检查本地状态及额度。只支持一个顺序运行的投递执行者，不要并发启动多个提交进程。

`record` 输入示例见 [examples/candidate.json](examples/candidate.json)。示例均为虚构数据，不是已投递记录。真实输入存放到 `work/`。正式提交记录必须有带时区的 submitted_at 和明确 submission_evidence；结果不明须用 submission_unknown，不能自动重投。

## 待处理岗位：用短编号继续

总记录中的每行有 `J0001` 这样的稳定编号。发送 **“继续 J0001”** 并附成绩单等所缺材料即可；英文可说 **“Resume J0001”**。原岗位链接也支持，但短编号通常比长链接占用更少上下文。助手只读取对应岗位、复核材料和仍开放的 JD，再补投；不会因为上传材料就重投已成功或结果不明的申请。

## 输出语言、目录与模式

- 中文初始化默认中文，英文初始化默认英文，也可以在首次问答明确选择，之后随时切换。申请材料遵循 JD 的语言，不必和记录语言相同。
- 新用户的桌面目录会先解析实际位置（包括系统重定向的桌面）；需要目录访问权限时按环境提示处理。找不到真实桌面时请选择明确路径。
- 同一个 `applications.md` 持续更新；`daily/YYYY-MM-DD.md` 按使用者时区标注日期，同一天刷新、旧日期保留。简历和凭证放在 `YYYY-MM-DD/J0001/`。
- 旧安装升级时保留原输出位置与历史；想切到桌面可让 Codex 执行 `configure --output-dir desktop`，未来文件写到新目录，不删除旧记录。
- 用 `configure --language zh --mode precise` 切换中文与精准模式；用 `--language en --mode general` 切回英文与普通模式。

精准模式依赖使用者环境里实际可用的文档/PDF工具：导出后必须检查一页、文字可选中、没有遮挡和缺字。记录工具本身不调用模型生成简历、不自带浏览器，也不绕过网站或 Codex 的权限规则。

## 许可证与贡献

采用 [MIT 许可证](LICENSE)。欢迎贡献通用代码、文档和虚构测试数据；不要提交真实求职者的简历、联系方式、授权记录或申请历史。

## 待处理、可选材料与邮箱追踪

每个未完成的投递都记录**原因、下一步、满足什么条件后再继续**，包括邮箱验证码、登录/CAPTCHA、缺成绩单或真实 GPA、未知必填问题、上传失败、工具不可用、网站错误、待授权以及其他未预见问题。可能已经提交但看不到回执时，记录为“结果待核实”并放在待处理区，先核实再决定，避免重复投递。验证码不写入记录。问题解决后用“继续 J0001”恢复对应申请，其他岗位可继续处理。

初始化时会提供两个**可跳过**的选项：补充成绩单等材料，以及连接 Gmail 或其他受支持邮箱。保存材料不代表允许向所有雇主发送；仅在相应申请需要且授权范围允许时使用。筛选会提前检查材料、硬性资格、发布时间和表单成本，优先处理匹配且能完成的申请。

**建议单独注册一个求职邮箱**，减少无关邮件带来的读取压力，也降低私人邮件暴露风险。不是强制。提供联系方式中的邮箱地址，不等于授权读取收件箱。只有明确选择启用，并完成当前环境实际可用的邮箱连接器授权后，才会读取约定范围内的求职邮件。按标签、雇主和时间筛选会减少实际读取内容，但不代表底层 OAuth 权限也被限制到该标签，请核对提供方真实授权页面。

邮箱已授权且工具可用时，助手整理回执、测评、面试、拒信、录用、截止时间及下一步，在已有求职记录中展示。无法明确对应岗位的邮件标为“待关联”，不会乱改申请状态。只保存必要摘要和邮件引用，不导出整个邮箱、不保存验证码。验证码协助需单独选择启用，仍遵守实际工具要求；需要本人操作时继续记入待处理。不会自动发送回复。

**不连接邮箱，就不提供邮件读取和追踪；找岗位、投递和手动更新照常使用。** 仓库不包含 Gmail OAuth 客户端、凭证或独立邮件读取器，需要 Codex 环境提供兼容连接器；没有工具时不会假装已连接。configure-email 只保存偏好，不完成授权。可用 `python scripts/job_assistant.py configure-email --disable` 关闭；撤销提供方访问权限需在其设置中完成，已有本地历史保留。

记录工具新增 block 保存具体阻塞、email-event 接收经过整理的最少邮件字段；仅凭邮件分类不会自动改成“已投递”或覆盖后续结果。具体流程见 [邮箱说明](.agents/skills/job-search-assistant/references/email.md) 和 [筛选清单](.agents/skills/job-search-assistant/references/screening.md)。筛选流程借鉴了 [ApplyPilot](https://github.com/yvonnehe772/applypilot) 的思路，不把这些通用做法宣称为独有功能。

## 岗位来源与公司偏好

初始化时会可选询问**公司阶段、人数规模、行业、目标公司与避开的公司**。例如早期 startup、成长型、成熟/上市公司，或“不限”；可以多选，之后随时更改。公司阶段与人数分开记录。“优先考虑”只影响排序，只有明确要求才作为硬性筛选；未知公司信息不会编造。老用户可以补充，不用重新初始化。

建议组合使用：**公司官网**核实当前 JD；**LinkedIn**找线索和设置提醒；**Greenhouse/MyGreenhouse、Lever、Ashby**查雇主岗位和申请；**Wellfound、YC Jobs**补充创业公司；**Handshake 或学校就业平台**找适合的实习与校招。Greenhouse 另有面向求职者的搜索/追踪入口 MyGreenhouse，Lever/Ashby 主要是雇主招聘系统。推荐来源不代表已安装接口或获准自动操作，也不代表自动获得邮箱或账号权限。当前流程不自动操作 LinkedIn 网站。官方链接与使用边界见 [岗位来源及公司筛选清单](.agents/skills/job-search-assistant/references/screening.md)。

## 初始化：地点、可工作时间与身份

首次设置会询问可工作的国家/城市（可选目标国家境内不限）、是否接受搬迁、remote/hybrid/in-person、最早入职和全职/兼职时间。可按需补充每周到岗天数限制、工时及实习时长；这些与助手每天几点运行分开记录。已有明确答案就复用：接受兼容地点的 in-person 和 relocation 时，不因普通的每周五天到岗问题反复卡住。

可以自愿提供所在国家的身份类别，例如 OPT/STEM OPT、H-1B、绿卡/永久居民、公民、其他或不披露；另外分别确认当前工作授权、现在及未来是否需要 sponsorship。不索取证件号码或照片。“已持有绿卡”和“是否另有正在办理的移民案件”分开记录，必要且未知的问题只问一次，并保存确认日期和适用上下文。
