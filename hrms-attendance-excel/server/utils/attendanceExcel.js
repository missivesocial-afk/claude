const ExcelJS = require('exceljs');
const dayjs = require('dayjs');
dayjs.extend(require('dayjs/plugin/utc'));
dayjs.extend(require('dayjs/plugin/timezone'));

// ADAPT: your office time zone (check-in / check-out times are shown and read in this zone).
const TIMEZONE = process.env.ATTENDANCE_TZ || 'Asia/Kolkata';
// ADAPT: the status values your Attendance model accepts.
const STATUSES = ['present', 'absent', 'half-day', 'leave', 'holiday', 'week-off'];
const MAX_ROWS = 50000;

const COLUMNS = [
  { header: 'Employee ID', key: 'employeeId', width: 26 },
  { header: 'Employee Name', key: 'name', width: 24 },
  { header: 'Date (YYYY-MM-DD)', key: 'date', width: 18 },
  { header: 'Day', key: 'day', width: 7 },
  { header: 'Check In (HH:mm)', key: 'checkIn', width: 17 },
  { header: 'Check Out (HH:mm)', key: 'checkOut', width: 18 },
  { header: 'Worked Hours', key: 'hours', width: 14 },
  { header: 'Status', key: 'status', width: 12 },
  { header: 'Remarks', key: 'remarks', width: 32 },
];
const READ_ONLY_KEYS = ['employeeId', 'name', 'day', 'hours']; // grey, ignored on upload (except Employee ID)
const GREY = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFEFEFEF' } };

const pad = (n) => String(n).padStart(2, '0');
const dayKey = (d) => dayjs(d).tz(TIMEZONE).format('YYYY-MM-DD');
const timeOf = (d) => (d ? dayjs(d).tz(TIMEZONE).format('HH:mm') : '');

// "2026-10-08" + "09:30" in office time zone -> Date. Overnight check-out (earlier than check-in) = next day.
function toDateTime(date, hhmm) {
  return hhmm ? dayjs.tz(`${date}T${hhmm}:00`, TIMEZONE).toDate() : null;
}
function startOfDay(date) {
  return dayjs.tz(`${date}T00:00:00`, TIMEZONE).toDate();
}
function workedHours(checkIn, checkOut) {
  if (!checkIn || !checkOut) return '';
  let mins = (new Date(checkOut) - new Date(checkIn)) / 60000;
  if (mins < 0) mins += 24 * 60;
  return Math.round((mins / 60) * 100) / 100;
}

// Excel sheet names: max 31 chars, no []:*?/\ and must be unique.
function sheetName(employee, used) {
  const base = String(employee.name || employee.email || employee._id)
    .replace(/[[\]:*?/\\]/g, ' ')
    .trim()
    .slice(0, 28) || 'Employee';
  let name = base;
  for (let i = 2; used.has(name.toLowerCase()); i++) name = `${base.slice(0, 27 - String(i).length)} (${i})`;
  used.add(name.toLowerCase());
  return name;
}

/**
 * employees: [{ _id, name, email }]
 * records:   [{ employee, date, checkIn, checkOut, status, remarks }]   (Attendance docs)
 * from / to: 'YYYY-MM-DD'
 */
