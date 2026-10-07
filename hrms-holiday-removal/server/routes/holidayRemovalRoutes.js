const express = require('express');
const ctrl = require('../controllers/holidayRemovalController');
const requireAdmin = require('../middleware/requireAdmin');

// ADAPT: path/name of your existing login-check middleware (the one that sets req.user).
const { protect } = require('../middleware/authMiddleware');

const router = express.Router();

// Employee
router.post('/holidays/:holidayId/removal-requests', protect, ctrl.createRequest);
router.get('/holiday-removal-requests/mine', protect, ctrl.myRequests);

// Admin only
router.get('/holiday-removal-requests', protect, requireAdmin, ctrl.listRequests);
router.patch('/holiday-removal-requests/:id/approve', protect, requireAdmin, ctrl.approveRequest);
router.patch('/holiday-removal-requests/:id/reject', protect, requireAdmin, ctrl.rejectRequest);

module.exports = router;
