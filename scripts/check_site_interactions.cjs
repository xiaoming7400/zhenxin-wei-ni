"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

// 最小 DOM 替身只验证事件逻辑；布局和键盘行为仍需浏览器验收。
function element(dataset = {}) {
  return {
    dataset, textContent: "", attributes: {}, events: {},
    classList: { toggle() {} },
    setAttribute(key, value) { this.attributes[key] = value; },
    addEventListener(event, callback) { this.events[event] = callback; }
  };
}
const root = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(root, "docs/index.html"), "utf8");
const ids = new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(match => [match[1], element()]));
const fields = ["rest", "connect"].map(field => element({ field }));
const scenes = ["silence", "needs", "boundary"].map(scene => element({ scene }));
const command = "使用 $female-intimacy-coach，帮我复盘这段聊天。";
ids.get("install-command").textContent = command;
let copied;
const navigator = { clipboard: { async writeText(value) { copied = value; } } };
vm.runInNewContext(fs.readFileSync(path.join(root, "docs/assets/site.js"), "utf8"), {
  document: {
    querySelectorAll(selector) {
      if (selector === "[data-field]") return fields;
      if (selector === "[data-scene]") return scenes;
      throw new Error(`未知选择器：${selector}`);
    },
    getElementById(id) { assert.ok(ids.has(id), `缺少页面元素：${id}`); return ids.get(id); }
  }, navigator
});
async function main() {
  for (const selected of [fields[1], fields[0], fields[1]]) {
    selected.events.click();
    assert.equal(ids.get("field-display").dataset.mode, selected.dataset.field);
    assert.match(ids.get("field-state").textContent, /边界保留/);
    assert.match(ids.get("field-display").attributes["aria-label"], /完整/);
    assert.ok(ids.get("field-message").textContent.length > 10);
    for (const button of fields) assert.equal(button.attributes["aria-pressed"], String(button === selected));
  }
  for (const [index, selected] of scenes.entries()) {
    selected.events.click();
    assert.equal(ids.get("scene-id").textContent, `0${index + 1}`);
    for (const key of ["question", "observation", "reply", "note"]) assert.ok(ids.get(`scene-${key}`).textContent.length > 0);
    for (const button of scenes) assert.equal(button.attributes["aria-pressed"], String(button === selected));
  }
  await ids.get("copy-command").events.click();
  assert.equal(copied, command);
  assert.match(ids.get("copy-status").textContent, /已复制/);
  navigator.clipboard.writeText = async () => { throw new Error("拒绝权限"); };
  await ids.get("copy-command").events.click();
  assert.match(ids.get("copy-status").textContent, /手动复制/);
  console.log("PASS: 心之壁往返切换、无障碍状态、三个沟通场景、复制成功与失败提示");
}
main().catch(error => { console.error(error); process.exitCode = 1; });
