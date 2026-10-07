const mongoose = require('mongoose');

// One request = "employee asks admin to remove / undo an already-approved holiday".
const holidayRemovalRequestSchema = new mongoose.Schema(
  {
    holiday: { type: mongoose.Schema.Types.ObjectId, ref: 'Holiday', required: true },
    employee: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    reason: { type: String, required: true, trim: true, minlength: 5, maxlength: 500 },
    status: {
      type: String,
      enum: ['pending', 'approved', 'rejected'],
      default: 'pending',
      index: true,
    },
    reviewedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    reviewedAt: { type: Date },
    adminNote: { type: String, trim: true, maxlength: 500 },
  },
  { timestamps: true }
);

// Only one *pending* request per holiday at a time (DB-level guard against double submit).
holidayRemovalRequestSchema.index(
  { holiday: 1 },
  { unique: true, partialFilterExpression: { status: 'pending' } }
);

module.exports = mongoose.model('HolidayRemovalRequest', holidayRemovalRequestSchema);
