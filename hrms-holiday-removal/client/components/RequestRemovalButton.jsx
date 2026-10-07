import { useState } from 'react';
import { apiFetch } from '../api';

/**
 * Replaces the old "Remove" button on an APPROVED holiday.
 * Props:
 *  - holiday: the holiday object (needs _id)
 *  - pendingRequest: true if this holiday already has a pending removal request
 *  - onRequested: callback after a request is sent (e.g. refresh the list)
 */
export default function RequestRemovalButton({ holiday, pendingRequest, onRequested }) {
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  if (pendingRequest) {
    return <span className="badge badge-warning">Removal requested – pending admin</span>;
  }

  const submit = async (e) => {
    e.preventDefault();
    if (reason.trim().length < 5) {
      setError('Please give a reason (at least 5 characters)');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await apiFetch(`/holidays/${holiday._id}/removal-requests`, {
        method: 'POST',
        body: JSON.stringify({ reason: reason.trim() }),
      });
      setOpen(false);
      setReason('');
      onRequested && onRequested();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <button type="button" className="btn btn-outline-danger btn-sm" onClick={() => setOpen(true)}>
        Request Removal
      </button>

      {open && (
        <div className="modal-backdrop-custom" onClick={() => !saving && setOpen(false)}>
          <form className="modal-box" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
            <h3>Request holiday removal</h3>
            <p>Your request will be sent to admin. The holiday stays approved until admin accepts it.</p>
            <label htmlFor="removal-reason">Reason *</label>
            <textarea
              id="removal-reason"
              rows={4}
              maxLength={500}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Why do you want to remove this holiday?"
              required
            />
            {error && <p className="text-danger">{error}</p>}
            <div className="modal-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setOpen(false)} disabled={saving}>
                Cancel
              </button>
              <button type="submit" className="btn btn-danger" disabled={saving}>
                {saving ? 'Sending…' : 'Send Request'}
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
}
