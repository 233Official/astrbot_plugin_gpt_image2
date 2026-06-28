# GPT Image2 绘图插件使用说明

当用户想让 Bot 生成图片、编辑图片、基于参考图重新绘制，或想先通过多轮对话整理生图提示词时，使用本插件能力。

---

## 插件能力

- 通过 OpenAI 兼容 Images API 或 Responses API 生成图片。
- `/image2 draw` 统一处理文生图和图生图：消息无图时文生图，当前消息或引用消息带图时自动走图生图/编辑。
- `/image2 edit` 显式图片编辑，适合用户明确要求“修改这张图”“把图里的 X 改成 Y”。
- `/image2 plan` 提供多轮图文设计会话，先澄清需求和整理提示词，再由用户确认生成。
- 支持主站、普通备用站点、权威兜底站点和自适应站点优先级。
- 管理员可查看站点健康、费用、余额、失败统计和诊断包。
- 支持配置 `draw_aliases`，用自定义前缀触发统一绘图入口。

---

## 用户可用命令

### 生成图片

```text
/image2 draw <提示词>
```

说明：

- 当前消息和引用消息都没有图片时，按提示词文生图。
- 当前消息附带图片，或回复/引用一条带图消息时，会自动使用这些图片作为参考图进行图生图/编辑。
- 用户说“画一张……”“生成……图片”“用这张图改成……”时，可以引导使用 `/image2 draw <提示词>`。

示例：

```text
/image2 draw 一只白色小猫，水彩风格，柔和光线
```

### 显式图片编辑

```text
/image2 edit <提示词>
```

说明：

- 必须在当前消息附带图片，或引用/回复带图消息。
- 适合用户明确要求编辑现有图片，而不是从零生成。

示例：

```text
/image2 edit 保留主体姿势，把背景改成夜晚赛博朋克街道
```

### Plan 多轮设计会话

```text
/image2 plan
/plan <描述>
/plan confirm
/plan retry
/plan quit
```

说明：

- `/image2 plan` 进入多轮图文设计会话。
- 进入 Plan 后，可继续用 `/plan <描述>` 补充需求；群聊普通消息不会被无条件拦截。
- 可以在 Plan 会话中附带或引用参考图。
- `/plan confirm` 使用当前整理好的提示词确认生成。
- `/plan retry` 重试上一条失败的 Plan 输入。
- `/plan quit` 退出当前 Plan 会话。
- 也支持 `/image2 plan confirm`、`/image2 plan retry`、`/image2 plan quit`。

当用户只给出模糊想法，例如“帮我想一张头像”“我想做一张海报但还没想清楚”，优先建议使用 `/image2 plan`。

### 查看帮助和状态

```text
/image2 help
/image2 status
```

- `/image2 help` 显示插件内帮助、当前配置摘要和可用命令。
- `/image2 status` 查看当前群/会话 Image2 开关状态。

---

## 管理员命令

以下命令通常需要管理员权限：

```text
/image2 on
/image2 off
/image2 mode [images|responses]
/image2 guard [images|responses|all] [on|off]
/image2 retry [global|here|interval] ...
/image2 providers
/image2 balance
/image2 balance set <Provider> <amount>
/image2 costs
/image2 costs recent [N]
/image2 stats
/image2 stats recent [N]
/image2 diag
```

说明：

- `/image2 on` / `/image2 off` 启用或关闭当前群/会话 Image2，默认开启。
- `/image2 mode` 查看或切换全局 API 模式，会影响 draw/edit 的站点过滤。
- `/image2 guard` 查看或切换 Prompt Guard。
- `/image2 retry` 查看或切换备用站点重试提示。
- `/image2 providers` 查看站点顺序、能力、健康、URL 展示策略、余额缓存和
  固定参考成本。
- `/image2 balance` 实时查询已配置余额接口的站点余额。
- `/image2 balance set <Provider> <amount>` 手动设置余额锚点，适合无法实时查询余额的站点。
- `/image2 costs` 和 `/image2 costs recent [N]` 查看费用统计和最近费用事件。
- `/image2 stats` 和 `/image2 stats recent [N]` 查看 Provider 统计、失败原因和最近失败记录。
- `/image2 diag` 生成诊断包，用于排查站点配置、请求失败和统计异常。

---

## 回复建议

用户说“帮我画一张猫猫图”：

```text
可以发送「/image2 draw 一只白色小猫，水彩风格，柔和光线」。
```

用户发图并说“把背景改掉”：

```text
可以回复这张图发送「/image2 edit 把背景改成夜晚赛博朋克街道，保留主体不变」。
```

用户想法很模糊：

```text
可以先发送「/image2 plan」进入多轮设计，我会帮你整理画面、风格和最终提示词，确认后再生成。
```

用户问为什么生成失败：

```text
可以先让管理员查看「/image2 providers」和「/image2 stats recent 5」。如果需要诊断包，可执行「/image2 diag」。
```

用户问怎么查看余额或费用：

```text
管理员可以发送「/image2 balance」「/image2 costs」或「/image2 stats」。无法实时查余额的站点可用「/image2 balance set <Provider> <amount>」设置手动锚点估算。
```

---

## 注意事项

- API Key、Provider 配置和余额接口凭据只应由管理员在 WebUI 配置，不要让用户在群聊里公开发送。
- `base_url` 应填写 OpenAI 兼容 API 根路径，例如 `https://api.example.com/v1`，不要包含 `images/generations`。
- 如果用户需要编辑图片，必须附带图片或引用带图消息。
- 如果用户想用普通自然语言慢慢讨论图片方案，优先建议 `/image2 plan`，不要直接猜测最终提示词。
- 如果当前群/会话被 `/image2 off` 关闭，应让管理员执行 `/image2 on` 恢复。
- 如果上游或平台发送图片失败，可让管理员查看 `/image2 stats recent [N]`、`/image2 providers` 和 `/image2 diag`。

---

## 当前未实现或不应承诺的能力

- 不承诺支持遮罩局部重绘，除非后续版本明确实现。
- 不承诺支持异步任务提交与轮询。
- 不承诺自动读取或修改 WebUI 配置；配置变更应由管理员完成。
- 不承诺所有 Provider 都支持相同模式、尺寸、质量、数量或图像编辑能力，应以 `/image2 providers` 和当前配置为准。

---

## 维护要求

每次插件新增、删除或修改用户可感知功能时，维护者必须同步更新：

- `README.md`
- `CHANGELOG.md`
- `skills/SKILL.md`

`skills/SKILL.md` 面向 AstrBot LLM 上下文，重点写清插件能做什么、用户怎么触发、管理员如何排障，以及哪些能力尚未实现。
