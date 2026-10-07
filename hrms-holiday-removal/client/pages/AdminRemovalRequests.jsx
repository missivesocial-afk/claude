import { useEffect, useState, useCallback } from 'react';
import { apiFetch } from '../api';

const fmt = (d) => (d ? new Date(d).toLocaleDateString() : '-');

// Admin-only page: list employee requests to remove approved holidays, with reason, and Approve (undo) / Reject.
export default function AdminRemovalRequests() {
  const [status, setStatus] = useState('pending');
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [busyId, setBusyId] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setRequests(await apiFetch(`/holiday-removal-requests?status=${status}`));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [status]);

  useEffect(() => {
    load();
  }, [load]);

  const act = async (id, action) => {
    const verb = action === 'approve' ? 'approve and REMOVE this holiday' : 'reject this request';
    const adminNote = window.prompt(`Optional note to employee (${verb}):`, '');
    if (adminNote === null) return; // admin cancelled
    setBusyId(id);
    try {
      await apiFetch(`/holiday-removal-requests/${id}/${action}`, {
        method: 'PATCH',
        body: JSON.stringify({ adminNote }),
      });
      await load();
    } catch (err) {
      alert(err.message);
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="container">
      <h2>Holiday Removal Requests</h2>

      <select value={status} onChange={(e) => setStatus(e.target.value)}>
        <option value="pending">Pending</option>
        <option value="approved">Approved (removed)</option>
        <option value="rejected">Rejected</option>
        <option value="all">All</option>
      </select>

      {error && <p className="text-danger">{error}</p>}
      {loading ? (
        <p>Loading…</p>
      ) : requests.length === 0 ? (
        <p>No {status === 'all' ? '' : status} requests.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Employee</th>
              {/* ADAPT: field names of your Holiday model */}
              <th>Holiday date(s)</th>
              <th>Reason</th>
              <th>Requested on</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {requests.map((r) => (
              <tr key={r._id}>
                <td>{r.employee?.name || r.employee?.email}</td>
                <td>
                  {fmt(r.holiday?.startDate || r.holiday?.date)}
                  {r.holiday?.endDate ? ` – ${fmt(r.holiday.endDate)}` : ''}
                </td>
                <td style={{ whiteSpace: 'pre-wrap' }}>{r.reason}</td>
                <td>{fmt(r.createdAt)}</td>
                <td>
                  {r.status}
                  {r.adminNote ? <div><small>Note: {r.adminNote}</small></div> : null}
                </td>
                <td>
                  {r.status === 'pending' ? (
                    <>
                      <button
                        className="btn btn-danger btn-sm"
                        disabled={busyId === r._id}
                        onClick={() => act(r._id, 'approve')}
                      >
                        Approve &amp; Undo Holiday
                      </button>{' '}
                      <button
                        className="btn btn-secondary btn-sm"
                        disabled={busyId === r._id}
                        onClick={() => act(r._id, 'reject')}
                      >
                        Reject
                      </button>
                    </>
                  ) : (
                    <small>by {r.reviewedBy?.name || '-'} on {fmt(r.reviewedAt)}</small>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
