"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    console.log("Login attempt:", { username, password: "***" });

    try {
      const result = await login(username, password);
      console.log("Login result:", result);

      if (result.success) {
        // Get user from result or localStorage
        let user = result.user;
        if (!user) {
          const userStr = localStorage.getItem("auth_user");
          if (userStr) {
            try {
              user = JSON.parse(userStr);
              console.log("User from localStorage:", user);
            } catch (e) {
              console.error("Error parsing user:", e);
            }
          }
        }

        console.log("Redirecting user:", user);

        // Small delay to ensure state is updated
        setTimeout(() => {
          // Redirect based on role
          if (user && user.role === "student") {
            console.log("Redirecting to /student");
            router.push("/student");
          } else if (user && user.role === "admin") {
            console.log("Redirecting to /");
            router.push("/");
          } else {
            console.log("Redirecting to / (default)");
            router.push("/");
          }
        }, 100);
      } else {
        console.error("Login failed:", result.error);
        setError(result.error || "Login failed");
        setLoading(false);
      }
    } catch (error: any) {
      console.error("Login error:", error);
      setError(error.message || "Login failed");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
        <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">
          Face Recognition System
        </h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your username"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your password"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-600">
          Contact admin for account access
        </p>
      </div>
    </div>
  );
}

