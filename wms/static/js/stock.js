async function refreshShelves() {
  const whSelect = document.getElementById('warehouse_id');
  const shelfSelect = document.getElementById('shelf_id');
  if (!whSelect || !shelfSelect) return;

  const warehouseId = whSelect.value;
  shelfSelect.innerHTML = '';

  const defaultOpt = document.createElement('option');
  defaultOpt.value = '0';
  defaultOpt.textContent = '-';
  shelfSelect.appendChild(defaultOpt);

  if (!warehouseId) return;

  const resp = await fetch(`/stock/api/shelves?warehouse_id=${encodeURIComponent(warehouseId)}`);
  if (!resp.ok) return;

  const data = await resp.json();
  for (const s of data) {
    const opt = document.createElement('option');
    opt.value = String(s.id);
    opt.textContent = s.code;
    shelfSelect.appendChild(opt);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const whSelect = document.getElementById('warehouse_id');
  if (whSelect) {
    whSelect.addEventListener('change', () => {
      refreshShelves();
    });
  }
});
