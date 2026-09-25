// 📋 Klassen-Checkliste — Autosave mit Debounce
const debounce = (fn, ms = 600) => {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
};

document.querySelectorAll('.item').forEach(card => {
  const id = card.dataset.id;
  const noteEl = card.querySelector('.note');

  const save = () => fetch('/api/checklist/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, status: card.dataset.status, note: noteEl.value })
  }).then(() => {
    card.querySelector('.meta').textContent = '💾 gespeichert ' + new Date().toLocaleString('de-DE');
  });

  card.querySelectorAll('.status-btn').forEach(btn => btn.addEventListener('click', () => {
    card.querySelectorAll('.status-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    card.dataset.status = btn.dataset.status;
    card.setAttribute('data-status', btn.dataset.status);
    save();
  }));

  noteEl.addEventListener('input', debounce(save, 700));
});

document.querySelectorAll('.eval').forEach(card => {
  const id = card.dataset.id;
  const doneBtn = card.querySelector('.done-btn');
  const resEl = card.querySelector('.result');
  let done = doneBtn.classList.contains('active');

  const save = () => fetch('/api/evaluation/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, done, result: resEl.value })
  });

  doneBtn.addEventListener('click', () => {
    done = !done;
    doneBtn.classList.toggle('active', done);
    doneBtn.textContent = done ? '✅' : '⬜';
    save();
  });
  resEl.addEventListener('input', debounce(save, 700));
});

const refSaved = document.getElementById('ref-saved');
document.querySelectorAll('.ref').forEach(ta => {
  ta.addEventListener('input', debounce(() => {
    fetch('/api/reflection/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ year_id: YEAR_ID, stage: STAGE, qkey: ta.dataset.qkey, answer: ta.value })
    }).then(() => {
      refSaved.textContent = '💾 Reflexion gespeichert — ' + new Date().toLocaleTimeString('de-DE');
    });
  }, 800));
});
