"use strict";
const scenes = {
  silence: {
    id: "01",
    question: "“消息一直没回，是不是不喜欢我了？”",
    observation: "没回消息是事实，“不喜欢我”还只是猜测。先看上一段聊了什么，以及有没有必须处理的事；不急着用反复追问换取确定感。",
    reply: "“想确认一下周末的安排。你方便时告诉我就好，如果还没确定，也可以直接说。”",
    note: "没有待确认的事情时，也可以先不追发，留一点空间。"
  },
  needs: {
    id: "02",
    question: "“我们想亲近的频率不一样，怎么开口才不会变成压力？”",
    observation: "需求不同不等于谁有问题，也不证明谁更爱谁。先谈自己的感受，再邀请对方表达；性别不决定谁应该主动或配合。",
    reply: "“我有点想念我们亲近的感觉，也不希望你勉强。你愿意聊聊最近的状态吗？现在不想谈也可以。”",
    note: "寻找双方都愿意的相处方式，而不是劝其中一方接受。"
  },
  boundary: {
    id: "03",
    question: "“我今晚想自己待着，又怕对方觉得我不在乎。”",
    observation: "需要独处与在乎对方可以同时存在。可以表达关心，也清楚说明这次的边界；不必靠勉强自己来证明感情。",
    reply: "“我在乎你，不过今晚需要自己休息一下。我们明天再聊，好吗？”",
    note: "后续时间只在你确实愿意时提出；对方失望也不代表你的边界无效。"
  }
};
document.querySelectorAll("[data-scene]").forEach(button => {
  button.addEventListener("click", () => {
    const scene = scenes[button.dataset.scene];
    document.querySelectorAll("[data-scene]").forEach(item => {
      const active = item === button;
      item.classList.toggle("active", active);
      item.setAttribute("aria-pressed", String(active));
    });
    for (const key of ["id", "question", "observation", "reply", "note"]) {
      document.getElementById(`scene-${key}`).textContent = scene[key];
    }
  });
});
document.getElementById("copy-command").addEventListener("click", async () => {
  const status = document.getElementById("copy-status");
  try {
    await navigator.clipboard.writeText(document.getElementById("install-command").textContent);
    status.textContent = "已复制。导入技能后，在聊天工具中粘贴即可。";
  } catch {
    status.textContent = "浏览器未允许复制，请选中上方文字手动复制。";
  }
});
