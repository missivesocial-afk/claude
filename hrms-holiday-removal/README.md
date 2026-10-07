# HRMS – Holiday removal requests (employee → admin)

**Before:** an employee could remove an approved holiday directly.
**After:** the employee clicks **Request Removal** and gives a reason. The request goes to admin.
Only admin can see these requests and the reasons. Admin can **Approve & Undo** the holiday or **Reject** the request.

Stack assumed: Express + MongoDB (Mongoose) + React. Search for `ADAPT` in the files. Those are the
places you may need to rename things to match your project.

## Files

| Copy this file | Into your project |
|---|---|
| `server/models/HolidayRemovalRequest.js` | `models/` |
| `server/controllers/holidayRemovalController.js` | `controllers/` |
| `server/routes/holidayRemovalRoutes.js` | `routes/` |
| `server/middleware/requireAdmin.js` | `middleware/` (skip if you already have an admin check) |
| `client/api.js` | `src/` (or use your existing axios helper) |
| `client/components/RequestRemovalButton.jsx` | `src/components/` |
| `client/pages/AdminRemovalRequests.jsx` | `src/pages/` |

## Steps

### 1. Fix the `ADAPT` lines in the controller
- `require('../models/Holiday')`: your holiday or leave model.
- `HOLIDAY_OWNER_FIELD`: the field holding the employee id (`employee`, `user`, `employeeId`…).
- `APPROVED_STATUS` / `REMOVED_STATUS`: your status values. Admin approval sets the holiday to
  `REMOVED_STATUS`, which keeps a history. If you'd rather delete it, replace the `findOneAndUpdate`
  with `Holiday.findOneAndDelete({ _id: request.holiday, status: APPROVED_STATUS })`.
- If an approved holiday deducts leave balance, add the refund where the comment says so.

### 2. Register the routes (`server.js` / `app.js`)
```js
app.use('/api', require('./routes/holidayRemovalRoutes'));
```
In `holidayRemovalRoutes.js`, point `protect` at your real login middleware.

### 3. IMPORTANT: block employees from removing holidays directly
Hiding the button isn't enough, because an employee could still call the API.
Find your existing delete/remove route for holidays and make it admin-only:
```js
const requireAdmin = require('../middleware/requireAdmin');

// before
router.delete('/holidays/:id', protect, deleteHoliday);
// after
router.delete('/holidays/:id', protect, requireAdmin, deleteHoliday);
```
(If an employee may still delete a holiday that is **not yet approved**, add a status check inside
`deleteHoliday` instead: if `status === 'approved'` and the user isn't admin, return 403.)

### 4. Employee holiday list: swap the Remove button
```jsx
import RequestRemovalButton from '../components/RequestRemovalButton';

// load the employee's pending requests once
const [myRequests, setMyRequests] = useState([]);
const loadMyRequests = () => apiFetch('/holiday-removal-requests/mine').then(setMyRequests);
useEffect(() => { loadMyRequests(); }, []);

// in the table row, replace the old Remove button for approved holidays:
{holiday.status === 'approved' && (
  <RequestRemovalButton
    holiday={holiday}
    pendingRequest={myRequests.some(
      (r) => r.status === 'pending' && (r.holiday?._id || r.holiday) === holiday._id
    )}
    onRequested={loadMyRequests}
  />
)}
```

### 5. Admin page: add a route and menu item (admin only)
```jsx
import AdminRemovalRequests from './pages/AdminRemovalRequests';

<Route path="/admin/holiday-removal-requests" element={<AdminRoute><AdminRemovalRequests /></AdminRoute>} />
```
Show the menu link only when `user.role === 'admin'`. The API also returns 403 to non-admins anyway.

### 6. Styles
The modal uses `modal-backdrop-custom`, `modal-box` and `modal-actions`. Either add this CSS or swap them for your UI library's modal:
```css
.modal-backdrop-custom { position: fixed; inset: 0; background: rgba(0,0,0,.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-box { background: #fff; padding: 20px; border-radius: 8px; width: min(480px, 92vw); display: flex; flex-direction: column; gap: 8px; }
.modal-box textarea { width: 100%; }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; }
```

## API

| Method | URL | Who | What |
|---|---|---|---|
| POST | `/api/holidays/:holidayId/removal-requests` body `{ reason }` | employee (own approved holiday) | send request |
| GET | `/api/holiday-removal-requests/mine` | employee | own requests and their status |
| GET | `/api/holiday-removal-requests?status=pending\|approved\|rejected\|all` | admin | list with reason |
| PATCH | `/api/holiday-removal-requests/:id/approve` body `{ adminNote? }` | admin | undo the holiday |
| PATCH | `/api/holiday-removal-requests/:id/reject` body `{ adminNote? }` | admin | keep the holiday |

## Rules built in
- The reason is required (5–500 characters).
- Only the holiday's own employee can request, and only for an **approved** holiday.
- Only one pending request per holiday, enforced in code and by a unique database index. After a rejection, the employee can ask again.
- Two admins can't approve the same request twice, because the claim is atomic.
- If the holiday was already changed when admin approves, the request goes back to pending and nothing is lost.