function buildWorkbook({ employees, records, from, to }) {
  const wb = new ExcelJS.Workbook();
  wb.creator = 'HRMS';

  const info = wb.addWorksheet('Instructions');
  info.columns = [{ width: 110 }];
  [
    'Attendance Timeline - how to upload',
    `Period: ${from} to ${to}   |   Time zone: ${TIMEZONE}`,
    '',
    '1. Each employee has their own sheet. Edit only the white columns: Check In, Check Out, Status, Remarks.',
    '2. Times as 24-hour HH:mm (e.g. 09:30, 18:45). A Check Out earlier than Check In counts as the next day (night shift).',
    `3. Status must be one of: ${STATUSES.join(', ')}. If Check In is filled and Status is empty, "present" is used.`,
    '4. Do not change the Employee ID or Date columns. Rows that are completely empty are skipped.',
    '5. Upload this same file in HRMS > Attendance Timeline > Upload. If any row has an error, nothing is saved.',
  ].forEach((t, i) => {
    const row = info.addRow([t]);
    if (i === 0) row.font = { bold: true, size: 14 };
  });

  const byKey = new Map(records.map((r) => [`${r.employee}|${dayKey(r.date)}`, r]));
  const used = new Set(['instructions']);
  const days = [];
  for (let d = dayjs(from); !d.isAfter(dayjs(to)); d = d.add(1, 'day')) days.push(d);

  for (const emp of employees) {
    const ws = wb.addWorksheet(sheetName(emp, used), { views: [{ state: 'frozen', ySplit: 1 }] });
    ws.columns = COLUMNS;
    ws.getRow(1).font = { bold: true };
    ws.getRow(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
    for (const key of ['date', 'checkIn', 'checkOut']) ws.getColumn(key).numFmt = '@'; // keep as text

    for (const d of days) {
      const date = d.format('YYYY-MM-DD');
      const rec = byKey.get(`${emp._id}|${date}`);
      const row = ws.addRow({
        employeeId: String(emp._id),
        name: emp.name || emp.email || '',
        date,
        day: d.format('ddd'),
        checkIn: rec ? timeOf(rec.checkIn) : '',
        checkOut: rec ? timeOf(rec.checkOut) : '',
        hours: rec ? workedHours(rec.checkIn, rec.checkOut) : '',
        status: rec?.status || '',
        remarks: rec?.remarks || '',
      });
      for (const key of [...READ_ONLY_KEYS, 'date']) row.getCell(key).fill = GREY;
      row.getCell('status').dataValidation = {
        type: 'list',
        allowBlank: true,
        formulae: [`"${STATUSES.join(',')}"`],
        showErrorMessage: true,
        error: `Choose one of: ${STATUSES.join(', ')}`,
      };
    }
  }
  return wb;
}

// ---------- reading an uploaded file ----------

const HEADER_MATCH = {
  employeeId: 'employee id',
  date: 'date',
  checkIn: 'check in',
  checkOut: 'check out',
  status: 'status',
  remarks: 'remarks',
};

function cellText(v) {
  if (v === null || v === undefined) return '';
  if (v instanceof Date) return v;
  if (typeof v === 'object') {
    if (v.richText) return v.richText.map((t) => t.text).join('').trim();
    if ('result' in v) return cellText(v.result); // formula
    if (v.text) return String(v.text).trim(); // hyperlink
  }
  return typeof v === 'number' ? v : String(v).trim();
}

function readDate(v) {
  if (typeof v === 'number' && v > 60 && v < 2958466) v = new Date(Date.UTC(1899, 11, 30) + Math.floor(v) * 86400000); // Excel serial date
  if (v instanceof Date) return `${v.getUTCFullYear()}-${pad(v.getUTCMonth() + 1)}-${pad(v.getUTCDate())}`;
  const m = /^(\d{4})-(\d{1,2})-(\d{1,2})$/.exec(String(v));
  if (!m) return null;
  const s = `${m[1]}-${pad(m[2])}-${pad(m[3])}`;
  return dayjs(s).format('YYYY-MM-DD') === s ? s : null;
}

function readTime(v) {
  if (v === '') return '';
  if (v instanceof Date) return `${pad(v.getUTCHours())}:${pad(v.getUTCMinutes())}`;
  if (typeof v === 'number' && v >= 0 && v < 1) {
    const mins = Math.round(v * 24 * 60) % (24 * 60); // Excel time fraction
    return `${pad(Math.floor(mins / 60))}:${pad(mins % 60)}`;
  }
  const m = /^(\d{1,2}):(\d{2})(?::\d{2})?\s*(am|pm)?$/i.exec(String(v));
  if (!m) return null;
  let h = Number(m[1]);
  const min = Number(m[2]);
  if (m[3]) {
    if (h < 1 || h > 12) return null;
    h = (h % 12) + (m[3].toLowerCase() === 'pm' ? 12 : 0);
  }
  return h <= 23 && min <= 59 ? `${pad(h)}:${pad(min)}` : null;
}

/** Returns { rows, errors }. rows: [{ employeeId, date, checkIn, checkOut, status, remarks, sheet, row }] */
async function parseWorkbook(buffer) {
  const wb = new ExcelJS.Workbook();
  try {
    await wb.xlsx.load(buffer);
  } catch {
    return { rows: [], errors: [{ sheet: '-', row: '-', message: 'File is not a valid .xlsx Excel file' }] };
  }

  const rows = [];
  const errors = [];
  const seen = new Map();

  wb.eachSheet((ws) => {
    const col = {};
    ws.getRow(1).eachCell((cell, n) => {
      const h = String(cellText(cell.value)).toLowerCase();
      for (const [key, label] of Object.entries(HEADER_MATCH)) if (!col[key] && h.startsWith(label)) col[key] = n;
    });
    if (!col.employeeId || !col.date) return; // not an attendance sheet (e.g. Instructions)

    ws.eachRow((r, rowNo) => {
      if (rowNo === 1) return;
      const get = (k) => (col[k] ? cellText(r.getCell(col[k]).value) : '');
      const err = (message) => errors.push({ sheet: ws.name, row: rowNo, message });

      const rawIn = get('checkIn');
      const rawOut = get('checkOut');
      let status = String(get('status')).toLowerCase();
      const remarks = String(get('remarks'));
      if (rawIn === '' && rawOut === '' && status === '' && remarks === '') return; // empty day -> skip

      const employeeId = String(get('employeeId'));
      const date = readDate(get('date'));
      const checkIn = readTime(rawIn);
      const checkOut = readTime(rawOut);

      if (!/^[a-f\d]{24}$/i.test(employeeId)) return err('Employee ID is missing or was changed');
      if (!date) return err(`Date "${get('date')}" is not valid (use YYYY-MM-DD)`);
      if (checkIn === null) return err(`Check In "${rawIn}" is not a valid time (use HH:mm)`);
      if (checkOut === null) return err(`Check Out "${rawOut}" is not a valid time (use HH:mm)`);
      if (checkOut && !checkIn) return err('Check Out is filled but Check In is empty');
      if (!status && checkIn) status = 'present';
      if (!STATUSES.includes(status)) return err(`Status "${status}" is not valid. Use: ${STATUSES.join(', ')}`);
      if (remarks.length > 500) return err('Remarks must be 500 characters or less');

      const key = `${employeeId}|${date}`;
      if (seen.has(key)) return err(`Same employee and date also on ${seen.get(key)}`);
      seen.set(key, `sheet "${ws.name}" row ${rowNo}`);

      rows.push({ employeeId, date, checkIn, checkOut, status, remarks, sheet: ws.name, row: rowNo });
    });
  });

  if (rows.length > MAX_ROWS) errors.push({ sheet: '-', row: '-', message: `Too many rows (max ${MAX_ROWS})` });
  if (!rows.length && !errors.length) {
    errors.push({ sheet: '-', row: '-', message: 'No attendance rows found. Upload the file downloaded from Attendance Timeline.' });
  }
  return { rows, errors };
}

module.exports = {
  TIMEZONE,
  STATUSES,
  buildWorkbook,
  parseWorkbook,
  toDateTime,
  startOfDay,
  workedHours,
};
