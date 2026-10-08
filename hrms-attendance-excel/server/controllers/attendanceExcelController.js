const mongoose = require('mongoose');
const dayjs = require('dayjs');
const { buildWorkbook, parseWorkbook, toDateTime, startOfDay } = require('../utils/attendanceExcel');

// ADAPT: your models and field names.
const User = require('../models/User');
const Attendance = require('../models/Attendance');
const EMPLOYEE_FILTER = {}; // e.g. { role: 'employee', isActive: true }
const EMPLOYEE_FIELDS = 'name email'; // shown in picker + used as sheet name
// Attendance fields used: employee, date, checkIn, checkOut, status, remarks

const MAX_DAYS = 366;
const isDay = (s) => typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && dayjs(s).format('YYYY-MM-DD') === s;

// GET /api/attendance/timeline/employees   (admin) -> list for the "select employees" picker
exports.listEmployees = async (req, res) => {
  try {
    const employees = await User.find(EMPLOYEE_FILTER).select(EMPLOYEE_FIELDS).sort({ name: 1 }).lean();
    res.json(employees);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// POST /api/attendance/timeline/export   (admin)
// body: { from: 'YYYY-MM-DD', to: 'YYYY-MM-DD', employeeIds: 'all' | ['id1', 'id2', ...] }
exports.exportTimeline = async (req, res) => {
  try {
    const { from, to, employeeIds } = req.body;
    if (!isDay(from) || !isDay(to)) return res.status(400).json({ message: 'From and To dates are required (YYYY-MM-DD)' });
    if (dayjs(to).isBefore(dayjs(from))) return res.status(400).json({ message: 'To date must be on or after From date' });
    if (dayjs(to).diff(dayjs(from), 'day') + 1 > MAX_DAYS) {
      return res.status(400).json({ message: `Date range can be at most ${MAX_DAYS} days` });
    }

    const filter = { ...EMPLOYEE_FILTER };
    if (employeeIds !== 'all') {
      if (!Array.isArray(employeeIds) || !employeeIds.length) {
        return res.status(400).json({ message: 'Select at least one employee, or choose All employees' });
      }
      if (!employeeIds.every((id) => mongoose.Types.ObjectId.isValid(id))) {
        return res.status(400).json({ message: 'Invalid employee id in selection' });
      }
      filter._id = { $in: employeeIds };
    }

    const employees = await User.find(filter).select(EMPLOYEE_FIELDS).sort({ name: 1 }).lean();
    if (!employees.length) return res.status(404).json({ message: 'No employees found' });

    const records = await Attendance.find({
      employee: { $in: employees.map((e) => e._id) },
      date: { $gte: startOfDay(from), $lt: startOfDay(dayjs(to).add(1, 'day').format('YYYY-MM-DD')) },
    }).lean();

    const wb = buildWorkbook({ employees, records, from, to });
    const who = employees.length === 1 ? (employees[0].name || 'employee').replace(/[^\w-]+/g, '_') : 'employees';
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', `attachment; filename="attendance_${who}_${from}_to_${to}.xlsx"`);
    await wb.xlsx.write(res);
    res.end();
  } catch (err) {
    if (!res.headersSent) res.status(500).json({ message: err.message });
    else res.end();
  }
};

// POST /api/attendance/timeline/import   (admin, multipart field "file")
// All-or-nothing: if any row has an error, nothing is saved and every error is returned.
exports.importTimeline = async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ message: 'Please choose an .xlsx file to upload' });

    const { rows, errors } = await parseWorkbook(req.file.buffer);

    const ids = [...new Set(rows.map((r) => r.employeeId))];
    const found = await User.find({ ...EMPLOYEE_FILTER, _id: { $in: ids } }).select('_id').lean();
    const known = new Set(found.map((u) => String(u._id)));
    for (const r of rows) {
      if (!known.has(r.employeeId)) errors.push({ sheet: r.sheet, row: r.row, message: 'Employee not found' });
    }

    if (errors.length) {
      errors.sort((a, b) => String(a.sheet).localeCompare(String(b.sheet)) || a.row - b.row);
      return res.status(400).json({ message: `${errors.length} error(s) found. Nothing was saved.`, errors });
    }

    const ops = rows.map((r) => {
      const dayStart = startOfDay(r.date);
      const nextDay = startOfDay(dayjs(r.date).add(1, 'day').format('YYYY-MM-DD'));
      const checkIn = toDateTime(r.date, r.checkIn);
      let checkOut = toDateTime(r.date, r.checkOut);
      if (checkIn && checkOut && checkOut <= checkIn) {
        checkOut = toDateTime(dayjs(r.date).add(1, 'day').format('YYYY-MM-DD'), r.checkOut); // night shift
      }
      return {
        updateOne: {
          filter: { employee: new mongoose.Types.ObjectId(r.employeeId), date: { $gte: dayStart, $lt: nextDay } },
          update: {
            $set: { checkIn, checkOut, status: r.status, remarks: r.remarks },
            $setOnInsert: { date: dayStart },
          },
          upsert: true,
        },
      };
    });

    const result = await Attendance.bulkWrite(ops, { ordered: false });
    res.json({
      message: 'Attendance uploaded',
      totalRows: rows.length,
      created: result.upsertedCount,
      updated: result.modifiedCount,
      unchanged: rows.length - result.upsertedCount - result.modifiedCount,
    });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};
