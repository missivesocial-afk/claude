const mongoose = require('mongoose');
const HolidayRemovalRequest = require('../models/HolidayRemovalRequest');

// ADAPT these to match your existing Holiday / Leave model.
const Holiday = require('../models/Holiday');
const HOLIDAY_OWNER_FIELD = 'employee'; // field on Holiday that holds the employee's user id
const APPROVED_STATUS = 'approved'; // Holiday.status value for an approved holiday
const REMOVED_STATUS = 'cancelled'; // Holiday.status value after admin undoes it

const isId = (id) => mongoose.Types.ObjectId.isValid(id);

// POST /api/holidays/:holidayId/removal-requests   (employee)
exports.createRequest = async (req, res) => {
  try {
    const { holidayId } = req.params;
    const reason = (req.body.reason || '').trim();

    if (!isId(holidayId)) return res.status(400).json({ message: 'Invalid holiday id' });
    if (reason.length < 5) {
      return res.status(400).json({ message: 'Please give a reason (at least 5 characters)' });
    }
    if (reason.length > 500) {
      return res.status(400).json({ message: 'Reason must be 500 characters or less' });
    }

    const holiday = await Holiday.findById(holidayId);
    if (!holiday || String(holiday[HOLIDAY_OWNER_FIELD]) !== String(req.user._id)) {
      return res.status(404).json({ message: 'Holiday not found' });
    }
    if (holiday.status !== APPROVED_STATUS) {
      return res.status(400).json({ message: 'Only approved holidays can be requested for removal' });
    }

    const existing = await HolidayRemovalRequest.findOne({ holiday: holidayId, status: 'pending' });
    if (existing) {
      return res.status(409).json({ message: 'A removal request is already pending for this holiday' });
    }

    const request = await HolidayRemovalRequest.create({
      holiday: holidayId,
      employee: req.user._id,
      reason,
    });
    res.status(201).json(request);
  } catch (err) {
    if (err.code === 11000) {
      return res.status(409).json({ message: 'A removal request is already pending for this holiday' });
    }
    res.status(500).json({ message: err.message });
  }
};

// GET /api/holiday-removal-requests/mine   (employee: see own requests + status)
exports.myRequests = async (req, res) => {
  try {
    const requests = await HolidayRemovalRequest.find({ employee: req.user._id })
      .populate('holiday')
      .sort({ createdAt: -1 });
    res.json(requests);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// GET /api/holiday-removal-requests?status=pending   (admin only)
exports.listRequests = async (req, res) => {
  try {
    const { status = 'pending' } = req.query;
    const filter = status === 'all' ? {} : { status };
    const requests = await HolidayRemovalRequest.find(filter)
      .populate('employee', 'name email') // ADAPT: fields on your User model
      .populate('holiday')
      .populate('reviewedBy', 'name')
      .sort({ createdAt: -1 });
    res.json(requests);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// PATCH /api/holiday-removal-requests/:id/approve   (admin only) -> undoes the holiday
exports.approveRequest = async (req, res) => {
  try {
    if (!isId(req.params.id)) return res.status(400).json({ message: 'Invalid request id' });

    // Atomically claim the request so two admins can't process it twice.
    const request = await HolidayRemovalRequest.findOneAndUpdate(
      { _id: req.params.id, status: 'pending' },
      {
        status: 'approved',
        reviewedBy: req.user._id,
        reviewedAt: new Date(),
        adminNote: (req.body.adminNote || '').trim(),
      },
      { new: true }
    );
    if (!request) return res.status(404).json({ message: 'Pending request not found' });

    const holiday = await Holiday.findOneAndUpdate(
      { _id: request.holiday, status: APPROVED_STATUS },
      { status: REMOVED_STATUS },
      { new: true }
    );

    if (!holiday) {
      // Holiday was already changed/removed - put the request back so nothing is lost.
      await HolidayRemovalRequest.updateOne(
        { _id: request._id },
        { status: 'pending', $unset: { reviewedBy: 1, reviewedAt: 1, adminNote: 1 } }
      );
      return res.status(409).json({ message: 'Holiday is no longer in approved state' });
    }

    // ADAPT: if approving a holiday deducted leave balance, give it back here, e.g.
    // await User.updateOne({ _id: holiday.employee }, { $inc: { leaveBalance: holiday.days } });

    res.json({ message: 'Holiday removed', request, holiday });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};

// PATCH /api/holiday-removal-requests/:id/reject   (admin only) -> holiday stays approved
exports.rejectRequest = async (req, res) => {
  try {
    if (!isId(req.params.id)) return res.status(400).json({ message: 'Invalid request id' });

    const request = await HolidayRemovalRequest.findOneAndUpdate(
      { _id: req.params.id, status: 'pending' },
      {
        status: 'rejected',
        reviewedBy: req.user._id,
        reviewedAt: new Date(),
        adminNote: (req.body.adminNote || '').trim(),
      },
      { new: true }
    );
    if (!request) return res.status(404).json({ message: 'Pending request not found' });

    res.json({ message: 'Request rejected', request });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
};
