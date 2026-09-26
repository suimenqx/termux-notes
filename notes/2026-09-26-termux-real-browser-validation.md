# 在 Termux 中验证网页前端的真实浏览器效果（2026-09-26）

## 适用范围与结论

手机可以是**开发主机**，被开发的产品仍可能面向电脑。先确认项目的目标平台，再选浏览器和视口。对于以桌面浏览器为目标、但在 Android/Termux 中开发的项目，本机已跑通的组合是：

| 组件 | 职责 |
| --- | --- |
| 项目的静态文件或本地 HTTP 开发服务器 | 提供待测页面 |
| Termux 版 Firefox | 执行真实 DOM、CSS、浏览器 API 与下载行为 |
| Xvfb | 提供无需额外 Android 图形界面的虚拟桌面显示 |
| geckodriver | 通过标准 WebDriver 控制 Firefox、取得页面状态和截图 |
| 项目已有的桌面 CI | 补充 Chromium 等目标引擎的回归测试 |

这不是一个新的 Web 服务，也不是 Android 系统浏览器。`file://` 可以测试单文件离线发布物；需要 HTTP、模块加载或路由的项目应启动其本地服务器。HDB、ADB、Playwright 和 Termux:X11 均不是上述自动化路径的必要条件。Termux:X11 只在需要人眼实时操作 Firefox 窗口时作为可选图形界面。

### 实测基线

2026-09-26 在华为 Mate 60 Pro+（HarmonyOS 4.2、Android API 31、ARM64）上使用 Termux Firefox 156.0.1、geckodriver 0.37.1 和 Xvfb 21.1.16-3。用 WebDriver 打开 `offline-table-analyzer/index.html` 的 `file://` 地址，设置 1440×900 浏览器窗口，页面视口为 1440×815；点击“加载示例”后得到 3 张表、12 行并取得真实截图。同一烟测也通过了 `http://127.0.0.1:4173/index.html` 本地服务入口。另用页面控件筛选数据、导出 XLSX，再用独立读取器确认文件内容。Firefox 在本机无需关闭内容沙箱。

版本和尺寸只是一次实测记录。后续 agent 应记录自己的浏览器版本、`innerWidth`、`innerHeight`、目标 URL 和验证结果。

## 1. 先确定要证明什么

1. 阅读项目的目标平台、启动脚本、发布方式和现有测试。按**产品目标平台**选桌面或移动视口，不按开发设备选。
2. 确认入口：单文件离线应用优先直接打开最终 HTML；需要开发服务器的应用使用 `http://127.0.0.1:<port>/`。需要验证生产构建时，应指向生产构建产物，而非仅开发服务器。
3. 选一条真实用户流程，写出可观察的预期：例如导入 → 解析 → 筛选 → 导出。至少检查 DOM 结果和浏览器截图；导出类功能还要读回文件。
4. 标明本机 Firefox 验证覆盖的范围，并查阅 CI 是否提供目标 Chromium、WebKit 或其他浏览器引擎的覆盖。

## 2. 安装与检查

在 Termux 中安装 X11 仓库及工具：

```sh
pkg install x11-repo
pkg install firefox geckodriver xorg-server-xvfb
firefox --version
geckodriver --version
command -v Xvfb
```

