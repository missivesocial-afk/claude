// Use after your existing auth middleware (the one that sets req.user).
// ADAPT: if your app stores roles differently (e.g. req.user.isAdmin, 'hr', 'superadmin'), change this check.
const ADMIN_ROLES = ['admin'];

module.exports = function requireAdmin(req, res, next) {
  if (!req.user || !ADMIN_ROLES.includes(req.user.role)) {
    return res.status(403).json({ message: 'Only admin can perform this action' });
  }
  next();
};
