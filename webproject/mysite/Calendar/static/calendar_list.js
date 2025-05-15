document.addEventListener('keydown', function (event) {
  const path = window.location.pathname;

  // 주간 보기: /calendar/week/
  if (path.includes('/week/')) {
    if (event.key === 'ArrowLeft') {
      window.location.href = '?date=' + window.prev_date;
    } else if (event.key === 'ArrowRight') {
      window.location.href = '?date=' + window.next_date;
    }

  // 월간 보기: /calendar/ 또는 /calendar/index/
  } else if (path === '/calendar/' || path.includes('/calendar/index')) {
    console.log(window.prev_year, window.prev_month)
    if (event.key === 'ArrowLeft') {
      window.location.href = '?year=' + window.prev_year + '&month=' + window.prev_month;
    } else if (event.key === 'ArrowRight') {
      window.location.href = '?year=' + window.next_year + '&month=' + window.next_month;
    }
  }
});


function openScheduleModal(el) {
  const day = el.getAttribute('data-day');
  const listEl = document.getElementById('scheduleModalList');
  listEl.innerHTML = '';

  if (window.scheduleData && scheduleData[day]) {
    scheduleData[day].forEach(item => {
      const li = document.createElement('li');
      li.className = 'list-group-item';
      li.role = 'button';
      li.textContent = item.task_name;
      li.style.backgroundColor = item.color;
      li.style.webkitTextFillColor = 'white';

      // ✨ data-* 속성 추가
      li.dataset.task = item.task_name;
      li.dataset.subject = item.subject;
      li.dataset.deadline = item.deadline;
      li.dataset.fixed = item.is_fixed;
      li.dataset.exam = item.is_exam_task;
      li.dataset.id = item.id;
      li.dataset.owner = item.owner_id;

      li.onclick = () => openTaskDetail(li);
      listEl.appendChild(li);
    });
  }

  const modal = new bootstrap.Modal(document.getElementById('scheduleModal'));  
  // modal.classList.add()
  modal.show();
}


function openTaskDetail(el) {
  document.getElementById("taskDetailModalLabel").textContent = el.dataset.task;
  document.getElementById("detailSubject").textContent = el.dataset.subject || '없음';
  document.getElementById("detailDeadline").textContent = el.dataset.deadline || '없음';
  document.getElementById("detailFixed").textContent = el.dataset.fixed === "true" ? "예" : "아니오";
  document.getElementById("detailExam").textContent = el.dataset.exam === "true" ? "예" : "아니오";

  //수정 링크 설정

  const id = el.dataset.id;
    const editLink = document.getElementById("editTaskLink");
    editLink.href = `/calendar/schedule/${id}/edit/?next=${encodeURIComponent(window.location.pathname + window.location.search)}`;

  // 소유자 비교 후 수정 버튼 보이기/숨기기
  const ownerId = parseInt(el.dataset.owner);
  
  if (window.currentUserId === ownerId) {
    editLink.classList.remove("d-none");
  } else {
    editLink.classList.add("d-none");
  }

  const modal = new bootstrap.Modal(document.getElementById('taskDetailModal'));
  modal.show();
}



function updateVisibility() {
  const showDone = document.getElementById("showDone").checked;
  const showDeadline = document.getElementById("showDeadline").checked;
  const showStart = document.getElementById("showStart").checked;

  document.querySelectorAll("[data-type='deadline']").forEach(el => {
    const isDone = el.dataset.done === "true";

    // 마감일이면서 완료된 일정인 경우 → showDone도 켜져야 함
    const shouldShow = showDeadline && (!isDone || (isDone && showDone));
    el.style.display = shouldShow ? "" : "none";
  });

  document.querySelectorAll("[data-type='start_time']").forEach(el => {
    // 시행일은 완료 여부 관계없이 showStart만 따름
    el.style.display = showStart ? "" : "none";
  });
}

["showDone", "showDeadline", "showStart"].forEach(id => {
  document.getElementById(id).addEventListener("change", updateVisibility);
});

document.addEventListener("DOMContentLoaded", updateVisibility);