如果已有旧镜像导致依赖版本不匹配，先用 `termux-change-repo` 为 main 与 x11 **同时**选择更新及时的镜像，再刷新软件包索引。曾遇到旧镜像的 Firefox 109 与本机新 `glib-bin` 无法匹配；切换到 Termux 官方 main/X11 源后安装成功。参考 [Termux 镜像清单](https://github.com/termux/termux-packages/wiki/Mirrors)。不要用修改 CPU 架构或手工拼装旧版依赖来绕过这类错误。

在 Android 共享存储目录开发时，文件系统可能不支持 npm 创建符号链接。该项目若需要安装 Node 开发依赖，可尝试 `npm ci --bin-links=false`，并用 `node node_modules/<package>/...` 调用本来依赖 `node_modules/.bin` 的命令。依赖安装策略以所在项目为准。

## 3. 启动浏览器服务

在同一 Termux shell 中运行，保持两个进程直到验证完成：

```sh
Xvfb :99 -screen 0 1600x1000x24 -nolisten tcp >"$PREFIX/tmp/web-xvfb.log" 2>&1 &
web_xvfb_pid=$!
DISPLAY=:99 geckodriver --port 4444 >"$PREFIX/tmp/web-geckodriver.log" 2>&1 &
web_gecko_pid=$!
curl --fail --silent http://127.0.0.1:4444/status
```

`curl` 应返回 `ready: true`。`4444` 是 geckodriver 的本机控制端口，不是项目的 Web 服务器端口。Xvfb 的 1600×1000 是可用显示区域，不等于页面 CSS 视口；验证脚本应主动设置浏览器窗口并读取 `innerWidth`/`innerHeight`。若端口或显示号被占用，改用空闲值并同步更新脚本。`xkbcomp` 的部分键位警告通常不会妨碍显示服务启动，应以实际 WebDriver 会话是否成功判断。

如果项目需要 HTTP，另开一个 Termux 会话启动**项目自己的**服务器，例如 `npm run dev -- --host 127.0.0.1`，先用 `curl -I http://127.0.0.1:<port>/` 确认页面可达。不要将服务监听到公网接口，除非测试场景明确要求。

## 4. 用 WebDriver 做一次可复制的验证

从项目根目录运行下例。`TARGET_PAGE` 可以是 HTML 文件路径、`file://` 地址或本地 HTTP URL；文件路径会被转换成正确的 `file://` URL。这个通用烟测负责启动会话、检查页面加载、获取桌面视口和截图。随后按项目流程补充点击、键盘输入、上传、下载及断言。

```sh
TARGET_PAGE="/absolute/path/to/index.html" node <<'NODE'
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const endpoint = 'http://127.0.0.1:4444';
const input = process.env.TARGET_PAGE;
if (!input) throw new Error('Set TARGET_PAGE to a file path or local URL');
const url = /^(https?:|file:)/.test(input) ? input : pathToFileURL(path.resolve(input)).href;

async function wd(method, route, body) {
  const response = await fetch(endpoint + route, {
    method,
    headers: { 'content-type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok || result.value?.error) throw new Error(JSON.stringify(result.value));
  return result.value;
}

(async () => {
  const { sessionId, capabilities } = await wd('POST', '/session', {
    capabilities: { alwaysMatch: { browserName: 'firefox' } },
  });
  const session = `/session/${sessionId}`;
  try {
    await wd('POST', `${session}/window/rect`, { width: 1440, height: 900 });
    await wd('POST', `${session}/url`, { url });
    const state = await wd('POST', `${session}/execute/sync`, {
      script: 'return {url: location.href, title: document.title, readyState: document.readyState, width: innerWidth, height: innerHeight, hasBody: !!document.body}',
      args: [],
    });
    assert.equal(state.readyState, 'complete');
    assert.equal(state.hasBody, true);
    assert.ok(state.width >= 1100, `unexpected desktop viewport: ${state.width}`);
    const png = await wd('GET', `${session}/screenshot`);
    const artifactDir = fs.mkdtempSync(path.join(process.env.PREFIX, 'tmp', 'web-smoke-'));
    const output = path.join(artifactDir, 'page.png');
    fs.writeFileSync(output, Buffer.from(png, 'base64'));
    console.log({ ...state, browser: capabilities.browserName,
      browserVersion: capabilities.browserVersion, screenshot: output });
  } finally {
    await wd('DELETE', session);
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
NODE
```

截图保存在输出中列出的 Termux 私有临时目录。使用图像查看工具检查真实布局、裁切、遮挡、字体和可见状态。测试敏感应用时使用合成数据，不要把正文、截图或导出文件写入公共日志或公开仓库；验证后清理临时产物。不要仅凭 `readyState` 或截图存在就宣布功能通过。WebDriver 的标准接口与用法见 [Mozilla geckodriver 文档](https://firefox-source-docs.mozilla.org/testing/geckodriver/Usage.html)。

### 将烟测扩展成项目验证

在上述 `try` 中按页面语义控件操作，并在每一步断言可见结果。WebDriver 元素 ID 使用 `element-6066-11e4-a52e-4f735466cecf` 字段。例如：

```js
const element = await wd('POST', `${session}/element`, {
  using: 'css selector', value: '#sampleLink',
});
await wd('POST', `${session}/element/${element['element-6066-11e4-a52e-4f735466cecf']}/click`, {});
const tables = await wd('POST', `${session}/execute/sync`, {
  script: 'return document.querySelectorAll("#previewArea table").length', args: [],
});
assert.equal(tables, 3);
```

异步结果应使用有上限的轮询等待预期状态，不依赖固定长时间 `sleep`。表单要用 WebDriver 的输入操作；下载要检查实际文件，XLSX 用独立读取器读回。截图应在关键状态各保存一张，保留 URL、视口、浏览器版本、DOM 断言、文件读回结果和失败日志。

### 导出与文件读回

为每次测试建立独立下载目录，并在创建 WebDriver 会话时传入 Firefox 首选项。下面的下载设置已在上述设备上验证：

```js
const downloadDir = fs.mkdtempSync(path.join(process.env.PREFIX, 'tmp', 'web-download-'));
const { sessionId } = await wd('POST', '/session', {
  capabilities: { alwaysMatch: {
    browserName: 'firefox',
    'moz:firefoxOptions': { prefs: {
      'browser.download.folderList': 2,
      'browser.download.dir': downloadDir,
      'browser.download.useDownloadDir': true,
      'browser.helperApps.neverAsk.saveToDisk': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    } },
  } },
});
```

点击页面的导出控件后，以有上限的轮询等待目录内出现完成的 `.xlsx` 文件；再用项目开发依赖中的独立读取器检查工作表名、表头、行数和关键值。本次实测下载了三个工作表，并由 `read-excel-file/node` 成功读回。不要仅凭“按钮可点击”或文件扩展名判断导出正确。

### 收尾

浏览器会话由示例脚本在 `finally` 中关闭。验证完毕后，在启动服务的 shell 中停止后台进程：

```sh
kill "$web_gecko_pid" "$web_xvfb_pid"
```

## 覆盖边界与故障处理

| 现象或问题 | 处理 |
| --- | --- |
| Playwright 在 Termux 报 `Unsupported platform: android` | 本机改用 Firefox + WebDriver；在受支持的桌面 CI 上保留 Playwright/Chromium。 |
| 依赖版本冲突，例如旧 Firefox 需要旧 `glib-bin` | 检查 main 和 x11 镜像时间与来源，换到当前官方镜像后再安装。 |
| `geckodriver` 连接失败 | 查看两个日志、`/status`、端口占用和 `DISPLAY=:99`。 |
| 浏览器无法启动 | 确认 Xvfb 正在运行、Firefox 与 geckodriver 已安装，并查看驱动日志；本机实测无需关闭 Firefox 内容沙箱。 |
| 截图像手机布局或被裁切 | 加大 Xvfb 屏幕，设置浏览器窗口，记录真实 `innerWidth`/`innerHeight`。 |
| `file://` 下模块或路由受限 | 按项目发布方式启本地 HTTP 服务器；离线单文件产品仍应另测 `file://`。 |
| 导出按钮点击后找不到文件 | 使用专用下载目录与 Firefox 下载首选项，等待文件写完，再以独立读取器验收。 |
| 浏览器渲染通过但目标是 Chrome/Edge/Safari | 继续运行对应桌面浏览器或 CI；本机 Firefox 结果只证明 Gecko。 |

对于面向 Android 浏览器/WebView 的产品，本方案只能作补充，不能代替真机浏览器及触控验收。对于面向桌面的产品，手机只是运行 Termux 的主机，重点应检查桌面视口与目标浏览器引擎，而非手机屏幕宽度。Termux 中的字体、窗口装饰和系统集成可能与目标 Windows/macOS/Linux 桌面不同；精确像素验收仍应在目标桌面系统上完成。

## 参考资料

- [Termux 包镜像与 X11 仓库](https://github.com/termux/termux-packages/wiki/Mirrors)
- [Mozilla geckodriver 使用说明](https://firefox-source-docs.mozilla.org/testing/geckodriver/Usage.html)
- [Termux:X11 官方说明（可选实时图形界面）](https://github.com/termux/termux-x11/blob/master/README.md)
- [华为 HDB 与 HiSuite 连接说明](https://consumer.huawei.com/cn/support/content/zh-cn16084837/)
