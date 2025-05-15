["showDone", "showDeadline", "showStart"].forEach(id => {
  const checkbox = document.getElementById(id);

  checkbox.addEventListener("change", () => {
    localStorage.setItem(id, checkbox.checked);  // ✅ 상태 저장
    reload();
  });
});

function restoreCheckboxStates() {
  ["showDone", "showDeadline", "showStart"].forEach(id => {
    const saved = localStorage.getItem(id);
    if (saved !== null) {
      document.getElementById(id).checked = (saved === "true");
    } else {
      // 초기값 true로 설정 (한 번도 저장된 적 없는 경우)
      document.getElementById(id).checked = true;
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  restoreCheckboxStates();        // ✅ 체크박스 복원
  reload();
});


document.getElementById('markDoneBtn').addEventListener('click', async function () {
    const id = document.getElementById('editTaskLink').href.split('/schedule/')[1].split('/')[0];
    try {
      const response = await fetch(`/calendar/schedule/${id}/mark_done/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });

      if (response.ok) {
        // 일정 데이터 갱신
        const modal = bootstrap.Modal.getInstance(
          document.getElementById('taskDetailModal')
        );
        modal.hide();
        location.reload();
        // ✅ 일정 새로 렌더링
      } else {
        alert('완료 처리 실패');
      }
    } catch (e) {
      alert('오류 발생: ' + e);
    }
    reload();
    location.reload();
  });

document.getElementById("unmarkDoneBtn").addEventListener("click", async function () {
  const id = document.getElementById("editTaskLink").href.split("/schedule/")[1].split("/")[0];

  try {
    const response = await fetch(`/calendar/schedule/${id}/unmark_done/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "Content-Type": "application/json"
      },
      body: JSON.stringify({})
    });

    if (response.ok) {
      const modal = bootstrap.Modal.getInstance(document.getElementById("taskDetailModal"));
      modal.hide();
      location.reload();  // 또는 renderWeekSchedule();
    } else {
      alert("미완료 처리 실패");
    }
  } catch (e) {
    alert("오류 발생: " + e);
  }
});


// CSRF 토큰 추출 함수
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}
