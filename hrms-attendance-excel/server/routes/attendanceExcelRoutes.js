const express = require('express');
const multer = require('multer');
const ctrl = require('../controllers/attendanceExcelController');
// requireAdmin comes from the holiday-removal feature (middleware/requireAdmin.js).
const requireAdmin = require('../middleware/requireAdmin');
// ADAPT: path/name of your existing login-check middleware (the one that sets req.user).
const { protect } = require('../middleware/authMiddleware');

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 5 * 1024 * 1024 }, // 5 MB
  fileFilter: (req, file, cb) => {
    const ok = /\.xlsx$/i.test(file.originalname);
    cb(ok ? null : new Error('Only .xlsx files are allowed'), ok);
  },
});

// Turn multer errors (too big / wrong type) into a clean 400 instead of a crash page.
const uploadFile = (req, res, next) =>
  upload.single('file')(req, res, (err) => {
    if (!err) return next();
    const message = err.code === 'LIMIT_FILE_SIZE' ? 'File is too large (max 5 MB)' : err.message;
    res.status(400).json({ message });
  });

const router = express.Router();

router.get('/attendance/timeline/employees', protect, requireAdmin, ctrl.listEmployees);
router.post('/attendance/timeline/export', protect, requireAdmin, ctrl.exportTimeline);
router.post('/attendance/timeline/import', protect, requireAdmin, uploadFile, ctrl.importTimeline);

module.exports = router;
