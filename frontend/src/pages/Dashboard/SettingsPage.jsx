import { useState } from "react";
import { KeyRound, Loader2, ShieldCheck, Trash2, User } from "lucide-react";
import { motion } from "framer-motion";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PageHeader } from "@/components/PageHeader";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import { changePassword, getApiMessage, updateProfile } from "@/services/api";

function FormField({ label, id, type = "text", value, onChange, placeholder, required }) {
  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="block text-sm font-medium">
        {label}
      </label>
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className="saas-input"
      />
    </div>
  );
}

function StatusMessage({ message, isError }) {
  if (!message) return null;
  return (
    <motion.p
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      role="alert"
      className={`rounded-md px-3 py-2 text-sm ${
        isError
          ? "bg-destructive/10 text-destructive"
          : "bg-primary/10 text-primary"
      }`}
    >
      {message}
    </motion.p>
  );
}

function AvatarDisplay({ name }) {
  const initials = (name || "U")
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase())
    .join("");

  return (
    <div className="flex items-center gap-4 mb-6">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/20 text-primary text-xl font-bold select-none">
        {initials}
      </div>
      <div>
        <p className="font-semibold">{name}</p>
        <p className="text-xs text-muted-foreground">Account avatar (auto-generated)</p>
      </div>
    </div>
  );
}

export default function SettingsPage() {
  const { user, refreshUser, logout } = useAuth();
  const toast = useToast();

  // Profile form
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [profileMsg, setProfileMsg] = useState("");
  const [profileErr, setProfileErr] = useState("");
  const [loadingProfile, setLoadingProfile] = useState(false);

  // Password form
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordMsg, setPasswordMsg] = useState("");
  const [passwordErr, setPasswordErr] = useState("");
  const [loadingPassword, setLoadingPassword] = useState(false);

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setProfileErr("");
    setProfileMsg("");
    if (!fullName.trim()) {
      setProfileErr("Full name is required.");
      return;
    }
    setLoadingProfile(true);
    try {
      await updateProfile({ full_name: fullName.trim() });
      await refreshUser();
      setProfileMsg("Profile updated successfully.");
      toast.success("Profile updated.");
    } catch (err) {
      const msg = getApiMessage(err, "Failed to update profile.");
      setProfileErr(msg);
      toast.error(msg);
    } finally {
      setLoadingProfile(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setPasswordErr("");
    setPasswordMsg("");
    if (!currentPassword || !newPassword || !confirmPassword) {
      setPasswordErr("All password fields are required.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordErr("New passwords do not match.");
      return;
    }
    if (newPassword.length < 8) {
      setPasswordErr("New password must be at least 8 characters.");
      return;
    }
    setLoadingPassword(true);
    try {
      await changePassword({ current_password: currentPassword, new_password: newPassword });
      setPasswordMsg("Password changed successfully.");
      toast.success("Password changed.");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      const msg = getApiMessage(err, "Failed to change password.");
      setPasswordErr(msg);
      toast.error(msg);
    } finally {
      setLoadingPassword(false);
    }
  };

  const handleDeleteAccount = () => {
    const confirmed = window.confirm(
      "Are you sure you want to delete your account? This action cannot be undone."
    );
    if (confirmed) {
      toast.error("Account deletion requires admin assistance. Please contact support.");
    }
  };

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.07 } },
  };
  const item = {
    hidden: { opacity: 0, y: 12 },
    show: { opacity: 1, y: 0, transition: { duration: 0.3 } },
  };

  return (
    <motion.div
      className="space-y-6 max-w-2xl"
      variants={container}
      initial="hidden"
      animate="show"
    >
      <PageHeader
        title="Settings"
        description="Manage your account preferences and security settings."
      />

      {/* ── Profile ── */}
      <motion.div variants={item}>
        <Card className="saas-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-4 w-4 text-primary" />
              Profile
            </CardTitle>
            <CardDescription>Update your display name and account details.</CardDescription>
          </CardHeader>
          <CardContent>
            <AvatarDisplay name={user?.full_name} />
            <form onSubmit={handleProfileSubmit} className="space-y-4">
              <StatusMessage message={profileMsg} isError={false} />
              <StatusMessage message={profileErr} isError />
              <FormField
                label="Full name"
                id="settings-full-name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Your full name"
                required
              />
              <FormField
                label="Email address"
                id="settings-email"
                type="email"
                value={user?.email || ""}
                onChange={() => {}}
                placeholder="your@email.com"
              />
              <p className="text-xs text-muted-foreground">
                Email changes require contacting support.
              </p>
              <Button type="submit" disabled={loadingProfile} className="w-full sm:w-auto">
                {loadingProfile && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Save profile
              </Button>
            </form>
          </CardContent>
        </Card>
      </motion.div>

      {/* ── Security ── */}
      <motion.div variants={item}>
        <Card className="saas-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-primary" />
              Security
            </CardTitle>
            <CardDescription>
              Change your password to keep your account secure.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              <StatusMessage message={passwordMsg} isError={false} />
              <StatusMessage message={passwordErr} isError />
              <FormField
                label="Current password"
                id="settings-current-password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Enter current password"
                required
              />
              <FormField
                label="New password"
                id="settings-new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="At least 8 characters"
                required
              />
              <FormField
                label="Confirm new password"
                id="settings-confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Repeat new password"
                required
              />
              <Button
                type="submit"
                disabled={loadingPassword}
                className="w-full sm:w-auto"
              >
                {loadingPassword && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                <KeyRound className="mr-2 h-4 w-4" />
                Change password
              </Button>
            </form>
          </CardContent>
        </Card>
      </motion.div>

      {/* ── Session ── */}
      <motion.div variants={item}>
        <Card className="saas-card">
          <CardHeader>
            <CardTitle className="text-sm">Session</CardTitle>
            <CardDescription>Manage your active session.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between rounded-lg border border-border/60 bg-muted/20 px-4 py-3 text-sm">
              <div>
                <p className="font-medium">Current session</p>
                <p className="text-xs text-muted-foreground">
                  Logged in as {user?.email}
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={logout}
              >
                Sign out
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* ── Danger Zone ── */}
      <motion.div variants={item}>
        <Card className="saas-card border-destructive/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-destructive">
              <Trash2 className="h-4 w-4" />
              Danger zone
            </CardTitle>
            <CardDescription>
              Irreversible actions — proceed with caution.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3">
              <div>
                <p className="text-sm font-medium">Delete account</p>
                <p className="text-xs text-muted-foreground">
                  Permanently remove your account and all associated data.
                </p>
              </div>
              <Button
                variant="destructive"
                size="sm"
                onClick={handleDeleteAccount}
              >
                Delete
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
