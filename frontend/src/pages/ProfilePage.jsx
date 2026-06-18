import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  Avatar,
  IconButton,
  Divider,
  Alert,
  CircularProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import {
  Edit as EditIcon,
  PhotoCamera as CameraIcon,
  Save as SaveIcon,
  Lock as LockIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import toast from 'react-hot-toast';
import { useAuth } from '../hooks/useAuth';

function ProfilePage() {
  const { user, updateProfile, logout } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [profileError, setProfileError] = useState('');

  const [passwordForm, setPasswordForm] = useState({
    current: '',
    newPassword: '',
    confirm: '',
  });
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [changingPassword, setChangingPassword] = useState(false);

  const [deleteDialog, setDeleteDialog] = useState(false);

  const handleSaveProfile = async () => {
    setProfileError('');
    if (!name.trim()) {
      setProfileError('Name cannot be empty.');
      return;
    }
    setSaving(true);
    try {
      await updateProfile({ name });
      setEditing(false);
      toast.success('Profile updated!');
    } catch {
      setProfileError('Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async () => {
    setPasswordError('');
    setPasswordSuccess('');

    if (!passwordForm.current || !passwordForm.newPassword || !passwordForm.confirm) {
      setPasswordError('All fields are required.');
      return;
    }
    if (passwordForm.newPassword.length < 8) {
      setPasswordError('New password must be at least 8 characters.');
      return;
    }
    if (passwordForm.newPassword !== passwordForm.confirm) {
      setPasswordError('New passwords do not match.');
      return;
    }

    setChangingPassword(true);
    try {
      const { authAPI } = await import('../services/api');
      await authAPI.updateProfile({ password: passwordForm.newPassword });
      setPasswordSuccess('Password changed successfully!');
      setPasswordForm({ current: '', newPassword: '', confirm: '' });
      toast.success('Password updated!');
    } catch (error) {
      setPasswordError(error.response?.data?.detail || 'Failed to change password.');
    } finally {
      setChangingPassword(false);
    }
  };

  const handleDeleteAccount = async () => {
    try {
      toast.error('Account deletion is currently unavailable through the UI.');
    } catch {
      toast.error('Failed to delete account.');
    }
    setDeleteDialog(false);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        My Profile
      </Typography>

      <Grid container spacing={3}>
        {/* Profile Info */}
        <Grid item xs={12} md={8}>
          <Card sx={{ borderRadius: 3 }} elevation={2}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Profile Information
              </Typography>

              {profileError && (
                <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
                  {profileError}
                </Alert>
              )}

              <TextField
                fullWidth
                label="Name"
                value={name}
                onChange={(e) => { setName(e.target.value); setEditing(true); }}
                margin="normal"
                InputProps={{
                  endAdornment: editing && (
                    <IconButton onClick={handleSaveProfile} disabled={saving} color="primary">
                      {saving ? <CircularProgress size={20} /> : <SaveIcon />}
                    </IconButton>
                  ),
                }}
              />

              <TextField
                fullWidth
                label="Email"
                value={user?.email || ''}
                margin="normal"
                disabled
                helperText="Email cannot be changed"
              />

              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Member since: {user?.created_at
                    ? new Date(user.created_at).toLocaleDateString()
                    : 'N/A'}
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {/* Change Password */}
          <Card sx={{ borderRadius: 3, mt: 3 }} elevation={2}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                <LockIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Change Password
              </Typography>

              {passwordError && (
                <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
                  {passwordError}
                </Alert>
              )}
              {passwordSuccess && (
                <Alert severity="success" sx={{ mb: 2, borderRadius: 2 }}>
                  {passwordSuccess}
                </Alert>
              )}

              <TextField
                fullWidth
                type="password"
                label="Current Password"
                value={passwordForm.current}
                onChange={(e) => setPasswordForm({ ...passwordForm, current: e.target.value })}
                margin="normal"
              />
              <TextField
                fullWidth
                type="password"
                label="New Password"
                value={passwordForm.newPassword}
                onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                margin="normal"
              />
              <TextField
                fullWidth
                type="password"
                label="Confirm New Password"
                value={passwordForm.confirm}
                onChange={(e) => setPasswordForm({ ...passwordForm, confirm: e.target.value })}
                margin="normal"
              />

              <Button
                variant="contained"
                onClick={handleChangePassword}
                disabled={changingPassword}
                sx={{ mt: 2 }}
              >
                {changingPassword ? <CircularProgress size={20} sx={{ mr: 1 }} /> : null}
                Update Password
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3, textAlign: 'center', p: 4 }} elevation={2}>
            <Avatar
              src={user?.avatar_url}
              sx={{
                width: 100,
                height: 100,
                mx: 'auto',
                mb: 2,
                bgcolor: 'primary.main',
                fontSize: '2.5rem',
                fontWeight: 700,
              }}
            >
              {(user?.name || user?.email || 'U')[0].toUpperCase()}
            </Avatar>
            <Typography variant="h6" fontWeight={600}>
              {user?.name || 'User'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {user?.email}
            </Typography>

            <Divider sx={{ my: 2 }} />

            <Box sx={{ textAlign: 'left' }}>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                Account Statistics
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Chip label={`Translations: ${user?.total_translations || 0}`} size="small" />
                <Chip label={`Summaries: ${user?.total_summaries || 0}`} size="small" />
                <Chip label={`Processed: ${user?.total_operations || 0}`} size="small" />
              </Box>
            </Box>
          </Card>

          <Button
            fullWidth
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={() => setDeleteDialog(true)}
            sx={{ mt: 2, borderRadius: 3 }}
          >
            Delete Account
          </Button>
        </Grid>
      </Grid>

      <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
        <DialogTitle>Delete Account</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete your account? This action is permanent and cannot be undone.
            All your data will be permanently removed.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>Cancel</Button>
          <Button onClick={handleDeleteAccount} color="error" variant="contained">
            Delete Account
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default ProfilePage;
