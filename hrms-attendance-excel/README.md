# HRMS – Attendance Timeline Excel (select employees + upload)

**Download:** choose From/To dates, then either **All employees** or **Select employees**. The picker has
search, a **Select all** checkbox and a checkbox per employee. You get one `.xlsx` with an **Instructions**
sheet plus **one sheet per employee**, one row per day.

**Upload:** an admin edits that same file and uploads it back. Attendance rows are created or updated.
If **any** row has a mistake, **nothing is saved** and the page lists every error (sheet, row, problem).

See `sample_attendance_timeline.xlsx` for what the download looks like.

Stack assumed: Express + MongoDB (Mongoose) + React, same as the holiday-removal feature.
Search for `ADAPT` to find what may need renaming.

## Install
```bash
npm install exceljs multer dayjs
```

## Files

| Copy this file | Into your project |
|---|---|
| `server/utils/attendanceExcel.js` | `utils/` |
| `server/controllers/attendanceExcelController.js` | `controllers/` |
| `server/routes/attendanceExcelRoutes.js` | `routes/` |
| `client/components/AttendanceExcelPanel.jsx` | `src/components/` |

It also uses `middleware/requireAdmin.js` and `src/api.js` from the `hrms-holiday-removal` folder.
`api.js` was updated to also export `API_BASE` and `authHeaders`, so copy it again.

## Steps

### 1. Fix the `ADAPT` lines
- **`attendanceExcel.js`**
  - `TIMEZONE`: your office time zone. The default is `Asia/Kolkata`, or set `ATTENDANCE_TZ` in `.env`.
  - `STATUSES`: the exact status values your Attendance model allows.
- **`attendanceExcelController.js`**
  - The `User` / `Attendance` model paths.
  - `EMPLOYEE_FILTER`: for example `{ role: 'employee', isActive: true }`, so admins and ex-employees aren't listed.
  - `EMPLOYEE_FIELDS`: the name field used for the picker and the sheet names.
  - The Attendance fields expected are `employee`, `date` (start of day), `checkIn`, `checkOut` (Date),
    `status` and `remarks`. If yours are named differently (for example `user`, `inTime`, `outTime`), rename them in
    the controller (the `find` and `ops` parts) and in `buildWorkbook`.

### 2. Register the routes (`server.js` / `app.js`)
```js
app.use('/api', require('./routes/attendanceExcelRoutes'));
```
In `attendanceExcelRoutes.js`, point `protect` at your real login middleware.

### 3. Put the panel on your Attendance Timeline page (admin only)
```jsx
import AttendanceExcelPanel from '../components/AttendanceExcelPanel';

{user.role === 'admin' && <AttendanceExcelPanel onUploaded={reloadTimeline} />}
```
It can replace your current "Download Excel" button. `onUploaded` is optional; use it to refresh the timeline after an upload.

### 4. Styles (optional)
```css
.attendance-excel-panel { display: flex; flex-direction: column; gap: 10px; max-width: 640px; }
.aep-row { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
.aep-picker { border: 1px solid #ddd; border-radius: 6px; padding: 8px; }
.aep-picker input[type=search] { width: 100%; margin-bottom: 6px; }
.aep-select-all { display: flex; gap: 6px; font-weight: 600; border-bottom: 1px solid #eee; padding-bottom: 6px; }
.aep-count { margin-left: auto; font-weight: 400; color: #666; }
.aep-list { max-height: 260px; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; padding-top: 6px; }
```

## The Excel sheet

| Employee ID | Employee Name | Date (YYYY-MM-DD) | Day | Check In (HH:mm) | Check Out (HH:mm) | Worked Hours | Status | Remarks |
|---|---|---|---|---|---|---|---|---|
| grey (don't edit) | grey | grey | grey | **edit** | **edit** | grey (auto) | **edit** (dropdown) | **edit** |

Upload rules:
- Rows where Check In, Check Out, Status and Remarks are all empty are skipped. Nothing is deleted.
- Times can be typed as `09:30`, `9:30 AM` or any Excel time format.
- A Check Out earlier than the Check In counts as the next day (night shift).
- A row with Check In and no Status is saved as `present`.
- Upload creates the record if that employee and day has none, and updates it if one exists.
- Grey columns (name, day, worked hours) are ignored on upload. Employee ID and Date identify the row.
- Max file size is 5 MB, and only `.xlsx` is accepted.

## API (admin only)

| Method | URL | Body |
|---|---|---|
| GET | `/api/attendance/timeline/employees` | for the picker |
| POST | `/api/attendance/timeline/export` | `{ from, to, employeeIds: 'all' \| [ids] }` → `.xlsx` file |
| POST | `/api/attendance/timeline/import` | multipart, field `file` → `{ created, updated, unchanged }` or `400 { errors: [{ sheet, row, message }] }` |
