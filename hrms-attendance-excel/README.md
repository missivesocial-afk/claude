# HRMS – Attendance Timeline Excel (select employees + upload)

**Download:** choose From/To dates and pick employees from the **Employees dropdown**. It starts on
**All employees**; open it to untick that and tick specific employees, with search. You get one `.xlsx` with an **Instructions**
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
| `client/components/EmployeeDropdown.jsx` | `src/components/` (same folder as the panel) |

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

### 4. Styles (needed for the dropdown to look like a dropdown)
```css
.attendance-excel-panel { display: flex; flex-direction: column; gap: 10px; max-width: 640px; }
.attendance-excel-panel > .btn { align-self: flex-start; }
.aep-row { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
.emp-dd { position: relative; width: 340px; max-width: 100%; }
.emp-dd-toggle { width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border: 1px solid #bbb; border-radius: 6px; background: #fff; cursor: pointer; font: inherit; }
.emp-dd-menu { position: absolute; z-index: 50; top: calc(100% + 4px); left: 0; right: 0; background: #fff; border: 1px solid #ccc; border-radius: 6px; box-shadow: 0 6px 18px rgba(0,0,0,.12); padding: 8px; }
.emp-dd-menu input[type=search] { width: 100%; box-sizing: border-box; padding: 6px 8px; margin-bottom: 6px; }
.emp-dd-item { display: flex; gap: 8px; align-items: center; padding: 4px 2px; cursor: pointer; }
.emp-dd-strong { font-weight: 600; border-bottom: 1px solid #eee; padding-bottom: 6px; }
.emp-dd-list { max-height: 240px; overflow-y: auto; }
.emp-dd-item small, .emp-dd-empty { color: #777; }
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
