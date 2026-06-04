import { useEffect, useState } from "react";
import { Trash2, Users } from "lucide-react";

import { EmptyState } from "@/components/EmptyState";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TableSkeleton } from "@/components/ui/skeleton";
import {
  deleteAdminUser,
  getAdminUsers,
  updateAdminUser,
} from "@/services/adminService";
import { getApiMessage } from "@/services/api";

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      setUsers(await getAdminUsers());
    } catch (err) {
      setError(getApiMessage(err, "Failed to load users"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleRole = async (id, role) => {
    try {
      await updateAdminUser(id, { role });
      await load();
    } catch (err) {
      setError(getApiMessage(err, "Update failed"));
    }
  };

  const handleActive = async (id, isActive) => {
    try {
      await updateAdminUser(id, { is_active: isActive });
      await load();
    } catch (err) {
      setError(getApiMessage(err, "Update failed"));
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Soft-delete this user?")) return;
    try {
      await deleteAdminUser(id);
      await load();
    } catch (err) {
      setError(getApiMessage(err, "Delete failed"));
    }
  };

  if (loading) {
    return <TableSkeleton rows={6} cols={6} />;
  }

  return (
    <Card className="saas-card">
      <CardHeader>
        <CardTitle>User management</CardTitle>
      </CardHeader>
      <CardContent>
        {error && (
          <p role="alert" className="mb-4 text-sm text-destructive rounded-md bg-destructive/10 px-3 py-2">
            {error}
          </p>
        )}
        {users.length === 0 ? (
          <EmptyState icon={Users} title="No users found" description="Registered users will appear here." />
        ) : (
        <div className="saas-table-wrap">
          <table className="saas-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td className="font-medium">{u.full_name}</td>
                  <td>{u.email}</td>
                  <td>
                    <select
                      value={u.role}
                      onChange={(e) => handleRole(u.id, e.target.value)}
                      className="rounded border border-input bg-background px-2 py-1 text-xs"
                    >
                      <option value="user">user</option>
                      <option value="admin">admin</option>
                    </select>
                  </td>
                  <td className="py-3 pr-4 capitalize">{u.status}</td>
                  <td className="py-3 pr-4 text-muted-foreground">
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}
                  </td>
                  <td className="py-3">
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleActive(u.id, u.status !== "active")}
                      >
                        {u.status === "active" ? "Suspend" : "Activate"}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-destructive"
                        onClick={() => handleDelete(u.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        )}
      </CardContent>
    </Card>
  );
}
