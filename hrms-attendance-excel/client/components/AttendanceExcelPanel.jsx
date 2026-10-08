import { useEffect, useRef, useState } from 'react';
import { API_BASE, apiFetch, authHeaders } from '../api'; // same api.js as the holiday-removal feature
import EmployeeDropdown from './EmployeeDropdown';

const pad = (n) => String(n).padStart(2, '0');
const ymd = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

/**
 * Admin panel for "Attendance Timeline Excel":
 *  - Download: date range + employee dropdown (All employees or specific ones; one sheet per employee)
 *  - Upload: send the edited file back to create / update attendance
 */
export default function AttendanceExcelPanel({ onUploaded }) {
  const now = new Date();
  const [from, setFrom] = useState(ymd(new Date(now.getFullYear(), now.getMonth(), 1)));
  const [to, setTo] = useState(ymd(now));
  const [employees, setEmployees] = useState([]);
  const [selected, setSelected] = useState(new Set());
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState('');

  const fileRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadErrors, setUploadErrors] = useState([]);

  useEffect(() => {
    apiFetch('/attendance/timeline/employees')
      .then((list) => {
        setEmployees(list);
        setSelected(new Set(list.map((e) => e._id))); // default: all employees
      })
      .catch((e) => setError(e.message));
  }, []);

  const allSelected = employees.length > 0 && selected.size === employees.length;

  const download = async () => {
    setError('');
    if (selected.size === 0) return setError('Select at least one employee');
    setDownloading(true);
    try {
      const res = await fetch(`${API_BASE}/attendance/timeline/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        credentials: 'include',
        body: JSON.stringify({ from, to, employeeIds: allSelected ? 'all' : [...selected] }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.message || 'Download failed');
      }
      const blob = await res.blob();
      const name = /filename="([^"]+)"/.exec(res.headers.get('Content-Disposition') || '')?.[1]
        || `attendance_${from}_to_${to}.xlsx`;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = name;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e.message);
    } finally {
      setDownloading(false);
    }
  };

  const upload = async () => {
    const file = fileRef.current?.files?.[0];
    setUploadResult(null);
    setUploadErrors([]);
    if (!file) return setUploadErrors([{ sheet: '-', row: '-', message: 'Choose an .xlsx file first' }]);
    const form = new FormData();
    form.append('file', file);
    setUploading(true);
    try {
      const res = await fetch(`${API_BASE}/attendance/timeline/import`, {
        method: 'POST',
        headers: authHeaders(), // no Content-Type: the browser sets the multipart boundary
        credentials: 'include',
        body: form,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setUploadErrors(data.errors || [{ sheet: '-', row: '-', message: data.message || 'Upload failed' }]);
        return;
      }
      setUploadResult(data);
      fileRef.current.value = '';
      onUploaded && onUploaded();
    } catch (e) {
      setUploadErrors([{ sheet: '-', row: '-', message: e.message }]);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="attendance-excel-panel">
      <h3>Attendance Timeline Excel</h3>

      <div className="aep-row">
        <label>
          From <input type="date" value={from} max={to} onChange={(e) => setFrom(e.target.value)} />
        </label>
        <label>
          To <input type="date" value={to} min={from} onChange={(e) => setTo(e.target.value)} />
        </label>
      </div>

      <div className="aep-row">
        <label>Employees</label>
        <EmployeeDropdown employees={employees} selected={selected} onChange={setSelected} />
      </div>

      {error && <p className="text-danger">{error}</p>}
      <button type="button" className="btn btn-primary" onClick={download} disabled={downloading}>
        {downloading ? 'Preparing…' : `Download Excel${allSelected ? ' (all)' : selected.size ? ` (${selected.size})` : ''}`}
      </button>

      <hr />

      <h4>Upload edited sheet</h4>
      <p>
        <small>
          Upload the same file you downloaded, after editing Check In / Check Out / Status / Remarks. If any row has an
          error, nothing is saved.
        </small>
      </p>
      <div className="aep-row">
        <input ref={fileRef} type="file" accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" />
        <button type="button" className="btn btn-success" onClick={upload} disabled={uploading}>
          {uploading ? 'Uploading…' : 'Upload'}
        </button>
      </div>

      {uploadResult && (
        <p className="text-success">
          Done: {uploadResult.created} created, {uploadResult.updated} updated, {uploadResult.unchanged} unchanged.
        </p>
      )}
      {uploadErrors.length > 0 && (
        <div className="aep-errors">
          <p className="text-danger">
            {uploadErrors.length} error(s). Nothing was saved. Fix these in the file and upload again:
          </p>
          <table className="table table-sm">
            <thead>
              <tr>
                <th>Sheet</th>
                <th>Row</th>
                <th>Problem</th>
              </tr>
            </thead>
            <tbody>
              {uploadErrors.slice(0, 200).map((e, i) => (
                <tr key={i}>
                  <td>{e.sheet}</td>
                  <td>{e.row}</td>
                  <td>{e.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
