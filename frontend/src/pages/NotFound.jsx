import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/PageHeader";

export default function NotFoundPage() {
  return (
    <div className="container flex min-h-[50vh] flex-col items-center justify-center py-16">
      <PageHeader
        title="Page not found"
        description="The page you requested does not exist or was moved."
      />
      <Button asChild className="mt-8">
        <Link to="/">Go home</Link>
      </Button>
    </div>
  );
}
