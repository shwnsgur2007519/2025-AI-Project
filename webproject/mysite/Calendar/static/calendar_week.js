
// ✅ 필터 상태 읽기
function getFilterSettings() {
  return {
    showDone: document.getElementById("showDone").checked,
    showDeadline: document.getElementById("showDeadline").checked,
    showStart: document.getElementById("showStart").checked,
  };
}

// ✅ 일정 표시 여부 판단
function shouldShow(item, settings) {
  const isDone = item.is_done;
  const type = item.type;
  if (type === "deadline") {
    return settings.showDeadline && (!isDone || (isDone && settings.showDone));
  }
  if (type === "start_time") {
    return settings.showStart && (!isDone || (isDone && settings.showDone));
  }
  return false;
}

// ✅ 일정 모두 제거
function clearWeekSchedule() {
  for (const day in scheduleData) {
    scheduleData[day].forEach(item => {
      const dt = item.type === "start_time" ? item.start_time : item.deadline;
      const dateObj = new Date(dt);
      const hour = dateObj.getHours().toString().padStart(2, '0');
      const cellId = `cell-${day}-${hour}`;
      const cell = document.getElementById(cellId);
      if (cell) cell.innerHTML = "";
    });
  }
}

// ✅ 일정 렌더링
function renderWeekSchedule() {
  const settings = getFilterSettings();

  for (const day in scheduleData) {
    scheduleData[day].forEach(item => {
      if (!shouldShow(item, settings)) return;

      const dt = item.type === "start_time" ? item.start_time : item.deadline;
      const dateObj = new Date(dt);
      const hour = dateObj.getHours().toString().padStart(2, '0');
      const cellId = `cell-${day}-${hour}`;
      const cell = document.getElementById(cellId);
      if (!cell) return;

      const div = document.createElement("div");
      div.className = "text-white rounded px-1 py-1 small text-truncate w-100 my-1";
      div.style.backgroundColor = item.type === "start_time" ? (item.is_done === true ? "#4677be" :"#0d6efd") : item.color;
      div.textContent = item.type === "start_time" ? `✓ ${item.task_name}` : item.task_name;

      div.setAttribute("role", "button");
      div.setAttribute("onclick", "openTaskDetail(this)");
      div.dataset.id = item.id;
      div.dataset.task = item.task_name;
      div.dataset.subject = item.subject;
      div.dataset.deadline = item.deadline;
      div.dataset.fixed = item.is_fixed;
      div.dataset.exam = item.is_exam_task;
      div.dataset.owner = item.owner_id;
      div.dataset.done = item.is_done;

      cell.appendChild(div);
    });
  }
}

// ✅ 일정 상세 보기
function openTaskDetail(el) {
  document.getElementById("taskDetailModalLabel").textContent = el.dataset.task;
  document.getElementById("detailSubject").textContent = el.dataset.subject || '없음';
  document.getElementById("detailDeadline").textContent = el.dataset.deadline || '없음';
  document.getElementById("detailFixed").textContent = el.dataset.fixed === "true" ? "예" : "아니오";
  document.getElementById("detailExam").textContent = el.dataset.exam === "true" ? "예" : "아니오";

  const id = el.dataset.id;
  const editLink = document.getElementById("editTaskLink");
  editLink.href = `/calendar/schedule/${id}/edit/?next=${encodeURIComponent(window.location.pathname + window.location.search)}`;

  const isDone = el.dataset.done === "true";
  
  const doneBtn = document.getElementById("markDoneBtn");
  const undoneBtn = document.getElementById("unmarkDoneBtn");

  if (isDone) {
    doneBtn.classList.add("d-none");
    undoneBtn.classList.remove("d-none");
  } else {
    doneBtn.classList.remove("d-none");
    undoneBtn.classList.add("d-none");
  }

  const modal = new bootstrap.Modal(document.getElementById('taskDetailModal'));
  modal.show();
}

function reload(){
    clearWeekSchedule();
    renderWeekSchedule();
}

// ✅ 초기화 및 이벤트 연결
document.addEventListener("DOMContentLoaded", () => {
  renderWeekSchedule();

  ["showDone", "showDeadline", "showStart"].forEach(id => {
    document.getElementById(id).addEventListener("change", () => {
        reload();
    });
  });
});
