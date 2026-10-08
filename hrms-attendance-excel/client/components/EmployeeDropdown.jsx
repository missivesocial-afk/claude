import { useEffect, useMemo, useRef, useState } from 'react';

/**
 * Dropdown to pick employees: "All employees" at the top, then a search box and one checkbox per employee.
 * Props:
 *  - employees: [{ _id, name, email }]
 *  - selected: Set of selected ids
 *  - onChange(newSet)
 */
export default function EmployeeDropdown({ employees, selected, onChange }) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const boxRef = useRef(null);

  // close when clicking outside
  useEffect(() => {
    const close = (e) => boxRef.current && !boxRef.current.contains(e.target) && setOpen(false);
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return q ? employees.filter((e) => `${e.name || ''} ${e.email || ''}`.toLowerCase().includes(q)) : employees;
  }, [employees, search]);

  const allSelected = employees.length > 0 && selected.size === employees.length;
  const allFilteredSelected = filtered.length > 0 && filtered.every((e) => selected.has(e._id));

  const label = allSelected
    ? `All employees (${employees.length})`
    : selected.size === 0
      ? 'Select employees…'
      : selected.size === 1
        ? (() => {
            const e = employees.find((x) => selected.has(x._id));
            return e ? e.name || e.email : '1 employee';
          })()
        : `${selected.size} employees selected`;

  const toggle = (id) => {
    const next = new Set(selected);
    next.has(id) ? next.delete(id) : next.add(id);
    onChange(next);
  };

  const toggleAll = () => onChange(allSelected ? new Set() : new Set(employees.map((e) => e._id)));

  const toggleFiltered = () => {
    const next = new Set(selected);
    filtered.forEach((e) => (allFilteredSelected ? next.delete(e._id) : next.add(e._id)));
    onChange(next);
  };

  return (
    <div className="emp-dd" ref={boxRef}>
      <button type="button" className="emp-dd-toggle" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        <span>{label}</span>
        <span className="emp-dd-caret">▾</span>
      </button>

      {open && (
        <div className="emp-dd-menu">
          <input
            type="search"
            placeholder="Search employee…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            autoFocus
          />

          {search ? (
            <label className="emp-dd-item emp-dd-strong">
              <input type="checkbox" checked={allFilteredSelected} onChange={toggleFiltered} />
              Select all matching "{search}"
            </label>
          ) : (
            <label className="emp-dd-item emp-dd-strong">
              <input type="checkbox" checked={allSelected} onChange={toggleAll} />
              All employees
            </label>
          )}

          <div className="emp-dd-list">
            {filtered.map((e) => (
              <label key={e._id} className="emp-dd-item">
                <input type="checkbox" checked={selected.has(e._id)} onChange={() => toggle(e._id)} />
                <span>
                  {e.name || e.email}
                  {e.name && e.email ? <small> — {e.email}</small> : null}
                </span>
              </label>
            ))}
            {filtered.length === 0 && <small className="emp-dd-empty">No employees match.</small>}
          </div>
        </div>
      )}
    </div>
  );
}
